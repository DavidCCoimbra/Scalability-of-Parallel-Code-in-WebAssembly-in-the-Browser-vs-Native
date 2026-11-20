import json
import os
import tempfile
import threading
import unittest
from unittest import mock
import urllib.error
import urllib.request
from http.client import HTTPResponse
from pathlib import Path

from harness.server import ExistingResult, InvalidResult, ResultStore, make_server

META = {"userAgent": "test", "clockResolutionNs": 5000, "clockSmallestStepNs": 100}

ISOLATION_HEADERS = {
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
}


class ServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.www = root / "www"
        self.results = root / "results"
        self.www.mkdir()
        (self.www / "index.html").write_text("<!doctype html>")
        (self.www / "bench_bg.wasm").write_bytes(b"\0asm")
        (self.www / "worker.js").write_text("export {}")
        self.server = make_server(self.www, self.results, port=0)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def get(self, path: str) -> HTTPResponse:
        response: HTTPResponse = urllib.request.urlopen(self.base + path)
        return response

    def post(self, path: str, body: dict[str, object]) -> HTTPResponse:
        request = urllib.request.Request(
            self.base + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response: HTTPResponse = urllib.request.urlopen(request)
        return response

    def test_binds_to_localhost_only(self) -> None:
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_files_are_served_with_cross_origin_isolation_headers(self) -> None:
        response = self.get("/index.html")
        for header, value in ISOLATION_HEADERS.items():
            self.assertEqual(response.headers[header], value)
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_wasm_and_javascript_have_the_right_content_types(self) -> None:
        self.assertEqual(self.get("/bench_bg.wasm").headers["Content-Type"], "application/wasm")
        self.assertEqual(self.get("/worker.js").headers["Content-Type"], "text/javascript")

    def test_posted_results_are_written_to_disk(self) -> None:
        response = self.post("/results?run=run-001", {"csv": "a,b\n1,2\n", "meta": META})
        self.assertEqual(response.status, 201)
        self.assertEqual((self.results / "run-001.csv").read_text(), "a,b\n1,2\n")
        self.assertEqual(json.loads((self.results / "run-001.json").read_text()), META)

    def test_unsafe_run_id_is_rejected(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/results?run=../escape", {"csv": "", "meta": META})
        self.assertEqual(error.exception.code, 400)
        self.assertFalse(any(self.results.parent.glob("escape*")))

    def test_existing_run_is_not_overwritten(self) -> None:
        self.post("/results?run=once", {"csv": "first\n", "meta": META})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/results?run=once", {"csv": "second\n", "meta": META})
        self.assertEqual(error.exception.code, 409)
        self.assertEqual((self.results / "once.csv").read_text(), "first\n")

    def test_run_id_with_trailing_newline_is_rejected(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/results?run=abc%0A", {"csv": "", "meta": META})
        self.assertEqual(error.exception.code, 400)

    def test_meta_without_required_keys_is_rejected(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/results?run=nometa", {"csv": "x\n", "meta": {"userAgent": "test"}})
        self.assertEqual(error.exception.code, 400)
        self.assertFalse((self.results / "nometa.csv").exists())

    def test_malformed_body_is_rejected(self) -> None:
        request = urllib.request.Request(self.base + "/results?run=bad", data=b"not json", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 400)

    def test_unknown_clock_resolution_is_stored_as_null(self) -> None:
        meta = {**META, "clockResolutionNs": None, "clockSmallestStepNs": None}
        response = self.post("/results?run=nullclock", {"csv": "x\n", "meta": meta})
        self.assertEqual(response.status, 201)
        stored = json.loads((self.results / "nullclock.json").read_text())
        self.assertIsNone(stored["clockResolutionNs"])

    def test_posted_errors_are_written_to_disk(self) -> None:
        response = self.post("/errors?run=fail-1", {"error": "InconsistentChecksum", "meta": META})
        self.assertEqual(response.status, 201)
        stored = json.loads((self.results / "fail-1.error.json").read_text())
        self.assertEqual(stored, {"error": "InconsistentChecksum", **META})

    def test_errors_are_not_overwritten_and_ids_are_checked(self) -> None:
        self.post("/errors?run=fail-2", {"error": "first"})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/errors?run=fail-2", {"error": "second"})
        self.assertEqual(error.exception.code, 409)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/errors?run=../x", {"error": "boom"})
        self.assertEqual(error.exception.code, 400)

    def test_post_to_other_paths_is_not_found(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post("/elsewhere", {})
        self.assertEqual(error.exception.code, 404)


class ResultStoreTest(unittest.TestCase):
    def test_failed_metadata_write_leaves_no_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ResultStore(Path(tmp))
            with self.assertRaises(InvalidResult):
                store.save("broken", "x\n", {**META, "extra": object()})
            self.assertEqual(sorted(path.name for path in Path(tmp).iterdir()), [])

    def test_duplicate_post_keeps_the_stored_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ResultStore(Path(tmp))
            store.save("dup", "x\n", {**META, "first": True})
            (Path(tmp) / "dup.csv").unlink()
            with self.assertRaises(ExistingResult):
                store.save("dup", "y\n", {**META, "first": False})
            self.assertTrue(json.loads((Path(tmp) / "dup.json").read_text())["first"])

    def test_failed_csv_link_removes_the_metadata_it_linked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ResultStore(Path(tmp))
            real_link = os.link
            calls = []

            def link(source: str, target: Path) -> None:
                calls.append(target)
                if str(target).endswith(".csv"):
                    raise FileExistsError(target)
                real_link(source, target)

            with mock.patch("harness.server.os.link", link):
                with self.assertRaises(ExistingResult):
                    store.save("race", "x\n", META)
            self.assertEqual(len(calls), 2)
            self.assertEqual(sorted(path.name for path in Path(tmp).iterdir()), [])

    def test_failed_error_write_leaves_no_partial_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ResultStore(Path(tmp))
            with self.assertRaises(InvalidResult):
                store.save_error("broken", "boom", {"extra": object()})
            self.assertEqual(sorted(path.name for path in Path(tmp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()

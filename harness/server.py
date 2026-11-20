"""Local server for the browser runs: serves www/ cross-origin isolated
and stores POST /results.

Usage: python3 harness/server.py [--www bench/www] [--results data/raw] [--port 8000] [--verbose]

Standard library only, so it also runs as a plain script.
"""

import argparse
import json
import os
import re
import socket
import sys
import tempfile
import threading
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import BaseServer
from typing import TypedDict
from urllib.parse import parse_qs, urlsplit

# Loopback only: the results endpoint accepts writes from anyone who can reach it.
HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MAX_RUN_ID_LENGTH = 64
RUN_ID = re.compile(rf"[A-Za-z0-9_-]{{1,{MAX_RUN_ID_LENGTH}}}")
REQUIRED_META = ("userAgent", "clockResolutionNs", "clockSmallestStepNs")
MAX_BODY_BYTES = 64 * 1024 * 1024
RESULTS_PATH = "/results"
ERRORS_PATH = "/errors"
STAGING_PREFIX = ".staging-"
JSON_INDENT = 2
# SharedArrayBuffer, and so WASM threads, needs a cross-origin isolated page.
# https://developer.mozilla.org/en-US/docs/Web/API/Window/crossOriginIsolated
RESPONSE_HEADERS = {
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cache-Control": "no-store",
}


class ResultPost(TypedDict):
    csv: str
    meta: object


class ErrorPost(TypedDict):
    error: str
    meta: object


class InvalidResult(ValueError):
    pass


class ExistingResult(FileExistsError):
    pass


def check_run_id(run_id: str) -> None:
    if not RUN_ID.fullmatch(run_id):
        raise InvalidResult(f"invalid run id {run_id!r}")


def check_meta_object(meta: object) -> dict[str, object]:
    if not isinstance(meta, dict):
        raise InvalidResult("meta must be an object")
    return meta


def body_problem(required: str) -> InvalidResult:
    return InvalidResult(f"body must be a JSON object with a {required} string")


def required_text(body: dict[str, object], key: str) -> str:
    value = body.get(key)
    if not isinstance(value, str):
        raise body_problem(key)
    return value


def to_json_text(document: object) -> str:
    try:
        return json.dumps(document, indent=JSON_INDENT)
    except (TypeError, ValueError) as error:
        raise InvalidResult(f"metadata is not JSON: {error}") from error


class ResultStore:
    def __init__(self, directory: Path):
        self.directory = directory

    def save(self, run_id: str, csv: str, meta: object) -> Path:
        self.validate(run_id, meta)
        csv_path = self.directory / f"{run_id}.csv"
        metadata_path = self.directory / f"{run_id}.json"
        if csv_path.exists():
            raise ExistingResult(f"run {run_id} already stored")
        self.directory.mkdir(parents=True, exist_ok=True)
        metadata = to_json_text(meta)
        try:
            self.publish(metadata, metadata_path)
        except FileExistsError as error:
            raise ExistingResult(f"run {run_id} already stored") from error
        try:
            self.publish(csv, csv_path)
        except FileExistsError as error:
            metadata_path.unlink()
            raise ExistingResult(f"run {run_id} already stored") from error
        return csv_path

    def save_error(self, run_id: str, error: str, meta: object) -> Path:
        check_run_id(run_id)
        record = to_json_text({"error": error, **check_meta_object(meta)})
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{run_id}.error.json"
        try:
            self.publish(record, path)
        except FileExistsError as exc:
            raise ExistingResult(f"error for run {run_id} already stored") from exc
        return path

    @staticmethod
    def validate(run_id: str, meta: object) -> None:
        check_run_id(run_id)
        missing = [key for key in REQUIRED_META if key not in check_meta_object(meta)]
        if missing:
            raise InvalidResult(f"meta is missing {', '.join(missing)}")

    def publish(self, text: str, target: Path) -> None:
        # A hard link appears complete in one step and fails if the target exists,
        # so a result is never half written and never overwritten.
        staged = self.stage(text)
        try:
            os.link(staged, target)
        finally:
            os.unlink(staged)

    def stage(self, text: str) -> str:
        descriptor, path = tempfile.mkstemp(dir=self.directory, prefix=STAGING_PREFIX)
        with os.fdopen(descriptor, "w") as file:
            file.write(text)
        return path


class BenchHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "text/javascript",
    }

    def __init__(
        self,
        request: socket.socket | tuple[bytes, socket.socket],
        client_address: tuple[str, int],
        server: BaseServer,
        *,
        store: ResultStore,
        verbose: bool,
        directory: str | None = None,
    ):
        self.store = store
        self.verbose = verbose
        super().__init__(request, client_address, server, directory=directory)

    def end_headers(self) -> None:
        for header, value in RESPONSE_HEADERS.items():
            self.send_header(header, value)
        super().end_headers()

    def do_POST(self) -> None:
        url = urlsplit(self.path)
        if url.path not in (RESULTS_PATH, ERRORS_PATH):
            self.reply(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        try:
            run_id = parse_qs(url.query).get("run", [""])[0]
            saved = self.save_result(run_id) if url.path == RESULTS_PATH else self.save_error(run_id)
        except ExistingResult as error:
            self.reply(HTTPStatus.CONFLICT, {"error": str(error)})
        except (InvalidResult, KeyError, TypeError, ValueError) as error:
            self.reply(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        else:
            self.reply(HTTPStatus.CREATED, {"saved": saved.name})

    def save_result(self, run_id: str) -> Path:
        post = self.read_result_post()
        return self.store.save(run_id, post["csv"], post["meta"])

    def save_error(self, run_id: str) -> Path:
        post = self.read_error_post()
        return self.store.save_error(run_id, post["error"], post["meta"])

    def read_result_post(self) -> ResultPost:
        body = self.read_json(required="csv")
        return ResultPost(csv=required_text(body, "csv"), meta=body.get("meta"))

    def read_error_post(self) -> ErrorPost:
        body = self.read_json(required="error")
        return ErrorPost(error=required_text(body, "error"), meta=body.get("meta", {}))

    def read_json(self, required: str) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_BODY_BYTES:
            raise InvalidResult("missing or oversized body")
        body: object = json.loads(self.rfile.read(length))
        if not isinstance(body, dict):
            raise body_problem(required)
        return body

    def reply(self, status: HTTPStatus, payload: dict[str, str]) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        if self.verbose:
            sys.stderr.write(f"{self.address_string()} {format % args}\n")


def make_server(www: Path, results: Path, port: int = DEFAULT_PORT, verbose: bool = False) -> ThreadingHTTPServer:
    handler = partial(BenchHandler, directory=str(www), store=ResultStore(results), verbose=verbose)
    return ThreadingHTTPServer((HOST, port), handler)


class BackgroundServer:
    def __init__(self, www: Path):
        self.www = www
        self.port: int | None = None
        self.server: ThreadingHTTPServer | None = None

    def start(self, results: Path) -> int:
        self.server = make_server(self.www, results, port=0)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self.port

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--www", type=Path, default=Path("bench/www"))
    parser.add_argument("--results", type=Path, default=Path("data/raw"))
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    server = make_server(args.www, args.results, args.port, args.verbose)
    print(f"serving {args.www} on http://{HOST}:{server.server_address[1]}, results in {args.results}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

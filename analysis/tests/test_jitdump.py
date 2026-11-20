import struct
import tempfile
import unittest
from pathlib import Path

from analysis.extras.jitdump import CODE_LOAD, HEADER, MAGIC, RECORD, TruncatedDump, compiled_code, find


def code_load(name: str, address: int, code: bytes) -> bytes:
    body = CODE_LOAD.pack(1, 2, address, address, len(code), 0) + name.encode() + b"\0" + code
    return RECORD.pack(0, RECORD.size + len(body), 0) + body


def dump(*records: bytes) -> bytes:
    return HEADER.pack(MAGIC, 1, HEADER.size, 62, 0, 1, 0, 0) + b"".join(records)


class JitdumpTest(unittest.TestCase):
    def test_reads_every_code_load_record(self) -> None:
        data = dump(code_load("a-liftoff", 0x10, b"\x90"), struct.pack("<IIQ", 3, RECORD.size, 0), code_load("a-turbofan", 0x20, b"\xc3\xc3"))
        codes = list(compiled_code(data))
        self.assertEqual([(c.name, c.address, c.code) for c in codes], [("a-liftoff", 0x10, b"\x90"), ("a-turbofan", 0x20, b"\xc3\xc3")])

    def test_finds_the_first_function_with_the_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jit-1.dump"
            path.write_bytes(dump(code_load("f-32-liftoff", 1, b"\x90"), code_load("f-32-turbofan", 2, b"\xc3")))
            found = find([path], "-32-turbofan")
            assert found is not None
            self.assertEqual(found.code, b"\xc3")
            self.assertIsNone(find([path], "-33-turbofan"))

    def test_a_cut_last_record_is_skipped(self) -> None:
        whole = dump(code_load("f-1-liftoff", 1, b"\x90"), code_load("f-32-turbofan", 2, b"\xc3\xc3\xc3"))
        self.assertEqual([c.name for c in compiled_code(whole[:-2])], ["f-1-liftoff"])

    def test_a_record_whose_code_overruns_it_is_reported(self) -> None:
        record = bytearray(code_load("f-32-turbofan", 2, b"\xc3"))
        record[RECORD.size + 24 : RECORD.size + 32] = (99).to_bytes(8, "little")
        with self.assertRaises(TruncatedDump):
            list(compiled_code(dump(bytes(record))))

    def test_other_files_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            list(compiled_code(b"\0" * HEADER.size))


if __name__ == "__main__":
    unittest.main()

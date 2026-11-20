import unittest

from harness.native import CSV_HEADER
from harness.native.interface import SCHEMA_VERSION
from harness.native.row_schema import LEGACY_SCHEMA, schema_of, upgraded

LEGACY_COLUMNS = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum".split(",")


def legacy_row(phase: str, input_kind: str = "few", k: str = "4") -> dict[str, object]:
    values = ["chrome", "hist-local", input_kind, k, "64", "32", "24301", "8", phase, "0", "10", "0x01", "0x02"]
    return dict(zip(LEGACY_COLUMNS, values))


class RowSchemaTest(unittest.TestCase):
    def test_the_header_extends_the_legacy_columns(self) -> None:
        self.assertEqual(CSV_HEADER.split(",")[: len(LEGACY_COLUMNS)], LEGACY_COLUMNS)
        self.assertEqual(SCHEMA_VERSION, 2)

    def test_a_row_without_a_schema_column_is_schema_1(self) -> None:
        self.assertEqual(schema_of(legacy_row("measured")), LEGACY_SCHEMA)
        self.assertEqual(schema_of({**legacy_row("measured"), "schema": "2"}), 2)

    def test_a_legacy_row_gets_every_column_with_the_values_its_build_implied(self) -> None:
        row = upgraded(legacy_row("measured"), {"passes": 3, "grain": 16})
        self.assertEqual(list(row), CSV_HEADER.split(","))
        self.assertEqual(
            {key: row[key] for key in ("schema", "probe", "palette", "pitch", "passes", "grain", "mem_before_bytes")},
            {"schema": "1", "probe": "", "palette": "spread", "pitch": "64", "passes": "3", "grain": "16", "mem_before_bytes": ""},
        )

    def test_legacy_calibration_samples_were_broadcasts_and_runs_without_keys_used_the_defaults(self) -> None:
        row = upgraded(legacy_row("calibration-warm", input_kind="noise", k=""), {})
        self.assertEqual((row["probe"], row["palette"], row["passes"], row["grain"]), ("broadcast", "", "1", ""))

    def test_a_current_row_is_left_as_it_is(self) -> None:
        current = dict(zip(CSV_HEADER.split(","), ["x"] * len(CSV_HEADER.split(","))))
        current["schema"] = "2"
        self.assertEqual(upgraded(current, {"passes": 9}), current)


if __name__ == "__main__":
    unittest.main()

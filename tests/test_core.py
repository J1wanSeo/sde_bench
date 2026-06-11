import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sde_bench import benchmark, evaluate, load_config, load_records


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class SdeBenchCoreTests(unittest.TestCase):
    def test_load_records_infers_numeric_and_categorical_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "records.csv"
            write_csv(
                path,
                [
                    {"case_id": "A", "age": "42", "dept": "OS"},
                    {"case_id": "B", "age": "53.5", "dept": "GI"},
                ],
            )

            records = load_records(path)

        self.assertEqual(records[0]["age"], 42)
        self.assertEqual(records[1]["age"], 53.5)
        self.assertEqual(records[0]["dept"], "OS")

    def test_evaluate_returns_syntheval_axes_plus_groundedness_and_domain_consistency(self) -> None:
        real = [
            {"case_id": "A", "age": 40, "dept": "OS", "sex": "F", "diagnosis": "ACL tear"},
            {"case_id": "B", "age": 55, "dept": "GI", "sex": "M", "diagnosis": "gastric ulcer"},
            {"case_id": "C", "age": 70, "dept": "NS", "sex": "F", "diagnosis": "spinal stenosis"},
        ]
        synthetic = [
            {
                "case_id": "S1",
                "source_id": "A",
                "age": 41,
                "dept": "OS",
                "sex": "F",
                "diagnosis": "ACL tear",
                "claim": "ACL tear requiring arthroscopy",
                "evidence": "ACL tear requiring arthroscopy",
                "expected_dept": "OS",
                "predicted_dept": "OS",
            },
            {
                "case_id": "S2",
                "source_id": "B",
                "age": 56,
                "dept": "GI",
                "sex": "M",
                "diagnosis": "gastric ulcer",
                "claim": "gastric ulcer follow-up",
                "evidence": "gastric ulcer follow-up",
                "expected_dept": "GI",
                "predicted_dept": "GI",
            },
            {
                "case_id": "S3",
                "source_id": "C",
                "age": 71,
                "dept": "NS",
                "sex": "F",
                "diagnosis": "spinal stenosis",
                "claim": "spinal stenosis with leg pain",
                "evidence": "spinal stenosis with leg pain",
                "expected_dept": "NS",
                "predicted_dept": "OS",
            },
        ]
        source = {
            "A": {"dept": "OS", "diagnosis": "ACL tear"},
            "B": {"dept": "GI", "diagnosis": "gastric ulcer"},
            "C": {"dept": "NS", "diagnosis": "spinal stenosis"},
        }

        report = evaluate(real=real, synthetic=synthetic, source=source, target="dept")

        self.assertEqual(
            list(report["axes"]),
            [
                "fidelity",
                "utility",
                "privacy",
                "fairness",
                "diversity",
                "groundedness",
                "domain_consistency",
            ],
        )
        self.assertGreater(report["axes"]["fidelity"]["score"], 0.8)
        self.assertAlmostEqual(report["axes"]["groundedness"]["metrics"]["source_attribution_rate"], 1.0)
        self.assertAlmostEqual(report["axes"]["domain_consistency"]["metrics"]["dept_consistency"], 1.0)
        self.assertAlmostEqual(report["axes"]["utility"]["metrics"]["label_accuracy"], 2 / 3)
        self.assertLess(report["axes"]["utility"]["score"], 1.0)

    def test_benchmark_ranks_multiple_synthetic_datasets(self) -> None:
        real = [
            {"case_id": "A", "age": 40, "dept": "OS"},
            {"case_id": "B", "age": 60, "dept": "GI"},
        ]
        close = [{"case_id": "C1", "age": 41, "dept": "OS"}, {"case_id": "C2", "age": 59, "dept": "GI"}]
        far = [{"case_id": "F1", "age": 10, "dept": "PY"}, {"case_id": "F2", "age": 11, "dept": "PY"}]

        ranked = benchmark(real=real, synthetic_sets={"close": close, "far": far})

        self.assertEqual(ranked["ranking"][0]["name"], "close")
        self.assertGreater(ranked["ranking"][0]["overall_score"], ranked["ranking"][1]["overall_score"])

    def test_custom_axis_config_filters_report_axes(self) -> None:
        config = load_config({"axes": ["privacy", "groundedness"]})

        report = evaluate(
            real=[{"case_id": "A", "age": 40, "dept": "OS"}],
            synthetic=[{"case_id": "S1", "source_id": "A", "age": 41, "dept": "OS"}],
            config=config,
        )

        self.assertEqual(list(report["axes"]), ["privacy", "groundedness"])

    def test_bundled_privacy_preset_loads_by_name(self) -> None:
        config = load_config("privacy_eval")

        self.assertEqual(config["axes"], ["privacy", "groundedness"])


class SdeBenchCliTests(unittest.TestCase):
    def test_cli_writes_json_and_markdown_reports(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_path = root / "real.csv"
            synth_path = root / "synthetic.csv"
            out_json = root / "report.json"
            out_md = root / "report.md"
            write_csv(real_path, [{"case_id": "A", "age": "40", "dept": "OS"}])
            write_csv(
                synth_path,
                [{"case_id": "S1", "source_id": "A", "age": "41", "dept": "OS", "expected_dept": "OS", "predicted_dept": "OS"}],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "evaluate",
                    "--real",
                    str(real_path),
                    "--synthetic",
                    str(synth_path),
                    "--target",
                    "dept",
                    "--json-out",
                    str(out_json),
                    "--md-out",
                    str(out_md),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("groundedness", report["axes"])
            self.assertIn("SDE-Bench Report", out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

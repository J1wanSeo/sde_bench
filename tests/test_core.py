import csv
import json
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sde_bench import benchmark, evaluate, load_config, load_records
from sde_bench.core import _ks_distance
from sde_bench.adapters.amlsim import export_amlsim_records
from sde_bench.adapters.health_gym import export_health_gym_art_records
from sde_bench.adapters.kmuc import export_kmuc_records
from sde_bench.adapters.medsynth import export_medsynth_records
from sde_bench.adapters.synthea import export_synthea_records
from sde_bench.adapters.synsum import export_synsum_records
from sde_bench.domain_datasets import build_domain_survey, markdown_domain_survey
from sde_bench.original_benchmarks import build_cross_benchmark_report, markdown_cross_benchmark


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


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

    def test_load_records_accepts_json_and_jsonl_medical_datasets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "records.json"
            jsonl_path = root / "records.jsonl"
            rows = [{"case_id": "A", "age": 42, "dept": "OS"}]
            json_path.write_text(json.dumps(rows), encoding="utf-8")
            write_jsonl(jsonl_path, rows)

            self.assertEqual(load_records(json_path), rows)
            self.assertEqual(load_records(jsonl_path), rows)

    def test_load_records_sniffs_semicolon_csv(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "records.csv"
            path.write_text(";policy;common_cold;days_at_home\n0;yes;1;2\n", encoding="utf-8")

            records = load_records(path)

        self.assertEqual(records[0]["policy"], "yes")
        self.assertEqual(records[0]["common_cold"], 1)
        self.assertEqual(records[0]["days_at_home"], 2)
        self.assertNotIn("", records[0])

    def test_evaluate_returns_medical_benchmark_axes(self) -> None:
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
                "medical_fidelity",
                "clinical_task_utility",
                "privacy",
                "equity",
                "medical_diversity",
                "clinical_groundedness",
                "clinical_validity",
                "medical_interoperability",
            ],
        )
        self.assertGreater(report["axes"]["medical_fidelity"]["score"], 0.8)
        self.assertAlmostEqual(report["axes"]["clinical_groundedness"]["metrics"]["source_attribution_rate"], 1.0)
        self.assertAlmostEqual(report["axes"]["clinical_validity"]["metrics"]["dept_consistency"], 1.0)
        self.assertAlmostEqual(report["axes"]["clinical_task_utility"]["metrics"]["label_accuracy"], 2 / 3)
        self.assertLess(report["axes"]["clinical_task_utility"]["score"], 1.0)

    def test_clinical_validity_includes_medical_validity_metrics(self) -> None:
        report = evaluate(
            real=[{"case_id": "A", "age": 40, "dept": "OS", "diagnosis": "ACL tear"}],
            synthetic=[
                {
                    "case_id": "S1",
                    "age": 40,
                    "dept": "OS",
                    "diagnosis": "ACL tear",
                    "icd10_codes": "S83,I10,M25562",
                    "procedures": "ACL reconstruction",
                    "acuity": "elective",
                    "laterality": "left",
                },
                {
                    "case_id": "S2",
                    "age": 130,
                    "dept": "OS",
                    "diagnosis": "",
                    "icd10_codes": "BADCODE",
                    "procedures": "",
                    "acuity": "unknown",
                    "laterality": "up",
                },
            ],
            target="dept",
        )

        metrics = report["axes"]["clinical_validity"]["metrics"]
        self.assertEqual(metrics["icd10_format_validity"], 0.5)
        self.assertEqual(metrics["procedure_completeness"], 0.5)
        self.assertEqual(metrics["acuity_validity"], 0.5)
        self.assertEqual(metrics["laterality_validity"], 0.5)
        self.assertEqual(metrics["age_validity"], 0.5)

    def test_interoperability_axis_scores_omop_readiness(self) -> None:
        report = evaluate(
            real=[
                {
                    "case_id": "P1",
                    "age": 41,
                    "diagnosis": "Hypertension",
                    "omop_domains": "person,visit_occurrence,condition_occurrence",
                    "standard_vocabularies": "SNOMED-CT",
                    "encounter_id": "E1",
                    "condition_start": "2024-01-01",
                }
            ],
            synthetic=[
                {
                    "case_id": "P2",
                    "age": 43,
                    "diagnosis": "Diabetes",
                    "omop_domains": "person,visit_occurrence,condition_occurrence,procedure_occurrence",
                    "standard_vocabularies": "SNOMED-CT,LOINC",
                    "encounter_id": "E2",
                    "condition_start": "2024-02-01",
                    "procedure_date": "2024-02-02",
                }
            ],
        )

        metrics = report["axes"]["medical_interoperability"]["metrics"]
        self.assertAlmostEqual(metrics["omop_domain_coverage"], 4 / 6)
        self.assertAlmostEqual(metrics["standard_vocabulary_rate"], 1.0)
        self.assertAlmostEqual(metrics["temporal_traceability"], 1.0)
        self.assertAlmostEqual(metrics["relational_integrity"], 1.0)
        self.assertAlmostEqual(report["axes"]["medical_interoperability"]["score"], (4 / 6 + 1 + 1 + 1) / 4)

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
        config = load_config({"axes": ["privacy", "clinical_groundedness"]})

        report = evaluate(
            real=[{"case_id": "A", "age": 40, "dept": "OS"}],
            synthetic=[{"case_id": "S1", "source_id": "A", "age": 41, "dept": "OS"}],
            config=config,
        )

        self.assertEqual(list(report["axes"]), ["privacy", "clinical_groundedness"])

    def test_bundled_privacy_preset_loads_by_name(self) -> None:
        config = load_config("privacy_eval")

        self.assertEqual(config["axes"], ["privacy", "clinical_groundedness"])

    def test_bundled_core_preset_excludes_medical_specific_axes(self) -> None:
        config = load_config("core_eval")

        self.assertEqual(config["axes"], ["medical_fidelity", "clinical_task_utility", "privacy", "equity", "medical_diversity"])

    def test_equity_without_sensitive_columns_is_not_scored_as_fair(self) -> None:
        report = evaluate(
            real=[{"case_id": "A", "age": 40, "dept": "OS"}],
            synthetic=[{"case_id": "S1", "age": 41, "dept": "OS"}],
            sensitive_columns=[],
        )

        self.assertIsNone(report["axes"]["equity"]["score"])
        self.assertEqual(report["axes"]["equity"]["metrics"]["skipped"], "no_sensitive_columns")

    def test_privacy_distance_sampling_caps_quadratic_comparisons(self) -> None:
        real = [{"case_id": f"R{i}", "age": i, "dept": "A" if i % 2 else "B"} for i in range(20)]
        synthetic = [{"case_id": f"S{i}", "age": i + 1, "dept": "A" if i % 2 else "B"} for i in range(30)]

        report = evaluate(
            real=real,
            synthetic=synthetic,
            config={"axes": ["privacy"], "privacy_distance_sample_size": 5},
        )

        metrics = report["axes"]["privacy"]["metrics"]
        self.assertEqual(metrics["records_compared"], 30)
        self.assertEqual(metrics["distance_synthetic_records"], 5)
        self.assertEqual(metrics["distance_reference_records"], 5)
        self.assertTrue(metrics["distance_sampled"])

    def test_ks_distance_handles_large_unique_numeric_columns_quickly(self) -> None:
        left = [float(i) for i in range(5000)]
        right = [float(i + 2500) for i in range(5000)]

        start = time.perf_counter()
        distance = _ks_distance(left, right)
        elapsed = time.perf_counter() - start

        self.assertAlmostEqual(distance, 0.5)
        self.assertLess(elapsed, 0.25)

    def test_kmuc_adapter_exports_reference_source_and_lay_variant_records(self) -> None:
        enriched = [
            {
                "case_id": "KMUC-OS-001",
                "source": "data/patient_cases/001.md",
                "raw_chart": "가상환자A01 (M/72)\n",
                "extraction": {
                    "current_diagnosis": "Fx femoral neck",
                    "planned_procedure": "ORIF",
                    "icd10_candidates": ["S72"],
                    "procedure_candidates": ["ORIF"],
                    "acuity": "urgent",
                    "laterality": "left",
                    "dept_hint": ["OS"],
                },
                "labels": {"expected_department": "OS"},
            }
        ]
        lay = [
            {
                "case_id": "KMUC-OS-001",
                "variant_id": 0,
                "tone": "plain_self",
                "lay_text": "왼쪽 고관절 골절로 수술 상담을 받고 싶어요.",
                "original_emr": "가상환자A01 (M/72)\n",
                "expected_dept": "OS",
            }
        ]

        exported = export_kmuc_records(enriched, lay_variants=lay)

        self.assertEqual(exported["reference"][0]["case_id"], "KMUC-OS-001")
        self.assertEqual(exported["source"][0]["source_id"], "KMUC-OS-001")
        self.assertEqual(exported["synthetic"][0]["source_id"], "KMUC-OS-001")
        self.assertEqual(exported["synthetic"][0]["claim"], "왼쪽 고관절 골절로 수술 상담을 받고 싶어요.")
        self.assertEqual(exported["synthetic"][0]["evidence"], "가상환자A01 (M/72)\n")

    def test_synsum_adapter_exports_internal_split_records(self) -> None:
        rows = [
            {
                "pneu": "1",
                "cold": "0",
                "dysp": "1",
                "cough": "1",
                "pain": "0",
                "fever": "1",
                "nasal": "0",
                "asthma": "0",
                "smoking": "1",
                "COPD": "0",
                "hay_fever": "0",
                "antibiotics": "1",
                "season": "winter",
                "days_at_home": "5",
                "text": "Patient has pneumonia with cough and fever.",
                "advanced_text": "PNA, cough, fever.",
            },
            {
                "pneu": "0",
                "cold": "1",
                "dysp": "0",
                "cough": "1",
                "pain": "0",
                "fever": "0",
                "nasal": "1",
                "asthma": "0",
                "smoking": "0",
                "COPD": "0",
                "hay_fever": "1",
                "antibiotics": "0",
                "season": "spring",
                "days_at_home": "2",
                "text": "Patient has common cold and nasal symptoms.",
                "advanced_text": "Cold, nasal symptoms.",
            },
        ]

        exported = export_synsum_records(rows, split_fraction=0.5)

        self.assertEqual(exported["reference"][0]["diagnosis_group"], "pneumonia")
        self.assertEqual(exported["synthetic"][0]["diagnosis_group"], "common_cold")
        self.assertEqual(exported["synthetic"][0]["claim"], "Cold, nasal symptoms.")
        self.assertEqual(exported["synthetic"][0]["evidence"], "Patient has common cold and nasal symptoms.")
        self.assertEqual(exported["synthetic"][0]["source_id"], exported["source"][0]["source_id"])

    def test_medsynth_adapter_exports_dialogue_note_records(self) -> None:
        rows = [
            {
                " Note": "The patient is a 52-year-old with left knee pain.",
                "Dialogue": "[patient] I have left knee pain.",
                "ICD10": "M25562",
                "ICD10_desc": "PAIN IN LEFT KNEE",
            },
            {
                " Note": "The patient is a 40-year-old with cough.",
                "Dialogue": "[patient] I have cough.",
                "ICD10": "R05",
                "ICD10_desc": "COUGH",
            },
        ]

        exported = export_medsynth_records(rows, split_fraction=0.5)

        self.assertEqual(exported["reference"][0]["icd10_codes"], "M25562")
        self.assertEqual(exported["synthetic"][0]["diagnosis_group"], "R05")
        self.assertEqual(exported["synthetic"][0]["age"], 40)
        self.assertEqual(exported["synthetic"][0]["evidence"], "[patient] I have cough.")
        self.assertEqual(exported["synthetic"][0]["source_id"], exported["source"][0]["source_id"])

    def test_synthea_adapter_exports_patient_level_csv_records(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_csv(
                root / "patients.csv",
                [
                    {
                        "Id": "P1",
                        "BIRTHDATE": "1980-01-01",
                        "GENDER": "F",
                        "RACE": "white",
                        "ETHNICITY": "nonhispanic",
                    },
                    {
                        "Id": "P2",
                        "BIRTHDATE": "1975-06-01",
                        "GENDER": "M",
                        "RACE": "asian",
                        "ETHNICITY": "hispanic",
                    },
                ],
            )
            write_csv(
                root / "encounters.csv",
                [
                    {"Id": "E1", "START": "2020-01-01", "PATIENT": "P1", "CODE": "185345009", "DESCRIPTION": "Encounter"},
                    {"Id": "E2", "START": "2021-01-01", "PATIENT": "P2", "CODE": "185345009", "DESCRIPTION": "Encounter"},
                ],
            )
            write_csv(
                root / "conditions.csv",
                [
                    {
                        "START": "2020-01-01",
                        "PATIENT": "P1",
                        "ENCOUNTER": "E1",
                        "CODE": "59621000",
                        "DESCRIPTION": "Hypertension",
                    },
                    {
                        "START": "2021-01-01",
                        "PATIENT": "P2",
                        "ENCOUNTER": "E2",
                        "CODE": "44054006",
                        "DESCRIPTION": "Diabetes mellitus",
                    },
                ],
            )
            write_csv(
                root / "procedures.csv",
                [
                    {
                        "DATE": "2021-01-02",
                        "PATIENT": "P2",
                        "ENCOUNTER": "E2",
                        "CODE": "73761001",
                        "DESCRIPTION": "Colonoscopy",
                    }
                ],
            )

            exported = export_synthea_records(root, split_fraction=0.5)

        self.assertEqual(exported["reference"][0]["case_id"], "SYNTHEA-P1")
        self.assertEqual(exported["synthetic"][0]["case_id"], "SYNTHEA-P2")
        self.assertEqual(exported["synthetic"][0]["source_id"], exported["source"][0]["source_id"])
        self.assertEqual(exported["synthetic"][0]["diagnosis"], "Diabetes mellitus")
        self.assertIn("condition_occurrence", exported["synthetic"][0]["omop_domains"])
        self.assertIn("procedure_occurrence", exported["synthetic"][0]["omop_domains"])
        self.assertEqual(exported["synthetic"][0]["standard_vocabularies"], "SNOMED-CT")
        self.assertEqual(exported["synthetic"][0]["encounter_id"], "E2")

    def test_health_gym_adapter_exports_longitudinal_art_records_by_patient(self) -> None:
        rows = [
            {"VL": "29.9", "CD4": "793.4", "Rel CD4": "30.8", "Gender": "1", "Ethnic": "3", "Drug (M)": "1", "PatientID": "0", "Timestep": "0"},
            {"VL": "29.2", "CD4": "467.4", "Rel CD4": "30.3", "Gender": "1", "Ethnic": "3", "Drug (M)": "0", "PatientID": "0", "Timestep": "1"},
            {"VL": "31.1", "CD4": "500.0", "Rel CD4": "28.1", "Gender": "0", "Ethnic": "2", "Drug (M)": "1", "PatientID": "1", "Timestep": "0"},
            {"VL": "30.5", "CD4": "510.0", "Rel CD4": "28.5", "Gender": "0", "Ethnic": "2", "Drug (M)": "0", "PatientID": "1", "Timestep": "1"},
        ]

        exported = export_health_gym_art_records(rows, split_fraction=0.5)

        self.assertEqual([row["patient_id"] for row in exported["reference"]], ["0", "0"])
        self.assertEqual([row["patient_id"] for row in exported["synthetic"]], ["1", "1"])
        self.assertEqual(exported["synthetic"][0]["case_id"], "HEALTHGYM-ART-1-T0")
        self.assertEqual(exported["synthetic"][0]["source_id"], exported["source"][0]["source_id"])
        self.assertEqual(exported["synthetic"][0]["diagnosis"], "HIV antiretroviral therapy")
        self.assertEqual(exported["synthetic"][0]["condition_start"], "2023-01-01")
        self.assertIn("measurement", exported["synthetic"][0]["omop_domains"])
        self.assertEqual(exported["synthetic"][0]["standard_vocabularies"], "LOINC|RxNorm|SNOMED-CT")

    def test_amlsim_adapter_exports_transaction_records(self) -> None:
        rows = [
            {
                "TXN_ID": "1",
                "ACCOUNT_ID": "1000000001",
                "COUNTER_PARTY_ACCOUNT_NUM": "9000000001",
                "TXN_SOURCE_TYPE_CODE": "CHECK",
                "tx_count": "1",
                "TXN_AMOUNT_ORIG": "120.50",
                "start": "1",
                "end": "1",
            },
            {
                "TXN_ID": "2",
                "ACCOUNT_ID": "1000000002",
                "COUNTER_PARTY_ACCOUNT_NUM": "9000000002",
                "TXN_SOURCE_TYPE_CODE": "WIRE",
                "tx_count": "3",
                "TXN_AMOUNT_ORIG": "5000",
                "start": "2",
                "end": "2",
            },
        ]

        exported = export_amlsim_records(rows, split_fraction=0.5)

        self.assertEqual(exported["reference"][0]["case_id"], "AMLSIM-TXN-1")
        self.assertEqual(exported["synthetic"][0]["case_id"], "AMLSIM-TXN-2")
        self.assertEqual(exported["synthetic"][0]["source_id"], exported["source"][0]["source_id"])
        self.assertEqual(exported["synthetic"][0]["transaction_type"], "WIRE")
        self.assertEqual(exported["synthetic"][0]["amount"], 5000)
        self.assertEqual(exported["synthetic"][0]["expected_transaction_type"], "WIRE")


class SdeBenchCliTests(unittest.TestCase):
    def test_domain_survey_prioritizes_medical_and_cross_domain_candidates(self) -> None:
        survey = build_domain_survey()
        rendered = markdown_domain_survey(survey)

        self.assertEqual(survey["schema_version"], "0.1.0")
        self.assertGreaterEqual(survey["domain_counts"]["medical"], 5)
        self.assertIn("finance", survey["domain_counts"])
        self.assertIn("science", survey["domain_counts"])
        self.assertEqual(survey["next_batch"][0]["dataset_id"], "de_synpuf_claims")
        self.assertIn("Health Gym", rendered)
        self.assertIn("FiFAR", rendered)
        self.assertIn("SynTReN", rendered)

    def test_cli_writes_domain_dataset_survey(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_json = root / "survey.json"
            out_md = root / "survey.md"

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "dataset-survey",
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
            survey = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("candidate_datasets", survey)
            self.assertIn("Domain Coverage", out_md.read_text(encoding="utf-8"))

    def test_original_benchmark_matrix_records_staged_applicability(self) -> None:
        reports = {
            "KMUC": {
                "overall_score": 0.8,
                "axes": {
                    "medical_fidelity": {"score": 1.0},
                    "medical_interoperability": {"score": None},
                },
            },
            "Synthea": {
                "overall_score": 0.82,
                "axes": {
                    "medical_fidelity": {"score": 0.3},
                    "medical_interoperability": {"score": 1.0},
                },
            },
        }

        report = build_cross_benchmark_report(reports)
        rendered = markdown_cross_benchmark(report)

        self.assertEqual(report["stage_a"]["kmuc_matching"]["status"], "computed")
        self.assertEqual(report["stage_b"]["simsum_symptom_ie"]["SimSUM"]["status"], "paper_reported")
        self.assertEqual(report["stage_b"]["synthea_structured_ehr"]["Synthea"]["value"], "`medical_interoperability=1.0000`")
        self.assertIn("Stage A", rendered)
        self.assertIn("medical_interoperability=1.0000", rendered)

    def test_original_benchmark_matrix_exposes_formula_and_combined_stage(self) -> None:
        reports = {
            "KMUC": {
                "overall_score": 0.8,
                "axes": {
                    "medical_interoperability": {"score": None},
                },
            },
            "Synthea": {
                "overall_score": 0.82,
                "axes": {
                    "medical_interoperability": {"score": 1.0},
                },
            },
            "HealthGymART": {
                "overall_score": 0.93,
                "axes": {
                    "medical_interoperability": {"score": 0.9583333333333334},
                },
            },
        }

        report = build_cross_benchmark_report(reports)
        rendered = markdown_cross_benchmark(report)

        synthea_family = report["benchmark_families"]["synthea_structured_ehr"]
        self.assertIn("metric_formula", synthea_family)
        self.assertIn("applicability_rule", synthea_family)
        self.assertEqual(report["stage_ab"]["synthea_structured_ehr"]["KMUC"]["status"], "not_applicable")
        self.assertEqual(report["stage_ab"]["synthea_structured_ehr"]["Synthea"]["value"], "`medical_interoperability=1.0000`")
        self.assertEqual(report["stage_ab"]["synthea_structured_ehr"]["HealthGymART"]["value"], "`medical_interoperability=0.9583`")
        self.assertIn("Stage A/B Combined", rendered)
        self.assertIn("mean(domain_coverage", rendered)
        self.assertIn("HealthGymART", rendered)

    def test_cli_writes_cross_benchmark_matrix(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            kmuc_report = root / "kmuc.json"
            synthea_report = root / "synthea.json"
            out_json = root / "cross.json"
            out_md = root / "cross.md"
            kmuc_report.write_text(
                json.dumps({"overall_score": 0.8, "axes": {"medical_fidelity": {"score": 1.0}}}),
                encoding="utf-8",
            )
            synthea_report.write_text(
                json.dumps({"overall_score": 0.82, "axes": {"medical_interoperability": {"score": 1.0}}}),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "cross-benchmark",
                    "--sde-report",
                    f"KMUC={kmuc_report}",
                    "--sde-report",
                    f"Synthea={synthea_report}",
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
            matrix = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("benchmark_families", matrix)
            self.assertIn("SDE-Bench Cross-Dataset Results", out_md.read_text(encoding="utf-8"))

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
            self.assertIn("clinical_groundedness", report["axes"])
            self.assertIn("SDE-Bench Report", out_md.read_text(encoding="utf-8"))

    def test_cli_exports_kmuc_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "kmuc"
            parsed = repo_root / "layer3_datasets/patient_dataset/parsed"
            enriched_path = parsed / "patient_cases.v2.enriched.jsonl"
            lay_path = parsed / "patient_cases.v2.lay.jsonl"
            predictions_path = root / "predictions.json"
            out_dir = root / "out"
            write_jsonl(
                enriched_path,
                [
                    {
                        "case_id": "KMUC-OS-001",
                        "raw_chart": "가상환자A01 (F/45)\n",
                        "extraction": {
                            "current_diagnosis": "ACL tear",
                            "procedure_candidates": ["ACL reconstruction"],
                            "icd10_candidates": ["S83.5"],
                            "acuity": "elective",
                            "laterality": "right",
                        },
                        "labels": {"expected_department": "OS"},
                    }
                ],
            )
            write_jsonl(
                lay_path,
                [
                    {
                        "case_id": "KMUC-OS-001",
                        "variant_id": 0,
                        "tone": "plain_self",
                        "lay_text": "무릎 인대 파열로 진료를 받고 싶어요.",
                        "original_emr": "가상환자A01 (F/45)\n",
                        "expected_dept": "OS",
                    }
                ],
            )
            predictions_path.write_text(
                json.dumps({"per_case": [{"case_id": "KMUC-OS-001", "variant_id": 0, "top_depts": ["OS"]}]}),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "kmuc-export",
                    "--repo-root",
                    str(repo_root),
                    "--predictions",
                    str(predictions_path),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic_lay.jsonl")
            self.assertEqual(exported[0]["source_id"], "KMUC-OS-001")
            self.assertEqual(exported[0]["predicted_dept"], "OS")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())

    def test_cli_exports_synsum_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            synsum_path = root / "SynSUM.csv"
            out_dir = root / "out"
            write_csv(
                synsum_path,
                [
                    {
                        "pneu": "1",
                        "cold": "0",
                        "dysp": "1",
                        "cough": "1",
                        "pain": "0",
                        "fever": "1",
                        "nasal": "0",
                        "asthma": "0",
                        "smoking": "1",
                        "COPD": "0",
                        "hay_fever": "0",
                        "antibiotics": "1",
                        "season": "winter",
                        "days_at_home": "5",
                        "text": "Patient has pneumonia with cough and fever.",
                        "advanced_text": "PNA, cough, fever.",
                    },
                    {
                        "pneu": "0",
                        "cold": "1",
                        "dysp": "0",
                        "cough": "1",
                        "pain": "0",
                        "fever": "0",
                        "nasal": "1",
                        "asthma": "0",
                        "smoking": "0",
                        "COPD": "0",
                        "hay_fever": "1",
                        "antibiotics": "0",
                        "season": "spring",
                        "days_at_home": "2",
                        "text": "Patient has common cold and nasal symptoms.",
                        "advanced_text": "Cold, nasal symptoms.",
                    },
                ],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "synsum-export",
                    "--input",
                    str(synsum_path),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic.jsonl")
            self.assertEqual(exported[0]["diagnosis_group"], "common_cold")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())

    def test_cli_exports_medsynth_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            medsynth_path = root / "MedSynth.csv"
            out_dir = root / "out"
            write_csv(
                medsynth_path,
                [
                    {
                        " Note": "The patient is a 52-year-old with left knee pain.",
                        "Dialogue": "[patient] I have left knee pain.",
                        "ICD10": "M25562",
                        "ICD10_desc": "PAIN IN LEFT KNEE",
                    },
                    {
                        " Note": "The patient is a 40-year-old with cough.",
                        "Dialogue": "[patient] I have cough.",
                        "ICD10": "R05",
                        "ICD10_desc": "COUGH",
                    },
                ],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "medsynth-export",
                    "--input",
                    str(medsynth_path),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic.jsonl")
            self.assertEqual(exported[0]["icd10_codes"], "R05")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())

    def test_cli_exports_synthea_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_dir = root / "synthea"
            csv_dir.mkdir()
            out_dir = root / "out"
            write_csv(
                csv_dir / "patients.csv",
                [
                    {"Id": "P1", "BIRTHDATE": "1980-01-01", "GENDER": "F", "RACE": "white", "ETHNICITY": "nonhispanic"},
                    {"Id": "P2", "BIRTHDATE": "1975-06-01", "GENDER": "M", "RACE": "asian", "ETHNICITY": "hispanic"},
                ],
            )
            write_csv(
                csv_dir / "conditions.csv",
                [
                    {"START": "2020-01-01", "PATIENT": "P1", "ENCOUNTER": "E1", "CODE": "59621000", "DESCRIPTION": "Hypertension"},
                    {"START": "2021-01-01", "PATIENT": "P2", "ENCOUNTER": "E2", "CODE": "44054006", "DESCRIPTION": "Diabetes mellitus"},
                ],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "synthea-export",
                    "--csv-dir",
                    str(csv_dir),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic.jsonl")
            self.assertEqual(exported[0]["diagnosis"], "Diabetes mellitus")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())

    def test_cli_exports_health_gym_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "health_gym.csv"
            out_dir = root / "out"
            write_csv(
                input_path,
                [
                    {"VL": "29.9", "CD4": "793.4", "Rel CD4": "30.8", "Gender": "1", "Ethnic": "3", "Drug (M)": "1", "PatientID": "0", "Timestep": "0"},
                    {"VL": "29.2", "CD4": "467.4", "Rel CD4": "30.3", "Gender": "1", "Ethnic": "3", "Drug (M)": "0", "PatientID": "0", "Timestep": "1"},
                    {"VL": "31.1", "CD4": "500.0", "Rel CD4": "28.1", "Gender": "0", "Ethnic": "2", "Drug (M)": "1", "PatientID": "1", "Timestep": "0"},
                    {"VL": "30.5", "CD4": "510.0", "Rel CD4": "28.5", "Gender": "0", "Ethnic": "2", "Drug (M)": "0", "PatientID": "1", "Timestep": "1"},
                ],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "health-gym-export",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic.jsonl")
            self.assertEqual(exported[0]["patient_id"], "1")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())

    def test_cli_exports_amlsim_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "tx.csv"
            out_dir = root / "out"
            write_csv(
                input_path,
                [
                    {
                        "TXN_ID": "1",
                        "ACCOUNT_ID": "1000000001",
                        "COUNTER_PARTY_ACCOUNT_NUM": "9000000001",
                        "TXN_SOURCE_TYPE_CODE": "CHECK",
                        "tx_count": "1",
                        "TXN_AMOUNT_ORIG": "120.50",
                        "start": "1",
                        "end": "1",
                    },
                    {
                        "TXN_ID": "2",
                        "ACCOUNT_ID": "1000000002",
                        "COUNTER_PARTY_ACCOUNT_NUM": "9000000002",
                        "TXN_SOURCE_TYPE_CODE": "WIRE",
                        "tx_count": "3",
                        "TXN_AMOUNT_ORIG": "5000",
                        "start": "2",
                        "end": "2",
                    },
                ],
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sde_bench",
                    "amlsim-export",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                ],
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            exported = load_records(out_dir / "synthetic.jsonl")
            self.assertEqual(exported[0]["transaction_type"], "WIRE")
            self.assertTrue((out_dir / "reference.jsonl").exists())
            self.assertTrue((out_dir / "source.jsonl").exists())


if __name__ == "__main__":
    unittest.main()

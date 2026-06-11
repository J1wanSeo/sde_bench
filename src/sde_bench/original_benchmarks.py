from __future__ import annotations

from typing import Any

Report = dict[str, Any]


BENCHMARK_FAMILIES: dict[str, Report] = {
    "kmuc_matching": {
        "origin_dataset": "KMUC synthetic lay cases",
        "native_task": "Patient lay text to department/doctor retrieval",
        "core_metric": "dept_top1, dept_hit@5, mrr_dept, proc_coverage@5, icd_coverage@5",
        "metric_formula": "dept_top1 = correct_top1 / N; hit@5 = any_correct_in_top5 / N; MRR = mean(1 / rank_expected_dept)",
        "required_inputs": "lay/patient text, expected department, candidate doctor/procedure/ICD index",
        "applicability_rule": "computed only when patient text, expected department, and the same candidate index are available",
        "portability": "Portable only when department labels and the same doctor/procedure index are available.",
    },
    "medsynth_dial_note": {
        "origin_dataset": "MedSynth",
        "native_task": "Dial-2-Note and Note-2-Dial fine-tuning on Aci-Bench",
        "core_metric": "LLM jury preference rate; optional BLEU/ROUGE/METEOR",
        "metric_formula": "win_rate = preferred_outputs / judged_outputs; text metrics use standard BLEU/ROUGE/METEOR against target notes/dialogues",
        "required_inputs": "paired dialogue and note, trainable generation model, Aci-Bench train/test, LLM judges",
        "applicability_rule": "computed only for paired dialogue-note datasets or adapters that can produce both directions",
        "portability": "Expensive and task-specific; not directly applicable to datasets without dialogue-note pairs.",
    },
    "simsum_symptom_ie": {
        "origin_dataset": "SimSUM",
        "native_task": "Symptom extraction from clinical notes",
        "core_metric": "F1 for dyspnea, cough, pain, nasal, fever; macro F1 for fever",
        "metric_formula": "F1_symptom = 2 * precision * recall / (precision + recall); macro_f1 = mean(F1_dyspnea, F1_cough, F1_pain, F1_nasal, F1_fever)",
        "required_inputs": "note text plus five respiratory symptom labels or spans",
        "applicability_rule": "computed only when notes expose gold respiratory symptom labels or span annotations",
        "portability": "Portable to respiratory datasets with symptom labels; otherwise requires label projection or manual annotation.",
    },
    "synthea_structured_ehr": {
        "origin_dataset": "Synthea",
        "native_task": "Structured synthetic EHR generation and standards-based interoperability",
        "core_metric": "Standard-format availability and structural consistency",
        "metric_formula": "mean(domain_coverage, standard_vocabulary_rate, temporal_traceability, relational_integrity)",
        "required_inputs": "patient, encounter, condition, procedure, drug, observation tables or equivalent FHIR/OMOP fields",
        "applicability_rule": "computed when structured EHR fields support patient, visit, condition, procedure, drug, and observation domains",
        "portability": "Portable to structured EHR/claims datasets; not applicable to pure text datasets.",
    },
}

DATASET_COLUMNS = ["KMUC", "MedSynth", "SimSUM", "Synthea", "HealthGymART"]

STAGE_A: dict[str, Report] = {
    "kmuc_matching": {
        "status": "computed",
        "value": "`dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931`",
        "why": "KMUC was designed for this retrieval/matching task.",
    },
    "medsynth_dial_note": {
        "status": "requires_adapter",
        "value": "n/a",
        "why": "KMUC has source EMR and lay text, not true doctor-patient dialogue paired with SOAP notes.",
    },
    "simsum_symptom_ie": {
        "status": "requires_labels",
        "value": "n/a",
        "why": "KMUC is multi-specialty and does not expose dyspnea/cough/pain/nasal/fever labels or spans.",
    },
    "synthea_structured_ehr": {
        "status": "not_applicable",
        "value": "n/a",
        "why": "KMUC current public benchmark export is case-level JSONL, not longitudinal EHR tables.",
    },
}

STAGE_B: dict[str, dict[str, Report]] = {
    "kmuc_matching": {
        "MedSynth": {"status": "not_applicable", "value": "n/a: no expected department or doctor index"},
        "SimSUM": {"status": "not_applicable", "value": "n/a: respiratory symptoms only, no department labels"},
        "Synthea": {"status": "not_applicable", "value": "n/a: structured EHR lacks KMUC doctor/procedure retrieval labels"},
        "HealthGymART": {"status": "not_applicable", "value": "n/a: no expected department or doctor index"},
    },
    "medsynth_dial_note": {
        "MedSynth": {
            "status": "paper_reported",
            "value": "Dial-2-Note `60.0%/95.0%/52.5%`; Note-2-Dial `55.0%/87.5%/80.0%` jury preference",
        },
        "SimSUM": {"status": "not_applicable", "value": "n/a: no dialogue-note pairs"},
        "Synthea": {"status": "not_applicable", "value": "n/a: no dialogue-note pairs"},
        "HealthGymART": {"status": "not_applicable", "value": "n/a: no dialogue-note pairs"},
    },
    "simsum_symptom_ie": {
        "MedSynth": {"status": "not_applicable", "value": "n/a: no gold dyspnea/cough/pain/nasal/fever labels"},
        "SimSUM": {
            "status": "paper_reported",
            "value": "normal F1 dyspnea `0.9617`, cough `0.9603`, pain `0.8143`, nasal `0.9628`, fever `0.9096`; compact F1 dyspnea `0.9444`, cough `0.9397`, pain `0.7940`, nasal `0.9622`, fever `0.9010`",
        },
        "Synthea": {"status": "requires_adapter", "value": "derive respiratory symptoms from Synthea conditions/observations"},
        "HealthGymART": {"status": "not_applicable", "value": "n/a: longitudinal HIV ART data lacks respiratory symptom labels"},
    },
    "synthea_structured_ehr": {
        "MedSynth": {"status": "not_applicable", "value": "n/a: text pair dataset"},
        "SimSUM": {"status": "not_applicable", "value": "n/a: single-encounter tabular/text benchmark"},
        "Synthea": {"status": "computed_from_sde_bench", "value": ""},
        "HealthGymART": {"status": "computed_from_sde_bench", "value": ""},
    },
}

SOURCE_NOTES = [
    "MedSynth original benchmark: https://arxiv.org/abs/2508.01401",
    "SimSUM original benchmark: https://arxiv.org/abs/2409.08936",
    "Synthea generator/sample page: https://synthetichealth.github.io/synthea/",
    "Synthea JAMIA paper: https://academic.oup.com/jamia/article/25/3/230/4098271",
    "Health Gym ART for HIV dataset: https://doi.org/10.6084/m9.figshare.22827878.v1",
    "Health Gym Scientific Data paper: https://www.nature.com/articles/s41597-022-01784-7",
]


def build_cross_benchmark_report(sde_reports: dict[str, Report]) -> Report:
    stage_b = {family: {dataset: dict(cell) for dataset, cell in cells.items()} for family, cells in STAGE_B.items()}
    for dataset, report in sde_reports.items():
        if dataset in stage_b["synthea_structured_ehr"]:
            score = _axis_score(report, "medical_interoperability")
            stage_b["synthea_structured_ehr"][dataset]["value"] = (
                f"`medical_interoperability={score:.4f}`" if score is not None else "n/a: no interoperability fields"
            )
    stage_ab = _combined_original_matrix(stage_b)
    stage_c = {
        dataset: _sde_summary(report)
        for dataset, report in sde_reports.items()
    }
    return {
        "schema_version": "0.1.0",
        "benchmark_families": BENCHMARK_FAMILIES,
        "stage_a": STAGE_A,
        "stage_b": stage_b,
        "stage_ab": stage_ab,
        "stage_c": stage_c,
        "source_notes": SOURCE_NOTES,
    }


def markdown_cross_benchmark(report: Report) -> str:
    lines = [
        "# Cross-Benchmark Evaluation Matrix",
        "",
        "This report separates two evaluation layers that should both appear in the paper:",
        "",
        "1. **SDE-Bench layer**: run every public synthetic medical dataset through the same SDE-Bench axes.",
        "2. **Original-benchmark layer**: treat each dataset paper's own evaluation protocol as a benchmark family, "
        "then test KMUC and the other public datasets against those protocols when the required fields exist.",
        "",
        "The second layer is stronger for publication because it avoids evaluating prior work only with our proposed "
        "metrics. It also exposes where each prior benchmark is narrow, task-specific, or not portable across dataset "
        "types.",
        "",
        "## Stage Definitions",
        "",
        "| Stage | Question | Rows | Columns |",
        "|---|---|---|---|",
        "| Stage A | How does KMUC perform under each prior dataset's original benchmark? | Original benchmark families | KMUC result and applicability |",
        "| Stage B | Under the same original benchmark, how do other public synthetic datasets perform? | Original benchmark families | MedSynth, SimSUM, Synthea, and future datasets |",
        "| Stage C | How do all datasets compare under SDE-Bench? | Datasets | SDE-Bench axes and overall score |",
        "",
        "## Original Benchmark Families",
        "",
        "| Benchmark Family | Origin Dataset | Native Task | Core Metric | Formula / Rule | Required Inputs | Portability |",
        "|---|---|---|---|---|---|---|",
    ]
    for key, family in report["benchmark_families"].items():
        lines.append(
            f"| `{key}` | {family['origin_dataset']} | {family['native_task']} | {family['core_metric']} | "
            f"{family['metric_formula']} | {family['required_inputs']} | {family['portability']} |"
        )
    combined_datasets = _dataset_columns(report["stage_ab"])
    lines.extend(
        [
            "",
            "## Stage A/B Combined: Prior Benchmarks Across Datasets",
            "",
            "| Benchmark Family | " + " | ".join(combined_datasets) + " |",
            "|---" + "|---:" * len(combined_datasets) + "|",
        ]
    )
    for key, cells in report["stage_ab"].items():
        rendered = [_render_cell(cells[dataset]) for dataset in combined_datasets]
        lines.append(f"| `{key}` | " + " | ".join(rendered) + " |")

    lines.extend(["", "## Stage A: KMUC Under Prior Benchmarks", "", "| Benchmark Family | KMUC Status | Current Result | Why |", "|---|---|---:|---|"])
    for key, cell in report["stage_a"].items():
        lines.append(f"| `{key}` | {cell['status']} | {cell['value']} | {cell['why']} |")

    datasets = _dataset_columns(report["stage_b"], include_kmuc=False)
    lines.extend(["", "## Stage B: Public Datasets Under Prior Benchmarks", "", "| Benchmark Family | " + " | ".join(datasets) + " |", "|---" + "|---:" * len(datasets) + "|"])
    for key, cells in report["stage_b"].items():
        rendered = [_render_cell(cells[dataset]) for dataset in datasets]
        lines.append(f"| `{key}` | " + " | ".join(rendered) + " |")

    lines.extend(
        [
            "",
            "## Stage C: SDE-Bench Cross-Dataset Results",
            "",
            "| Dataset | Overall | Fidelity | Utility | Privacy | Equity | Diversity | Groundedness | Validity | Interoperability |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for dataset, summary in report["stage_c"].items():
        lines.append(
            f"| {dataset} | {_fmt(summary['overall'])} | {_fmt(summary['medical_fidelity'])} | "
            f"{_fmt(summary['clinical_task_utility'])} | {_fmt(summary['privacy'])} | {_fmt(summary['equity'])} | "
            f"{_fmt(summary['medical_diversity'])} | {_fmt(summary['clinical_groundedness'])} | "
            f"{_fmt(summary['clinical_validity'])} | {_fmt(summary['medical_interoperability'])} |"
        )

    lines.extend(
        [
            "",
            "## Implementation Roadmap",
            "",
            "1. Keep each original paper protocol as a versioned benchmark family with explicit formula, required "
            "inputs, and applicability rules.",
            "2. Add executable dataset-to-benchmark view adapters for cells currently marked `requires_adapter` or "
            "`requires_labels`.",
            "3. For each Stage A/B cell, emit one of four states: `computed`, `paper_reported`, `requires_adapter`, "
            "or `not_applicable`.",
            "4. Compare numeric cells only when the same benchmark family, data split, and required labels are present. "
            "Otherwise, report the applicability state as part of the result.",
            "",
            "This keeps the paper claim defensible: KMUC can be shown against prior work's own tasks where portable, "
            "while SDE-Bench explains the common medical synthetic-data profile across heterogeneous datasets.",
        ]
    )

    lines.extend(["", "## Source Notes", ""])
    lines.extend(f"- {note}" for note in report.get("source_notes", []))
    lines.append("")
    return "\n".join(lines)


def _sde_summary(report: Report) -> Report:
    return {
        "overall": report.get("overall_score"),
        "medical_fidelity": _axis_score(report, "medical_fidelity"),
        "clinical_task_utility": _axis_score(report, "clinical_task_utility"),
        "privacy": _axis_score(report, "privacy"),
        "equity": _axis_score(report, "equity"),
        "medical_diversity": _axis_score(report, "medical_diversity"),
        "clinical_groundedness": _axis_score(report, "clinical_groundedness"),
        "clinical_validity": _axis_score(report, "clinical_validity"),
        "medical_interoperability": _axis_score(report, "medical_interoperability"),
    }


def _combined_original_matrix(stage_b: dict[str, dict[str, Report]]) -> dict[str, dict[str, Report]]:
    matrix: dict[str, dict[str, Report]] = {}
    for family in BENCHMARK_FAMILIES:
        cells = {"KMUC": dict(STAGE_A[family])}
        cells.update({dataset: dict(cell) for dataset, cell in stage_b.get(family, {}).items()})
        matrix[family] = cells
    return matrix


def _dataset_columns(stage: dict[str, dict[str, Report]], *, include_kmuc: bool = True) -> list[str]:
    present = {dataset for cells in stage.values() for dataset in cells}
    preferred = DATASET_COLUMNS if include_kmuc else [dataset for dataset in DATASET_COLUMNS if dataset != "KMUC"]
    columns = [dataset for dataset in preferred if dataset in present]
    columns.extend(sorted(present - set(columns)))
    return columns


def _axis_score(report: Report, axis: str) -> float | None:
    value = report.get("axes", {}).get(axis, {}).get("score")
    return float(value) if isinstance(value, int | float) and not isinstance(value, bool) else None


def _fmt(value: Any) -> str:
    if value is None:
        return "`n/a`"
    if isinstance(value, int | float) and not isinstance(value, bool):
        return f"`{float(value):.4f}`"
    return f"`{value}`"


def _render_cell(cell: Report) -> str:
    status = str(cell.get("status", "unknown"))
    value = str(cell.get("value", "n/a"))
    if value.startswith("n/a: "):
        return f"`{status}` ({value.removeprefix('n/a: ')})"
    if value == "n/a":
        return f"`{status}`"
    return f"`{status}`: {value}"

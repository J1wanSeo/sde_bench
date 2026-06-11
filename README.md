# SDE-Bench

Synthetic Medical Dataset Effectiveness Benchmark for evaluating synthetic
medical datasets, including LLM/RAG-generated patient cases and synthetic EHR
records.

SDE-Bench keeps the reusable shape of synthetic-data benchmark tools such as
SynthEval, but its target is medical data: clinical fidelity, downstream
clinical-task utility, privacy, equity, medical diversity, source grounding, and
clinical validity.

The benchmark interface is universal: any hospital, institution, public
synthetic EHR, or synthetic clinical-note dataset can be evaluated after mapping
its native files to the common JSON/JSONL/CSV schema.

## Evaluation Axes

SDE-Bench reports eight axes.

| Axis | Purpose | Origin |
|---|---|---|
| `medical_fidelity` | Distributional and pairwise similarity to a medical reference dataset | Synthetic-data benchmark core |
| `clinical_task_utility` | Downstream clinical label/task usefulness when expected/predicted fields exist | Synthetic-data benchmark core |
| `privacy` | Duplicate and nearest-reference memorization risk | SynthEval-style |
| `equity` | Sensitive-attribute distribution and group-target parity | Medical fairness/equity axis |
| `medical_diversity` | Coverage, entropy, and unique-record diversity | Synthetic-data benchmark core |
| `clinical_groundedness` | Source attribution and evidence support for generated clinical claims | SDE-Bench medical extension |
| `clinical_validity` | Rule/source consistency for fields such as ICD-10, procedure, acuity, laterality, department, and diagnosis | SDE-Bench medical extension |
| `medical_interoperability` | OMOP/FHIR-style structural readiness when longitudinal EHR fields are present | SDE-Bench medical extension |

The SDE-specific axes are `clinical_groundedness`, `clinical_validity`, and
`medical_interoperability`. They are intended for LLM + RAG pipelines and
medical synthetic EHRs, where the important question is not only whether records
resemble a target distribution, but also whether generated records are traceable
to evidence, clinically coherent, and mappable to standard data models when the
native dataset supports that claim.

For exact formulas, see [docs/formulas.md](docs/formulas.md). For the common
record schema, see [docs/schema.md](docs/schema.md).

## Install

From this folder:

```bash
python3 -m pip install -e .
```

The core package uses only the Python standard library.

## CLI

Single synthetic dataset:

```bash
python3 -m sde_bench evaluate \
  --real examples/real.csv \
  --synthetic examples/synthetic_good.csv \
  --source examples/source.csv \
  --target dept \
  --sensitive sex \
  --json-out reports/example_report.json \
  --md-out reports/example_report.md
```

JSON and JSONL are first-class input formats:

```bash
python3 -m sde_bench evaluate \
  --real exported/reference.jsonl \
  --synthetic exported/synthetic_lay.jsonl \
  --source exported/source.jsonl \
  --target dept \
  --sensitive sex
```

Dataset-specific adapters are optional convenience tools. For example, the KMUC
patient-case adapter exports local KMUC JSONL files into the common schema:

```bash
python3 -m sde_bench kmuc-export \
  --repo-root .. \
  --predictions ../layer3_datasets/patient_dataset/eval/H_kurev1_real_synth_v3.json \
  --out-dir reports/kmuc_export \
  --format jsonl
```

Multiple synthetic datasets:

```bash
python3 -m sde_bench benchmark \
  --real examples/real.csv \
  --synthetic-dir examples/synthetic_sets \
  --source examples/source.csv \
  --target dept \
  --sensitive sex \
  --json-out reports/example_benchmark.json
```

Original-paper benchmark matrix:

```bash
python3 -m sde_bench cross-benchmark \
  --sde-report KMUC=reports/kmuc_sde_report.json \
  --sde-report MedSynth=reports/public_benchmarks/medsynth/report.json \
  --sde-report SimSUM=reports/public_benchmarks/simsum/report.json \
  --sde-report Synthea=reports/public_benchmarks/synthea/report.json \
  --json-out reports/public_benchmarks/cross_benchmark_matrix.json \
  --md-out reports/public_benchmarks/cross_benchmark_matrix.md
```

Public synthetic dataset survey:

```bash
python3 -m sde_bench dataset-survey \
  --json-out reports/public_benchmarks/domain_dataset_survey.json \
  --md-out reports/public_benchmarks/domain_dataset_survey.md
```

## Python API

```python
from sde_bench import evaluate, load_records

report = evaluate(
    real=load_records("examples/real.csv"),
    synthetic=load_records("examples/synthetic_good.csv"),
    target="dept",
)
print(report["overall_score"])
```

## Output Shape

Each report contains:

- `schema_version`
- `records.real` and `records.synthetic`
- `axes.<axis>.score`
- `axes.<axis>.metrics`
- `overall_score`
- `skipped`, listing metrics that require missing optional inputs

The overall score is intentionally a convenience summary, not the scientific
claim. Papers should report the axis table and the task-specific metrics.

## SynthEval Completeness Checklist

| Requirement | SDE-Bench status |
|---|---|
| Public Python package layout | `pyproject.toml`, `src/sde_bench` |
| CLI | `python -m sde_bench evaluate/benchmark` |
| Single-dataset evaluation | `evaluate` |
| Multi-dataset benchmark | `benchmark` |
| Preset configs | `configs/full_eval.json`, `fast_eval.json`, `privacy_eval.json` |
| Metric modularity | axis functions in `core.py`; output shape supports new metric modules |
| Rankable benchmark output | `ranking` table with per-dataset reports |
| JSON report | `--json-out` |
| Markdown report | `--md-out` |
| Examples | `examples/` |
| Tests | `tests/` |
| License | MIT |

## Current Scope

This is an alpha medical benchmark package. It is designed to evaluate synthetic
medical datasets before a real holdout dataset is available, while leaving room
for later TSTR/TRTR, membership-inference, attribute-disclosure, clinical
review, and external dataset registry modules. Metrics that need missing inputs
are reported as skipped instead of silently omitted.

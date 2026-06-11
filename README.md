# SDE-Bench

Synthetic Dataset Effectiveness Benchmark for evaluating synthetic datasets with
standard utility/privacy criteria and two additional axes for LLM/RAG-generated,
evidence-grounded datasets.

SDE-Bench follows the public-package expectations established by tools such as
SynthEval: a reusable Python API, a command-line interface, preset evaluation
profiles, single-dataset evaluation, multi-dataset benchmarking, rankable output,
example data, tests, and JSON/Markdown reports.

## Evaluation Axes

SDE-Bench reports seven axes.

| Axis | Purpose | Origin |
|---|---|---|
| `fidelity` | Distributional and pairwise similarity to a reference dataset | SynthEval-style |
| `utility` | Downstream label/task usefulness when expected/predicted fields exist | SynthEval-style |
| `privacy` | Duplicate and nearest-reference memorization risk | SynthEval-style |
| `fairness` | Sensitive-attribute distribution and group-target parity | SynthEval-style |
| `diversity` | Coverage, entropy, and unique-record diversity | Common synthetic-data axis |
| `groundedness` | Source attribution and evidence support for generated claims | SDE-Bench extension |
| `domain_consistency` | Rule/source consistency for domain fields such as department and diagnosis | SDE-Bench extension |

The two SDE-specific axes are `groundedness` and `domain_consistency`. They are
intended for datasets generated from LLM + RAG pipelines, where the important
question is not only whether records resemble a target distribution, but also
whether generated records are traceable to evidence and internally/domain
consistent.

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

This is an alpha benchmark package. It is designed to be useful before a real
holdout dataset is available, while leaving room for later TSTR/TRTR,
membership-inference, and attribute-disclosure modules. Metrics that need those
inputs are reported as skipped instead of silently omitted.


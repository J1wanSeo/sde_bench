# Dataset Registry

SDE-Bench targets synthetic medical datasets from any institution or generator.
Each dataset should be adapted into the common schema in `docs/schema.md`,
preferably as JSONL.

## Status Labels

1. `evaluated`
   - Adapter, input manifest, command, and SDE-Bench report exist in this repo
     or an archived experiment bundle.

2. `adapter_ready`
   - Adapter exists, but the dataset has not been evaluated in the current
     report set.

3. `candidate`
   - Dataset appears suitable, but adapter and evaluation have not been
     completed.

4. `superseded`
   - Earlier dataset identifier or repository path that has moved to another
     maintained location.

## Evaluated Datasets

| Dataset ID | Status | Native Format | Adapter | Current Report |
|---|---|---|---|---|
| `kmuc_patient_cases_lay` | `evaluated` | JSONL + evaluation JSON | `python -m sde_bench kmuc-export` | `reports/kmuc_sde_report.md` |
| `medsynth_dialogue_note` | `evaluated` | CSV | `python -m sde_bench medsynth-export` | `reports/public_benchmarks/medsynth/report.md` |
| `simsum_respiratory` | `evaluated` | Semicolon CSV | `python -m sde_bench synsum-export` | `reports/public_benchmarks/simsum/report.md` |
| `synthea_ehr_sample` | `evaluated` | CSV tables | `python -m sde_bench synthea-export` | `reports/public_benchmarks/synthea/report.md` |

The current original-paper benchmark matrix is generated at
`reports/public_benchmarks/cross_benchmark_matrix.md` and keeps three stages:
KMUC under prior benchmark families, public datasets under those same benchmark
families, and all datasets under SDE-Bench.

The current domain-expansion survey is generated at
`reports/public_benchmarks/domain_dataset_survey.md`. It records medical,
finance, and science candidates, their native original-paper metrics, and the
adapter work needed before a dataset can be marked `evaluated`.

## External Public Candidates

This table keeps only short medical notes. Use the generated domain survey for
the full cross-domain candidate matrix and next-batch priority list.

| Dataset ID | Status | Source | Why It Fits | Adapter Work |
|---|---|---|---|---|
| `de_synpuf_claims` | `candidate` | https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files | CMS synthetic claims files; useful for claims-style distributional, privacy, equity, and utilization-task evaluation. | Map beneficiary, claim, diagnosis, and procedure files to patient or encounter records. |
| `health_gym_icu` | `next_batch` | https://arxiv.org/abs/2203.06369 | Public synthetic longitudinal health data for offline reinforcement learning and medical time-series evaluation. | Flatten ICU/HIV trajectories into JSONL visit/time records. |
| `sm3_text_to_query` | `candidate` | https://arxiv.org/abs/2411.05521 | Synthea-derived synthetic medical database plus text-to-query benchmark. | Extract patient tables separately from query-pair task data. |
| `synsum_respiratory` | `superseded` | https://github.com/prabaey/SynSUM | Earlier repository name for SimSUM/SynSUM materials. | Use `simsum_respiratory` from https://github.com/prabaey/SimSUM. |
| `medsyn_ru_notes` | `candidate` | https://arxiv.org/abs/2408.02056 | Open-source synthetic Russian clinical notes with ICD labels reported by the authors. | Locate dataset release, map ICD labels to `icd10_codes`, and evaluate multilingual text grounding carefully. |

## Evaluation Policy

1. Do not claim a candidate dataset is evaluated until its adapter, command, and
   report are present.
2. Report both axis scores and raw metrics. The overall score is only a compact
   ranking convenience.
3. Record native dataset licenses and redistribution limits before committing
   converted data.
4. For clinical text datasets without source evidence, run `evaluate` without
   `--source`; SDE-Bench will mark source-dependent groundedness and validity
   checks as skipped.

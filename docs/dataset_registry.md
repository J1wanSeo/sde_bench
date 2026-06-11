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

## External Public Candidates

| Dataset ID | Status | Source | Why It Fits | Adapter Work |
|---|---|---|---|---|
| `synthea_ehr` | `candidate` | https://github.com/synthetichealth/synthea | Public synthetic EHR generator and datasets; useful for structured EHR fidelity, privacy, equity, diversity, and clinical validity. | Needs Java runtime to generate CSV/FHIR locally, then map patient/condition/procedure/encounter outputs to patient-level JSONL. |
| `de_synpuf_claims` | `candidate` | https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files | CMS synthetic claims files; useful for claims-style distributional, privacy, equity, and utilization-task evaluation. | Map beneficiary, claim, diagnosis, and procedure files to patient or encounter records. |
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

# Medical Synthetic Dataset Comparison

This report compares public synthetic medical datasets using two layers:

1. Metrics reported by the original dataset authors.
2. SDE-Bench metrics computed through the shared schema.

For the cross-evaluation design where each original paper's benchmark becomes a
benchmark family, see `reports/public_benchmarks/cross_benchmark_matrix.md`.

The goal is not to claim that one scalar score proves superiority. The intended
paper claim is that KMUC exposes additional clinically relevant evidence,
utility, equity, and validity dimensions that are not jointly reported by prior
synthetic medical datasets.

## Datasets

| Dataset | Domain | Public Source | SDE-Bench Input |
|---|---|---|---|
| KMUC synthetic lay cases | Korean patient-to-department/doctor matching | Local generated dataset | 150 reference cases, 750 lay synthetic records |
| MedSynth | Synthetic medical dialogue-note pairs | https://huggingface.co/datasets/Ahmad0067/MedSynth | 5,120 reference notes, 5,120 synthetic note/dialogue records |
| SimSUM | Simulated respiratory structured + note records | https://github.com/prabaey/SimSUM | 1,000 reference records, 1,000 compact-note synthetic records sampled from first 2,000 rows |
| Synthea sample CSV | Synthetic longitudinal EHR generator sample | https://synthetichealth.github.io/synthea/ | 585 reference patients, 586 synthetic patients from the official April 2020 CSV sample |
| Health Gym ART for HIV | Synthetic longitudinal ART/HIV monthly records | https://doi.org/10.6084/m9.figshare.22827878.v1 | 300 reference records, 300 synthetic monthly records sampled from first 600 rows |

## Original Paper Metrics

| Dataset | Original Evaluation Focus | Reported Numbers |
|---|---|---|
| KMUC synthetic lay cases | Department matching and doctor retrieval with KURE-v1 | `dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931` |
| MedSynth | Extrinsic Dial-2-Note and Note-2-Dial model utility on Aci-Bench, judged by LLM jury | Dial-2-Note jury preference in favor of MedSynth: `60.0%` vs NoteChat+AciTrain, `95.0%` MedSynth-only vs NoteChat-only, `52.5%` vs AciTrain-only. Note-2-Dial: `55.0%`, `87.5%`, `80.0%` respectively. |
| SimSUM | Symptom extraction F1 over synthetic respiratory records | Latest arXiv v4 Table 4 neural-text F1, normal: dyspnea `0.9617`, cough `0.9603`, pain `0.8143`, nasal `0.9628`, fever `0.9096`. Compact: dyspnea `0.9444`, cough `0.9397`, pain `0.7940`, nasal `0.9622`, fever `0.9010`. |
| Synthea sample CSV | Public generator/sample release in FHIR, C-CDA, and CSV formats | The official sample page reports availability of over a thousand sample patients across export formats, but does not attach a single dataset-paper numeric quality metric to this CSV bundle. |
| Health Gym ART for HIV | Longitudinal synthetic ART data generated with WGAN-GP+VAE+Buffer and used for health data education/analytics | Figshare metadata reports `534,960` records, `8,916` synthetic patients, `60` monthly time points, and `15` columns. SDE-Bench uses a sampled run because current privacy distance is quadratic. |

## SDE-Bench Results

| Dataset | Overall | Medical Fidelity | Clinical Task Utility | Privacy | Equity | Medical Diversity | Clinical Groundedness | Clinical Validity | Medical Interoperability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KMUC synthetic lay cases | `0.8092` | `1.0000` | `0.8733` | `0.5000` | `0.8474` | `1.0000` | `0.5028` | `0.9408` | `n/a**` |
| MedSynth | `0.7446` | `0.2289` | `1.0000` | `0.7061` | `n/a*` | `0.7198` | `0.8128` | `1.0000` | `n/a**` |
| SimSUM sampled compact notes | `0.7843` | `0.9531` | `1.0000` | `0.1340` | `n/a*` | `0.7648` | `0.8540` | `1.0000` | `n/a**` |
| Synthea sample CSV | `0.8226` | `0.3033` | `0.9898` | `0.7521` | `0.7254` | `0.8123` | `1.0000` | `0.9978` | `1.0000` |
| Health Gym ART for HIV sampled rows | `0.8991` | `0.7517` | `1.0000` | `0.6104` | `0.9500` | `0.9225` | `1.0000` | `1.0000` | `0.9583` |

`*` Equity is skipped/no-sensitive-columns for MedSynth and SimSUM, so the
axis is excluded from the overall score. It should not be interpreted as
demonstrated fairness.

`**` Medical interoperability is skipped when the released records do not expose
OMOP/FHIR/CSV-derived interoperability fields. It is excluded from the overall
score rather than penalizing unstructured text datasets.

## Interpretation

1. KMUC is currently strongest on the dimensions that match the target medical
   service task: explicit department utility, sex-aware equity reporting,
   complete category coverage, and source-linked clinical validity.
2. MedSynth is strong on source-to-note lexical grounding and ICD code validity,
   and its own paper shows strong extrinsic generation utility. It does not
   expose demographic variables for equity analysis in the released CSV.
3. SimSUM is strong on structured fidelity and note compactness/grounding, but
   the sampled benchmark flags high exact-duplicate-like structural similarity
   under SDE-Bench privacy because compact-note records retain the same tabular
   variables as their source records.
4. Synthea is strongest on structured EHR interoperability because the official
   CSV exposes patient, encounter, condition, procedure, medication, and
   observation tables that map cleanly to OMOP-style domains. Its lower
   `medical_fidelity` in this run reflects a patient-level first-half/second-half
   split of one generated sample, not a real-vs-synthetic training holdout.
5. Health Gym ART shows strong longitudinal structured-data scores in the
   sampled run, especially equity, diversity, groundedness, validity, and
   interoperability. Its score should be interpreted as a sampled smoke-scale
   benchmark until SDE-Bench privacy distance is optimized for the full 534,960
   row release.
6. KMUC's weakest current SDE-Bench axis is lexical `clinical_groundedness`
   because Korean lay descriptions are compared against abbreviated mixed
   Korean/English EMR notes with token overlap. This should be upgraded with a
   semantic evidence checker or clinician review before making strong factual
   grounding claims.

## Reproduction Commands

```bash
curl -L https://huggingface.co/datasets/Ahmad0067/MedSynth/resolve/main/MedSynth_huggingface_final.csv \
  -o data/public_raw/medsynth/MedSynth_huggingface_final.csv

PYTHONPATH=src python3 -m sde_bench medsynth-export \
  --input data/public_raw/medsynth/MedSynth_huggingface_final.csv \
  --out-dir reports/public_benchmarks/medsynth \
  --format jsonl

PYTHONPATH=src python3 -m sde_bench evaluate \
  --real reports/public_benchmarks/medsynth/reference.jsonl \
  --synthetic reports/public_benchmarks/medsynth/synthetic.jsonl \
  --source reports/public_benchmarks/medsynth/source.jsonl \
  --target diagnosis_group \
  --json-out reports/public_benchmarks/medsynth/report.json \
  --md-out reports/public_benchmarks/medsynth/report.md
```

```bash
curl -L https://synthetichealth.github.io/synthea-sample-data/downloads/synthea_sample_data_csv_apr2020.zip \
  -o data/public_raw/synthea/synthea_sample_data_csv_apr2020.zip

unzip -o data/public_raw/synthea/synthea_sample_data_csv_apr2020.zip \
  -d data/public_raw/synthea

PYTHONPATH=src python3 -m sde_bench synthea-export \
  --csv-dir data/public_raw/synthea/csv \
  --out-dir reports/public_benchmarks/synthea \
  --format jsonl

PYTHONPATH=src python3 -m sde_bench evaluate \
  --real reports/public_benchmarks/synthea/reference.jsonl \
  --synthetic reports/public_benchmarks/synthea/synthetic.jsonl \
  --source reports/public_benchmarks/synthea/source.jsonl \
  --target diagnosis_group \
  --sensitive sex,race,ethnicity \
  --json-out reports/public_benchmarks/synthea/report.json \
  --md-out reports/public_benchmarks/synthea/report.md
```

```bash
curl -L https://raw.githubusercontent.com/prabaey/SimSUM/main/SimSUM.csv \
  -o data/public_raw/synsum/SimSUM.csv

PYTHONPATH=src python3 -m sde_bench synsum-export \
  --input data/public_raw/synsum/SimSUM.csv \
  --out-dir reports/public_benchmarks/simsum \
  --format jsonl \
  --limit 2000

PYTHONPATH=src python3 -m sde_bench evaluate \
  --real reports/public_benchmarks/simsum/reference.jsonl \
  --synthetic reports/public_benchmarks/simsum/synthetic.jsonl \
  --source reports/public_benchmarks/simsum/source.jsonl \
  --target diagnosis_group \
  --json-out reports/public_benchmarks/simsum/report.json \
  --md-out reports/public_benchmarks/simsum/report.md
```

```bash
curl -L https://ndownloader.figshare.com/files/40584980 \
  -o data/public_raw/health_gym/HealthGymV2_CbdrhDatathon_ART4HIV.csv

PYTHONPATH=src python3 -m sde_bench health-gym-export \
  --input data/public_raw/health_gym/HealthGymV2_CbdrhDatathon_ART4HIV.csv \
  --out-dir reports/public_benchmarks/health_gym \
  --format jsonl \
  --limit 600

PYTHONPATH=src python3 -m sde_bench evaluate \
  --real reports/public_benchmarks/health_gym/reference.jsonl \
  --synthetic reports/public_benchmarks/health_gym/synthetic.jsonl \
  --source reports/public_benchmarks/health_gym/source.jsonl \
  --target diagnosis_group \
  --sensitive sex,ethnicity \
  --json-out reports/public_benchmarks/health_gym/report.json \
  --md-out reports/public_benchmarks/health_gym/report.md
```

## Source Notes

- MedSynth paper: https://arxiv.org/html/2508.01401v1
- MedSynth dataset: https://huggingface.co/datasets/Ahmad0067/MedSynth
- SimSUM paper/repository: https://github.com/prabaey/SimSUM
- SimSUM arXiv version: https://arxiv.org/html/2409.08936v1
- Synthea project/sample page: https://synthetichealth.github.io/synthea/
- Synthea sample CSV bundle: https://synthetichealth.github.io/synthea-sample-data/downloads/synthea_sample_data_csv_apr2020.zip
- Health Gym ART for HIV Figshare dataset: https://doi.org/10.6084/m9.figshare.22827878.v1
- Health Gym Scientific Data paper: https://www.nature.com/articles/s41597-022-01784-7

## Attempted Additional Baselines

1. CMS SynPUF
   - Source: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files
   - Status: candidate. The public CMS page documents the synthetic claims
     purpose and user agreement, but the current automated run did not obtain a
     stable direct data-file URL.

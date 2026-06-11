# Medical Synthetic Dataset Comparison

This report compares public synthetic medical datasets using two layers:

1. Metrics reported by the original dataset authors.
2. SDE-Bench metrics computed through the shared schema.

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

## Original Paper Metrics

| Dataset | Original Evaluation Focus | Reported Numbers |
|---|---|---|
| KMUC synthetic lay cases | Department matching and doctor retrieval with KURE-v1 | `dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931` |
| MedSynth | Extrinsic Dial-2-Note and Note-2-Dial model utility on Aci-Bench, judged by LLM jury | Dial-2-Note jury preference in favor of MedSynth: `60.0%` vs NoteChat+AciTrain, `95.0%` MedSynth-only vs NoteChat-only, `52.5%` vs AciTrain-only. Note-2-Dial: `55.0%`, `87.5%`, `80.0%` respectively. |
| SimSUM | Symptom extraction F1 over synthetic respiratory records | Normal-note neural-text F1: dyspnea `0.9660`, cough `0.9595`, pain `0.8415`, nasal `0.9602`, fever `0.9074`. Compact-note neural-text F1: dyspnea `0.9383`, cough `0.9480`, pain `0.7828`, nasal `0.9583`, fever `0.8904`. |

## SDE-Bench Results

| Dataset | Overall | Medical Fidelity | Clinical Task Utility | Privacy | Equity | Medical Diversity | Clinical Groundedness | Clinical Validity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| KMUC synthetic lay cases | `0.8092` | `1.0000` | `0.8733` | `0.5000` | `0.8474` | `1.0000` | `0.5028` | `0.9408` |
| MedSynth | `0.7446` | `0.2289` | `1.0000` | `0.7061` | `n/a*` | `0.7198` | `0.8128` | `1.0000` |
| SimSUM sampled compact notes | `0.7843` | `0.9531` | `1.0000` | `0.1340` | `n/a*` | `0.7648` | `0.8540` | `1.0000` |

`*` Equity is skipped/no-sensitive-columns for MedSynth and SimSUM, so the
axis is excluded from the overall score. It should not be interpreted as
demonstrated fairness.

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
4. KMUC's weakest current SDE-Bench axis is lexical `clinical_groundedness`
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

## Source Notes

- MedSynth paper: https://arxiv.org/html/2508.01401v1
- MedSynth dataset: https://huggingface.co/datasets/Ahmad0067/MedSynth
- SimSUM paper/repository: https://github.com/prabaey/SimSUM
- SimSUM arXiv version: https://arxiv.org/html/2409.08936v1

## Attempted Additional Baselines

1. Synthea EHR generator
   - Source: https://github.com/synthetichealth/synthea
   - Status: not evaluated in this run because the local environment has no Java
     runtime. Synthea remains the next preferred EHR-style baseline once Java is
     available.

2. CMS SynPUF
   - Source: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files
   - Status: candidate. The public CMS page documents the synthetic claims
     purpose and user agreement, but the current automated run did not obtain a
     stable direct data-file URL.

# Cross-Benchmark Evaluation Matrix

This report separates two evaluation layers that should both appear in the paper:

1. **SDE-Bench layer**: run every public synthetic medical dataset through the same SDE-Bench axes.
2. **Original-benchmark layer**: treat each dataset paper's own evaluation protocol as a benchmark family, then test KMUC and the other public datasets against those protocols when the required fields exist.

The second layer is stronger for publication because it avoids evaluating prior work only with our proposed metrics. It also exposes where each prior benchmark is narrow, task-specific, or not portable across dataset types.

## Stage Definitions

| Stage | Question | Rows | Columns |
|---|---|---|---|
| Stage A | How does KMUC perform under each prior dataset's original benchmark? | Original benchmark families | KMUC result and applicability |
| Stage B | Under the same original benchmark, how do other public synthetic datasets perform? | Original benchmark families | MedSynth, SimSUM, Synthea, and future datasets |
| Stage C | How do all datasets compare under SDE-Bench? | Datasets | SDE-Bench axes and overall score |

## Original Benchmark Families

| Benchmark Family | Origin Dataset | Native Task | Core Metric | Required Inputs | Portability |
|---|---|---|---|---|---|
| `kmuc_matching` | KMUC synthetic lay cases | Patient lay text to department/doctor retrieval | dept_top1, dept_hit@5, mrr_dept, proc_coverage@5, icd_coverage@5 | lay/patient text, expected department, candidate doctor/procedure/ICD index | Portable only when department labels and the same doctor/procedure index are available. |
| `medsynth_dial_note` | MedSynth | Dial-2-Note and Note-2-Dial fine-tuning on Aci-Bench | LLM jury preference rate; optional BLEU/ROUGE/METEOR | paired dialogue and note, trainable generation model, Aci-Bench train/test, LLM judges | Expensive and task-specific; not directly applicable to datasets without dialogue-note pairs. |
| `simsum_symptom_ie` | SimSUM | Symptom extraction from clinical notes | F1 for dyspnea, cough, pain, nasal, fever; macro F1 for fever | note text plus five respiratory symptom labels or spans | Portable to respiratory datasets with symptom labels; otherwise requires label projection or manual annotation. |
| `synthea_structured_ehr` | Synthea | Structured synthetic EHR generation and standards-based interoperability | Standard-format availability and structural consistency | patient, encounter, condition, procedure, drug, observation tables or equivalent FHIR/OMOP fields | Portable to structured EHR/claims datasets; not applicable to pure text datasets. |

## Stage A: KMUC Under Prior Benchmarks

| Benchmark Family | KMUC Status | Current Result | Why |
|---|---|---:|---|
| `kmuc_matching` | computed | `dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931` | KMUC was designed for this retrieval/matching task. |
| `medsynth_dial_note` | requires_adapter | n/a | KMUC has source EMR and lay text, not true doctor-patient dialogue paired with SOAP notes. |
| `simsum_symptom_ie` | requires_labels | n/a | KMUC is multi-specialty and does not expose dyspnea/cough/pain/nasal/fever labels or spans. |
| `synthea_structured_ehr` | not_applicable | n/a | KMUC current public benchmark export is case-level JSONL, not longitudinal EHR tables. |

## Stage B: Public Datasets Under Prior Benchmarks

| Benchmark Family | MedSynth | SimSUM | Synthea |
|---|---:|---:|---:|
| `kmuc_matching` | `not_applicable` (no expected department or doctor index) | `not_applicable` (respiratory symptoms only, no department labels) | `not_applicable` (structured EHR lacks KMUC doctor/procedure retrieval labels) |
| `medsynth_dial_note` | `paper_reported`: Dial-2-Note `60.0%/95.0%/52.5%`; Note-2-Dial `55.0%/87.5%/80.0%` jury preference | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) |
| `simsum_symptom_ie` | `not_applicable` (no gold dyspnea/cough/pain/nasal/fever labels) | `paper_reported`: normal F1 dyspnea `0.9617`, cough `0.9603`, pain `0.8143`, nasal `0.9628`, fever `0.9096`; compact F1 dyspnea `0.9444`, cough `0.9397`, pain `0.7940`, nasal `0.9622`, fever `0.9010` | `requires_adapter`: derive respiratory symptoms from Synthea conditions/observations |
| `synthea_structured_ehr` | `not_applicable` (text pair dataset) | `not_applicable` (single-encounter tabular/text benchmark) | `computed_from_sde_bench`: `medical_interoperability=1.0000` |

## Stage C: SDE-Bench Cross-Dataset Results

| Dataset | Overall | Fidelity | Utility | Privacy | Equity | Diversity | Groundedness | Validity | Interoperability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KMUC | `0.8092` | `1.0000` | `0.8733` | `0.5000` | `0.8474` | `1.0000` | `0.5028` | `0.9408` | `n/a` |
| MedSynth | `0.7446` | `0.2289` | `1.0000` | `0.7061` | `n/a` | `0.7198` | `0.8128` | `1.0000` | `n/a` |
| SimSUM | `0.7843` | `0.9531` | `1.0000` | `0.1340` | `n/a` | `0.7648` | `0.8540` | `1.0000` | `n/a` |
| Synthea | `0.8226` | `0.3033` | `0.9898` | `0.7521` | `0.7254` | `0.8123` | `1.0000` | `0.9978` | `1.0000` |

## Implementation Roadmap

1. Implement `benchmark_families/` with one module per original benchmark: `kmuc_matching`, `medsynth_dial_note`, `simsum_symptom_ie`, and `synthea_structured_ehr`.
2. Add dataset-to-benchmark view adapters. These should produce benchmark-native inputs, not mutate the SDE-Bench canonical records.
3. For each cell in Stage A/B, emit one of three states: `computed`, `not_applicable`, or `requires_adapter`.
4. Only compare numeric cells when the same benchmark family, data split, and required labels are present. Otherwise, report the applicability state.

This keeps the paper claim defensible: KMUC can be shown against prior work's own tasks where portable, while SDE-Bench explains the common medical synthetic-data profile across heterogeneous datasets.

## Source Notes

- MedSynth original benchmark: https://arxiv.org/abs/2508.01401
- SimSUM original benchmark: https://arxiv.org/abs/2409.08936
- Synthea generator/sample page: https://synthetichealth.github.io/synthea/
- Synthea JAMIA paper: https://academic.oup.com/jamia/article/25/3/230/4098271

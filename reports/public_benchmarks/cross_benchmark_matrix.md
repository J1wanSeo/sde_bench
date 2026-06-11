# Cross-Benchmark Evaluation Matrix

This report separates two evaluation layers that should both appear in the paper:

1. **Original-benchmark layer**: treat each dataset paper's own evaluation protocol as a benchmark family, then test KMUC and the other public datasets against those protocols when the required fields exist.
2. **SDE-Bench layer**: run every public synthetic medical dataset through the same SDE-Bench axes.

The first layer is stronger for publication because it avoids evaluating prior work only with our proposed metrics. The second layer then explains the common medical synthetic-data profile across heterogeneous dataset types.

## Stage Definitions

| Stage | Question | Rows | Columns |
|---|---|---|---|
| Stage A | How do KMUC and public datasets perform under each prior dataset's original benchmark? | Original benchmark families | KMUC plus public synthetic datasets |
| Stage B | How do all datasets compare under SDE-Bench? | Datasets | SDE-Bench axes and overall score |

## Original Benchmark Families

| Benchmark Family | Origin Dataset | Native Task | Core Metric | Formula / Rule | Required Inputs | Portability |
|---|---|---|---|---|---|---|
| `kmuc_matching` | KMUC synthetic lay cases | Patient lay text to department/doctor retrieval | dept_top1, dept_hit@5, mrr_dept, proc_coverage@5, icd_coverage@5 | dept_top1 = correct_top1 / N; hit@5 = any_correct_in_top5 / N; MRR = mean(1 / rank_expected_dept) | lay/patient text, expected department, candidate doctor/procedure/ICD index | Portable only when department labels and the same doctor/procedure index are available. |
| `medsynth_dial_note` | MedSynth | Dial-2-Note and Note-2-Dial fine-tuning on Aci-Bench | LLM jury preference rate; optional BLEU/ROUGE/METEOR | win_rate = preferred_outputs / judged_outputs; text metrics use standard BLEU/ROUGE/METEOR against target notes/dialogues | paired dialogue and note, trainable generation model, Aci-Bench train/test, LLM judges | Expensive and task-specific; not directly applicable to datasets without dialogue-note pairs. |
| `simsum_symptom_ie` | SimSUM | Symptom extraction from clinical notes | F1 for dyspnea, cough, pain, nasal, fever; macro F1 for fever | F1_symptom = 2 * precision * recall / (precision + recall); macro_f1 = mean(F1_dyspnea, F1_cough, F1_pain, F1_nasal, F1_fever) | note text plus five respiratory symptom labels or spans | Portable to respiratory datasets with symptom labels; otherwise requires label projection or manual annotation. |
| `synthea_structured_ehr` | Synthea | Structured synthetic EHR generation and standards-based interoperability | Standard-format availability and structural consistency | mean(domain_coverage, standard_vocabulary_rate, temporal_traceability, relational_integrity) | patient, encounter, condition, procedure, drug, observation tables or equivalent FHIR/OMOP fields | Portable to structured EHR/claims datasets; not applicable to pure text datasets. |

## Stage A: Original-Metric Crosswalk

| Benchmark Family | KMUC | MedSynth | SimSUM | Synthea | HealthGymART | DeSynPUF |
|---|---:|---:|---:|---:|---:|---:|
| `kmuc_matching` | `computed`: `dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931` | `not_applicable` (no expected department or doctor index) | `not_applicable` (respiratory symptoms only, no department labels) | `not_applicable` (structured EHR lacks KMUC doctor/procedure retrieval labels) | `not_applicable` (no expected department or doctor index) | `not_applicable` (claims tables lack KMUC doctor/procedure retrieval labels) |
| `medsynth_dial_note` | `requires_adapter` | `paper_reported`: Dial-2-Note `60.0%/95.0%/52.5%`; Note-2-Dial `55.0%/87.5%/80.0%` jury preference | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) |
| `simsum_symptom_ie` | `requires_labels` | `not_applicable` (no gold dyspnea/cough/pain/nasal/fever labels) | `paper_reported`: normal F1 dyspnea `0.9617`, cough `0.9603`, pain `0.8143`, nasal `0.9628`, fever `0.9096`; compact F1 dyspnea `0.9444`, cough `0.9397`, pain `0.7940`, nasal `0.9622`, fever `0.9010` | `requires_adapter`: derive respiratory symptoms from Synthea conditions/observations | `not_applicable` (longitudinal HIV ART data lacks respiratory symptom labels) | `not_applicable` (claims data lacks respiratory symptom labels) |
| `synthea_structured_ehr` | `not_applicable` | `not_applicable` (no interoperability fields) | `not_applicable` (no interoperability fields) | `computed_from_sde_bench`: `medical_interoperability=1.0000` | `computed_from_sde_bench`: `medical_interoperability=0.9583` | `computed_from_sde_bench`: `medical_interoperability=0.9165` |

## Stage B: SDE-Bench Cross-Dataset Results

| Dataset | Overall | Fidelity | Utility | Privacy | Equity | Diversity | Scope | Groundedness | Validity | Interoperability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KMUC | `0.8302` | `1.0000` | `0.8733` | `0.5000` | `0.8474` | `1.0000` | `0.9770` | `0.5028` | `0.9408` | `n/a` |
| MedSynth | `0.6956` | `0.2289` | `1.0000` | `0.7249` | `n/a` | `0.7198` | `0.3827` | `0.8128` | `1.0000` | `n/a` |
| SimSUM | `0.7021` | `0.9531` | `1.0000` | `0.1340` | `n/a` | `0.7648` | `0.2086` | `0.8540` | `1.0000` | `n/a` |
| Synthea | `0.8050` | `0.3033` | `0.9898` | `0.7521` | `0.7254` | `0.8123` | `0.6652` | `1.0000` | `0.9974` | `1.0000` |
| HealthGymART | `0.8550` | `0.9537` | `1.0000` | `0.5929` | `0.9987` | `0.9660` | `0.2253` | `1.0000` | `1.0000` | `0.9583` |
| DeSynPUF | `0.8744` | `0.5969` | `0.9992` | `0.7538` | `0.9201` | `0.9279` | `0.8156` | `1.0000` | `0.9393` | `0.9165` |

## Implementation Roadmap

1. Keep each original paper protocol as a versioned benchmark family with explicit formula, required inputs, and applicability rules.
2. Add executable dataset-to-original-benchmark adapters for cells currently marked `requires_adapter` or `requires_labels`.
3. For each Stage A cell, emit one of four states: `computed`, `paper_reported`, `requires_adapter`, or `not_applicable`.
4. Compare numeric cells only when the same benchmark family, data split, and required labels are present. Otherwise, report the applicability state as part of the result.

This keeps the paper claim defensible: KMUC can be shown against prior work's own tasks where portable, while SDE-Bench explains the common medical synthetic-data profile across heterogeneous datasets.

## Source Notes

- MedSynth original benchmark: https://arxiv.org/abs/2508.01401
- SimSUM original benchmark: https://arxiv.org/abs/2409.08936
- Synthea generator/sample page: https://synthetichealth.github.io/synthea/
- Synthea JAMIA paper: https://academic.oup.com/jamia/article/25/3/230/4098271
- Health Gym ART for HIV dataset: https://doi.org/10.6084/m9.figshare.22827878.v1
- Health Gym Scientific Data paper: https://www.nature.com/articles/s41597-022-01784-7
- CMS DE-SynPUF downloads: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files

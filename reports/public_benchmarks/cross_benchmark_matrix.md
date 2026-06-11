# Cross-Benchmark Evaluation Matrix

This report separates two evaluation layers that should both appear in the paper:

1. **Original-benchmark layer**: treat each dataset paper's own evaluation protocol as a benchmark family, then test KMUC and the other public datasets against those protocols when the required fields exist.
2. **SDE-Bench layer**: run every public synthetic medical dataset through the same SDE-Bench axes.

The first layer is stronger for publication because it avoids evaluating prior work only with our proposed metrics. The second layer then explains the common medical synthetic-data profile across heterogeneous dataset types.

## Stage Definitions

| Stage | Question | Rows | Columns |
|---|---|---|---|
| Stage A | How do KMUC and public datasets perform under each prior dataset's original benchmark? | Original benchmark families | KMUC plus public synthetic datasets |
| Stage B | How do all datasets compare under SDE-Bench? | Datasets | SDE-Bench axes and available-axis mean score |

`Overall` is an available-axis mean. It is a compact summary for sorting, not a superiority claim, because unavailable axes are excluded rather than penalized.

## Original Benchmark Families

| Benchmark Family | Origin Dataset | Native Task | Core Metric | Formula / Rule | Required Inputs | Portability |
|---|---|---|---|---|---|---|
| `kmuc_matching` | KMUC synthetic lay cases | Patient lay text to department/doctor retrieval | dept_top1, dept_hit@5, mrr_dept, proc_coverage@5, icd_coverage@5 | dept_top1 = correct_top1 / N; hit@5 = any_correct_in_top5 / N; MRR = mean(1 / rank_expected_dept) | lay/patient text, expected department, candidate doctor/procedure/ICD index | Portable only when department labels and the same doctor/procedure index are available. |
| `medsynth_dial_note` | MedSynth | Dial-2-Note and Note-2-Dial fine-tuning on Aci-Bench | LLM jury preference rate; optional BLEU/ROUGE/METEOR | win_rate = preferred_outputs / judged_outputs; text metrics use standard BLEU/ROUGE/METEOR against target notes/dialogues | paired dialogue and note, trainable generation model, Aci-Bench train/test, LLM judges | Expensive and task-specific; not directly applicable to datasets without dialogue-note pairs. |
| `simsum_symptom_ie` | SimSUM | Symptom extraction from clinical notes | F1 for dyspnea, cough, pain, nasal, fever; macro F1 for fever | F1_symptom = 2 * precision * recall / (precision + recall); macro_f1 = mean(F1_dyspnea, F1_cough, F1_pain, F1_nasal, F1_fever) | note text plus five respiratory symptom labels or spans | Portable to respiratory datasets with symptom labels; otherwise requires label projection or manual annotation. |
| `synthea_structured_ehr` | Synthea | Structured synthetic EHR generation and standards-based interoperability | Public scale and standards-based EHR availability | paper-reported availability of synthetic patients encoded in HL7 FHIR/C-CDA plus FHIR API access | patient, encounter, condition, procedure, drug, observation tables or equivalent FHIR/OMOP fields | Portable to structured EHR/claims datasets; not applicable to pure text datasets. |
| `healthgym_longitudinal_realism` | HealthGymART | Longitudinal synthetic health data for offline reinforcement learning | Distributional, correlation, temporal-trend, and disclosure-risk similarity to source cohorts | paper-reported realism: synthetic distributions, correlations, and time trends mirror real datasets; disclosure risk estimated low | longitudinal patient trajectories with variables, time index, actions/treatments, and source-real cohort comparison | Portable to longitudinal treatment-policy datasets with real-source trajectories and privacy-risk evaluation. |
| `desynpuf_claims_public_use` | DE-SynPUF | Synthetic Medicare claims public-use file for software development and training | CMS-reported claims-format compatibility and public-use purpose | paper/agency-reported compatibility with CMS Limited Data Set formats and variable names | CMS beneficiary and claims files with SynPUF-compatible structure and data dictionary | Portable to synthetic claims files designed for identical-format software development and analyst training. |

## Stage A: Original-Metric Crosswalk

| Benchmark Family | KMUC | MedSynth | SimSUM | Synthea | HealthGymART | DeSynPUF |
|---|---:|---:|---:|---:|---:|---:|
| `kmuc_matching` | `computed`: `dept_top1=0.7467`, `dept_hit@5=0.8800`, `mrr_dept=0.7943`, `proc_coverage@5=0.5889`, `icd_coverage@5=0.5931` | `not_applicable` (no expected department or doctor index) | `not_applicable` (respiratory symptoms only, no department labels) | `not_applicable` (structured EHR lacks KMUC doctor/procedure retrieval labels) | `not_applicable` (no expected department or doctor index) | `not_applicable` (claims tables lack KMUC doctor/procedure retrieval labels) |
| `medsynth_dial_note` | `requires_adapter` | `paper_reported`: Dial-2-Note `60.0%/95.0%/52.5%`; Note-2-Dial `55.0%/87.5%/80.0%` jury preference | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) | `not_applicable` (no dialogue-note pairs) |
| `simsum_symptom_ie` | `requires_labels` | `not_applicable` (no gold dyspnea/cough/pain/nasal/fever labels) | `paper_reported`: normal F1 dyspnea `0.9617`, cough `0.9603`, pain `0.8143`, nasal `0.9628`, fever `0.9096`; compact F1 dyspnea `0.9444`, cough `0.9397`, pain `0.7940`, nasal `0.9622`, fever `0.9010` | `requires_adapter`: derive respiratory symptoms from Synthea conditions/observations | `not_applicable` (longitudinal HIV ART data lacks respiratory symptom labels) | `not_applicable` (claims data lacks respiratory symptom labels) |
| `synthea_structured_ehr` | `not_applicable` | `not_applicable` (text pair dataset) | `not_applicable` (single-encounter tabular/text benchmark) | `paper_reported`: JAMIA paper reports one million synthetic patient records freely available in standard formats including HL7 FHIR and C-CDA, with FHIR API access. | `sde_proxy`: `medical_interoperability=0.9583` | `sde_proxy`: `medical_interoperability=0.9165` |
| `healthgym_longitudinal_realism` | `not_applicable` | `not_applicable` (no longitudinal treatment-policy trajectories) | `not_applicable` (no longitudinal treatment-policy trajectories) | `not_applicable` (generated EHR records, not Health Gym source-cohort GAN evaluation) | `paper_reported`: Health Gym paper reports synthetic distributions, correlations, and temporal trends mirror real datasets, with very low disclosure risk. | `not_applicable` (claims tables are not longitudinal treatment-policy trajectories) |
| `desynpuf_claims_public_use` | `not_applicable` | `not_applicable` (dialogue-note text dataset) | `not_applicable` (respiratory note/label dataset) | `not_applicable` (EHR generator, not CMS claims SynPUF) | `not_applicable` (longitudinal ART data, not CMS claims SynPUF) | `paper_reported`: CMS reports SynPUFs use formats and variable names similar to CMS Limited Data Sets so programs created on SynPUFs function on CMS Limited Data Sets, while inferential research value is limited. |

## Stage B: SDE-Bench Cross-Dataset Results

| Dataset | Overall | Fidelity | Utility | Privacy | Equity | Diversity | Scope | Groundedness | Validity | Interoperability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KMUC | `0.8143` | `1.0000` | `0.7467` | `0.5000` | `0.8474` | `1.0000` | `0.9770` | `0.5028` | `0.9408` | `n/a` |
| MedSynth | `0.6448` | `0.2289` | `n/a` | `0.7249` | `n/a` | `0.7198` | `0.3827` | `0.8128` | `1.0000` | `n/a` |
| SimSUM | `0.6524` | `0.9531` | `n/a` | `0.1340` | `n/a` | `0.7648` | `0.2086` | `0.8540` | `1.0000` | `n/a` |
| Synthea | `0.7818` | `0.3033` | `n/a` | `0.7521` | `0.7254` | `0.8123` | `0.6652` | `1.0000` | `0.9962` | `1.0000` |
| HealthGymART | `0.8369` | `0.9537` | `n/a` | `0.5929` | `0.9987` | `0.9660` | `0.2253` | `1.0000` | `1.0000` | `0.9583` |
| DeSynPUF | `0.8557` | `0.5969` | `n/a` | `0.7538` | `0.9201` | `0.9279` | `0.8156` | `1.0000` | `0.9151` | `0.9165` |

## Implementation Roadmap

1. Keep each original paper protocol as a versioned benchmark family with explicit formula, required inputs, and applicability rules.
2. Add executable dataset-to-original-benchmark adapters for cells currently marked `requires_adapter` or `requires_labels`.
3. For each Stage A cell, emit one of five states: `computed`, `paper_reported`, `sde_proxy`, `requires_adapter`, or `not_applicable`. Treat `sde_proxy` as a compatibility proxy, not an original paper metric.
4. Compare numeric cells only when the same benchmark family, data split, and required labels are present. Otherwise, report the applicability state as part of the result.

This keeps the paper claim defensible: KMUC can be shown against prior work's own tasks where portable, while SDE-Bench explains the common medical synthetic-data profile across heterogeneous datasets.

## Publication Readiness Gate

Family-level status: `ready_for_family_level_equivalence`.
Cross-application status: `not_ready_for_full_cross_application`.
Independent recomputation status: `not_ready_for_independent_recomputation`.

The matrix is ready to support a family-level paper-equivalent benchmark claim: each prior benchmark family has origin-dataset evidence that is either computed or faithfully paper-reported. This is native-protocol evidence, not an independent reproduction claim. Full cross-application across incompatible dataset types remains a separate, not-yet-ready claim.

| Gate | Status | Evidence |
|---|---|---|
| Versioned original protocols | `pass` | Every benchmark family has formula, required inputs, and applicability rules. |
| Executable original metric | `pass` | 6 paper-equivalent cells are available. |
| Prior-paper baseline evidence | `pass` | 5 paper-reported cells are preserved separately from 1 recomputed cell. |
| Proxy separation | `pass` | 2 SDE-derived proxy cells are excluded from paper-equivalent evidence. |
| Adapter completeness | `fail` | 3 cells still require adapters or labels. |
| Family-level origin evidence | `pass` | 6 of 6 benchmark families have origin-dataset paper-equivalent evidence. |
| Independent origin recomputation | `fail` | 1 of 6 benchmark families has recomputed origin-dataset evidence. |

SDE-derived proxy cells are not counted as original-paper evidence. They can support interoperability compatibility claims, but not a full paper-equivalent benchmark claim.

### Blocking Cells

| Benchmark Family | Dataset | Status | Blocks | Next Action |
|---|---|---|---|---|
| `medsynth_dial_note` | KMUC | `requires_adapter` | full_equivalence | Build a dialogue-note adapter and run the Dial-2-Note/Note-2-Dial task or an explicitly labeled non-equivalent text-metric screen. |
| `simsum_symptom_ie` | KMUC | `requires_labels` | full_equivalence | Add dyspnea/cough/pain/nasal/fever labels or clinician-reviewed label projection before computing symptom F1. |
| `simsum_symptom_ie` | Synthea | `requires_adapter` | full_equivalence | Derive respiratory symptom labels from structured conditions/observations and validate the projection before computing F1. |

### Supplemental Proxy Cells

| Benchmark Family | Dataset | Status | Role | Next Action |
|---|---|---|---|---|
| `synthea_structured_ehr` | HealthGymART | `sde_proxy` | not_paper_equivalent | Replace the SDE proxy with the original paper's metric or cite a faithful paper-reported baseline. |
| `synthea_structured_ehr` | DeSynPUF | `sde_proxy` | not_paper_equivalent | Replace the SDE proxy with the original paper's metric or cite a faithful paper-reported baseline. |

## Source Notes

- MedSynth original benchmark: https://arxiv.org/abs/2508.01401
- SimSUM original benchmark: https://arxiv.org/abs/2409.08936
- Synthea generator/sample page: https://synthetichealth.github.io/synthea/
- Synthea JAMIA paper: https://academic.oup.com/jamia/article/25/3/230/4098271
- Synthea DOI: https://doi.org/10.1093/jamia/ocx079
- Health Gym ART for HIV dataset: https://doi.org/10.6084/m9.figshare.22827878.v1
- Health Gym arXiv paper: https://arxiv.org/abs/2203.06369
- Health Gym Scientific Data paper: https://www.nature.com/articles/s41597-022-01784-7
- CMS DE-SynPUF downloads: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files

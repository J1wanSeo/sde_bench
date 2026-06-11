# SDE-Bench Improvement Directions

## 1. Why Diversity Is Not Generalizability

`medical_diversity` measures whether synthetic records preserve the reference
support and avoid repetition. It answers: "within this dataset's declared
population, are categories covered and records non-collapsed?"

It does not answer: "is this dataset broadly reusable across medical
departments, diagnoses, procedures, scenarios, and downstream tasks?"

This distinction matters because a narrow disease-specific dataset can be
internally diverse and still not be a general-purpose synthetic medical
dataset.

## 2. Why HealthGymART Scores High Without Being Broad

HealthGymART is a strong longitudinal HIV/ART synthetic dataset. It has stable
monthly records, patient-time structure, source-like evidence fields, and
standardized temporal identifiers. Those properties produce high scores for
fidelity, diversity, groundedness, validity, and interoperability.

Its clinical scope is narrow: one disease family, no department labels, no broad
procedure vocabulary, and no multi-specialty patient-intent task. The
`clinical_scope_generalizability` axis makes that limitation visible while still
preserving its strength as a structured longitudinal benchmark.

## 3. Current Score Pattern

After adding `clinical_scope_generalizability`, the current Stage B SDE-Bench
scores show the intended separation:

| Dataset | Overall | Scope | Main Interpretation |
|---|---:|---:|---|
| KMUC | `0.8302` | `0.9770` | Broad multi-specialty synthetic patient cases, but lexical grounding and privacy distance remain weak. |
| HealthGymART | `0.8550` | `0.2253` | Strong narrow longitudinal HIV/ART structure, not broad clinical scope. |
| DeSynPUF | `0.8744` | `0.8156` | Broad claims diagnosis/procedure coverage, strong structured claims baseline. |
| Synthea | `0.8050` | `0.6652` | Broad EHR structure and interoperability, but no department/scenario labels in this export. |
| MedSynth | `0.6956` | `0.3827` | Broad diagnoses in dialogue-note pairs, but weak department/procedure/scenario scope. |
| SimSUM | `0.7021` | `0.2086` | Strong respiratory-specific benchmark, intentionally narrow. |

## 4. How To Improve KMUC Fairly

1. Improve `clinical_groundedness`.
   - Current support uses lexical token overlap.
   - Korean lay text and mixed Korean/English abbreviated EMR notes are
     under-scored.
   - Add Korean medical synonym normalization, abbreviation expansion, and a
     semantic evidence checker using embedding similarity or clinician/LLM
     entailment labels.

2. Reframe privacy for source-linked transformations.
   - KMUC lay cases intentionally preserve department, diagnosis, and procedure
     labels from source cases.
   - Current nearest-reference distance therefore penalizes clinically faithful
     source-linked transformation.
   - Report two privacy views: transformation privacy for source-linked lay
     variants, and de novo privacy for independently generated synthetic cases.

3. Add structured interoperability fields.
   - Export `patient_id`, `encounter_id`, `condition_start`, `procedure_date`,
     `omop_domains`, and `standard_vocabularies` where the source case supports
     them.
   - This should make KMUC comparable to Synthea/DE-SynPUF on structured-readiness
     without pretending the dataset is longitudinal EHR.

4. Keep Stage A original metrics explicit.
   - KMUC should continue to report `dept_top1`, `dept_hit@5`, `mrr_dept`,
     `proc_coverage@5`, and `icd_coverage@5`.
   - These original task metrics show the intended patient-to-care matching
     utility better than the generic SDE-Bench scalar.

5. Do not optimize only for `overall_score`.
   - The paper claim should be axis-based: KMUC is broad and task-oriented;
     HealthGymART is narrow and longitudinal; Synthea/DE-SynPUF are structured
     EHR/claims baselines.
   - A single scalar should be treated as a table-sorting aid, not the proof of
     superiority.

## 5. Recommended Paper Claim

SDE-Bench distinguishes two properties often mixed together in prior synthetic
health-data evaluation: internal distribution quality and clinical scope
generalizability. HealthGymART demonstrates high-quality narrow longitudinal
generation, while KMUC demonstrates broad multi-specialty patient-facing
coverage and matching-task utility. Adding semantic grounding and structured
interoperability exports should make KMUC's intended contribution measurable
without relying on a metric that simply rewards one data format.

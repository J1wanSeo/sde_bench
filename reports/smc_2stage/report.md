# SDE-Bench Report — SMC 2-stage (doctor → structured case → lay query)

dataset: structured cases `layer3_datasets/patient_dataset/parsed/smc_cases.v1.jsonl` (1,170)
         + lay queries `layer4_labeled_jsonl/smc_eval_cases.v1.jsonl` (1,170)
config: full_eval (all 9 axes). Structured middle layer added KMUC-style, so clinical
axes (validity/scope/equity) are now applicable instead of n/a.

## 1-stage vs 2-stage profile

| Axis | 1-stage (lay only) | 2-stage (＋structured case) |
|---|---|---|
| medical_fidelity | 0.980 | **1.000** |
| clinical_task_utility | n/a | n/a (needs matching predictions/embedding) |
| privacy | 0.500 | 0.500 |
| equity | (n/a) | **1.000** |
| medical_diversity | 0.860 | **1.000** |
| clinical_scope_breadth | 0.438 | **0.984** |
| clinical_groundedness | 0.508 | 0.500 |
| clinical_validity | (n/a) | **0.940** |
| medical_interoperability | n/a | n/a |
| **overall** | 0.657 | **0.846** |

## What the middle layer unlocked
- scope_breadth 0.44→0.98: diagnosis_unique 0→**21**, procedure_unique 0→**502**, demographic 0→**0.91** (age 5 bins, sex 2).
- clinical_validity now real **0.94**: icd10 format 1.0, acuity 1.0, laterality 1.0, age 1.0, dept_consistency 1.0 (procedure_completeness 0.52 = some cases have no procedure by design).
- equity 1.0 (sex balance), fidelity 1.0, diversity 1.0.

## Honest caveats (unchanged structural limits)
- **clinical_task_utility still n/a** — no predicted_* labels. Real matching utility (Top-k/MRR) needs SMC embedding → eval_v2 (separate step).
- **fidelity 1.0 is internal consistency**, not realism vs real EMR: structured cases are LLM-inferred (haiku) from lay+doctor focus, and lay rows inherit the structured fields (same shape as KMUC). It does not prove the cases match real Samsung EMR.
- **groundedness evidence_support ≈ 0 (→0.5 axis)**: lexical Korean-lay vs English-dx mismatch (risk_register #5); attribution 1.0. Needs semantic scorer.
- **privacy 0.5 low-signal** for this generated set; content dedup already enforced (0 exact dup, 0 jargon in lay).

## Net
Adding the KMUC-style structured middle layer turns SMC from a thin lay-query set
(overall 0.657, many n/a) into a structured case-plus-lay-query dataset
(available-axis mean **0.846**). This supports field-available, axis-level
comparison to KMUC and public structured benchmarks, not a full equivalence
claim: utility, semantic groundedness, privacy attack resistance, and
interoperability still require separate evidence.

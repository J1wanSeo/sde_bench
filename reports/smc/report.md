# SDE-Bench Report — SMC (Samsung) lay-query matching dataset

dataset: `layer4_labeled_jsonl/smc_eval_cases.v1.jsonl` (1,170 lay queries, 390 doctors, 23 depts)
reference pool: 406 SMC doctor profiles
config: smc_layquery (axes applicable to a lay-query matching set)
note: validity / equity / interoperability axes EXCLUDED — a lay patient-query set
has no structured EHR fields (age/dx/icd/vitals), so those axes are not applicable
(after the utility/validity hardening, absent fields report n/a rather than inflated 1.0).

## Axis profile

| Axis | Score | Read |
|---|---|---|
| medical_fidelity | 0.980 | query dept distribution mirrors doctor pool (1 shared column: dept) |
| clinical_task_utility | **n/a** | no predicted_* labels → matching Top-k/MRR must be run separately (embedding) |
| privacy | 0.500 | dup 0.0; nearest-ref distance 0.0 (only dept shared → low signal, see caveat) |
| medical_diversity | 0.860 | category_coverage 1.0, entropy_ratio 1.0, unique_record_ratio 0.58* |
| clinical_scope_breadth | 0.438 | dept_scope 1.0 (23 depts) BUT dx/procedure/demographic = 0 (lay text has none) |
| clinical_groundedness | 0.508 | source_attribution 1.0 (every query→gold doctor); evidence_support 0.016 (lexical)* |

overall (available-axis mean): 0.657

## Caveats (data-type, not defects)

1. **Lay-query set ≠ structured EHR.** diagnosis/procedure/age/sex absent by design →
   scope_breadth dx/procedure/demographic = 0, and validity/interop excluded. This is the
   dataset TYPE, not a quality failure. Compare SMC only against other lay-query/matching sets.
2. **evidence_support = 0.016 is a lexical artifact.** Korean lay queries share almost no
   surface tokens with English/Korean specialty_text, yet are semantically grounded
   (risk_register #5). Needs semantic/entailment scorer, not lexical overlap.
3. **unique_record_ratio 0.58** is a fingerprint artifact: SDE-Bench fingerprint excludes the
   `claim` (query) text, so 3 queries per doctor look like near-duplicates structurally.
   Actual content uniqueness = **100% (1,170 distinct queries, 0 exact dup, verified)**.
4. **privacy 0.5 low-signal**: only `dept` is shared with the reference pool, so nearest-
   reference distance collapses. Memorization for this generated set is better screened by
   the content-level dedup already applied (0 exact, 0 jargon).

## What IS validated for SMC
- Full department coverage (23/23 in pool), perfectly balanced ambiguity (390/390/390).
- 100% source attribution to gold doctors (groundedness provenance).
- High dept-distribution fidelity to the doctor pool (0.98).
- 100% content-unique, jargon-free queries.

## Next (to fill clinical_task_utility)
Embed SMC specialty_text with models/H_kurev1_real_synth_v3 → run eval_v2 matching →
Top-1/Hit@5/MRR; compare to Anam (0.633 / 0.913 / 0.734) for 2-hospital portability.

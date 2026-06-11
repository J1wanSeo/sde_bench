# Peer Review Risk Register

This register lists the main critiques a medical informatics reviewer could
raise and the corresponding mitigation in SDE-Bench.

## 1. "Overall score is not a valid superiority claim."

Risk: The overall score averages only available axes. Datasets without
interoperability or equity fields are not penalized for those missing axes, so
overall scores are not strictly comparable as a single scalar.

Mitigation:

- Label `overall_score` as an available-axis mean.
- Make the paper claim from axis-level profiles, not from the scalar rank.
- Report skipped axes and raw metrics beside every score.

## 2. "Scope breadth is not true generalizability."

Risk: Breadth across departments, diagnoses, procedures, demographics, scenarios,
and task signals is only a structural scope measure. It does not prove external
hospital transfer or out-of-distribution model performance.

Mitigation:

- Use `clinical_scope_breadth`, not `clinical_scope_generalizability`.
- Reserve "generalizability" for future external-site or external-task
validation.
- Interpret KMUC's high score as broad coverage, not as proven transfer.

## 3. "HealthGymART is narrow but still scores high."

Risk: A narrow HIV/ART longitudinal dataset can score high on fidelity,
diversity, groundedness, validity, and interoperability because it is internally
well structured.

Mitigation:

- Keep those high scores because they reflect real strengths.
- Use `clinical_scope_breadth` to show that it is narrow in medical scope.
- Claim complementarity: HealthGymART is a strong narrow longitudinal baseline;
KMUC is broad and patient-facing.

## 4. "Stage A mixes original paper metrics and SDE-Bench-derived proxies."

Risk: Synthea's structured-EHR row does not correspond to a single numeric
original-paper benchmark metric in the same way as KMUC matching, MedSynth jury
preference, or SimSUM symptom F1.

Mitigation:

- Mark SDE-derived compatibility values as `sde_proxy`.
- Treat `sde_proxy` cells as interoperability proxies, not original paper
metrics.
- Avoid comparing `sde_proxy` cells as if they were paper-reported results.

## 5. "Groundedness underestimates Korean lay-to-EMR semantic support."

Risk: Current groundedness uses lexical token overlap. Korean lay descriptions
and mixed Korean/English EMR abbreviations can be semantically faithful while
scoring low.

Mitigation:

- Report current groundedness as a lexical screen.
- Add Korean medical synonym normalization, abbreviation expansion, and semantic
evidence scoring before claiming strong factual grounding.
- Consider clinician review or blinded LLM entailment as a validation layer.

## 6. "Privacy metric penalizes source-linked transformations."

Risk: KMUC lay cases intentionally preserve structured clinical facts from source
cases. Nearest-reference distance therefore becomes low, which can look like
privacy weakness even when the intended task is source-grounded transformation.

Mitigation:

- Report source-linked transformation privacy separately from de novo synthetic
privacy.
- Add membership inference and attribute disclosure tests for de novo variants.
- Do not use nearest-reference distance alone as a privacy guarantee.

## 7. "Public baselines are heterogeneous."

Risk: MedSynth, SimSUM, Synthea, HealthGymART, DE-SynPUF, and KMUC differ in
format, target task, and source-reference semantics. One universal table can
hide non-comparability.

Mitigation:

- Keep Stage A applicability states explicit.
- Use Stage B as a common-axis profile, not as a claim that all datasets solve
the same problem.
- Report domain, native format, target, sensitive columns, and skipped axes for
each dataset.

## 8. "This is not yet equivalent to every prior paper's own benchmark."

Risk: A reviewer can argue that Stage A is a crosswalk rather than a full
paper-equivalent benchmark matrix because some cells are `requires_adapter`,
`requires_labels`, or `sde_proxy`.

Mitigation:

- Add a publication-readiness gate to the generated cross-benchmark report.
- Count only `computed` and `paper_reported` cells as paper-equivalent evidence.
- State that the current package is an executable profile plus original-metric
crosswalk until adapter and label gaps are closed.

## Recommended Reviewer-Safe Claim

SDE-Bench provides a structured axis-level profile and original-metric crosswalk
for heterogeneous synthetic medical datasets. It does not prove that one dataset
is universally superior. In the current evidence, KMUC is strongest on clinical
scope breadth and patient-facing department-matching utility, while structured
public baselines remain stronger on longitudinal or interoperability-oriented
axes. Full paper-equivalent benchmark claims should be limited to cells marked
`computed` or `paper_reported`.

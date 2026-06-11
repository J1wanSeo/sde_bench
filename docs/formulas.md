# Metric Formulas

Notation:

- `R`: reference records.
- `S`: synthetic records.
- `C`: compared columns after excluding identifiers and provenance columns.
- `mean(...)`: arithmetic mean over available numeric metric values, clipped to
  `[0, 1]`.
- `TVD(P, Q) = 0.5 * sum_x |P(x) - Q(x)|`.

## 1. Medical Fidelity

For each common column `c`:

- Numeric column: `column_similarity(c) = 1 - KS(R_c, S_c)`.
- Categorical column: `column_similarity(c) = 1 - TVD(R_c, S_c)`.

For each categorical column pair `(a, b)` among the first eight categorical
columns:

- `pairwise_similarity(a,b) = 1 - TVD(R_{a,b}, S_{a,b})`.

Axis score:

```text
medical_fidelity = mean(column_similarity, pairwise_similarity)
```

Interpretation: high score means the synthetic dataset preserves marginal and
simple pairwise structure in the compared medical fields. It does not prove that
clinical prose is realistic.

## 2. Clinical Task Utility

When `expected_<target>` and `predicted_<target>` fields exist:

```text
label_accuracy = count(expected == predicted) / count(expected and predicted present)
label_support = count(expected and predicted present)
target_population_rate = count(target present) / count(S)
clinical_task_utility = label_accuracy   # n/a when predicted_* labels are absent
```

Interpretation: utility is the downstream task accuracy. `target_population_rate`
(mere presence of a target column) is reported as a metric but does NOT count
toward the score; without `predicted_*` labels the axis is reported as `n/a`,
not a high score. In retrieval or matching studies, papers should also report
native task metrics such as hit@k, MRR, AUROC, or F1.

## 3. Privacy

For every synthetic record, SDE-Bench builds a fingerprint after removing id,
source, claim, evidence, expected label, and predicted label columns.

```text
exact_duplicate_rate = count(fingerprint(s) in fingerprints(R)) / count(S)
mixed_distance(s, r) = mean per-column normalized numeric distance or categorical mismatch
median_distance_to_reference = median_s min_r mixed_distance(s, r)
privacy = ((1 - exact_duplicate_rate) + median_distance_to_reference) / 2
```

For large datasets, `median_distance_to_reference` is computed on a deterministic
stride sample controlled by `privacy_distance_sample_size` in the evaluation
config. `exact_duplicate_rate` is still computed over all synthetic records.
Reports include `distance_sampled`, `distance_synthetic_records`, and
`distance_reference_records` so the sampling scope is explicit.

Interpretation: high score means less exact copying and larger nearest-reference
distance. This is a lightweight screen, not a replacement for membership
inference or attribute disclosure attacks.

## 4. Equity

For each sensitive column `g`:

```text
sensitive_distribution_similarity(g) = 1 - TVD(R_g, S_g)
```

For target parity:

```text
group_target_parity = mean_{group pairs} (1 - TVD(S_target | group_i, S_target | group_j))
equity = mean(sensitive_distribution_similarity, group_target_parity)
```

Interpretation: high score means the synthetic dataset preserves demographic
composition and avoids large target-distribution shifts between groups. It does
not prove clinical fairness by itself.

## 5. Medical Diversity

For categorical columns:

```text
category_coverage(c) = |unique(R_c) intersect unique(S_c)| / |unique(R_c)|
entropy_ratio(c) = min(H(S_c) / H(R_c), 1)
unique_record_ratio = count(unique fingerprints in S) / count(S)
medical_diversity = mean(category_coverage, entropy_ratio, unique_record_ratio)
```

Interpretation: high score means the synthetic set covers the reference support
without collapsing to repeated records.

## 6. Clinical Scope Breadth

For a set of values `V` and a target breadth cap `K`:

```text
unique_scope(V, K) = min(count(unique(V)) / K, 1)
entropy_scope(V, K) = H(V) / log2(min(K, count(unique(V))))
absolute_scope(V, K) = mean(unique_scope(V, K), entropy_scope(V, K))
```

SDE-Bench computes:

```text
department_scope = absolute_scope(dept or specialty labels, 8)
diagnosis_scope = absolute_scope(diagnosis_group or ICD chapter/group labels, 12)
procedure_scope = absolute_scope(procedure labels, 8)
demographic_scope = mean(absolute_scope(age bins, 5),
                         absolute_scope(sex/gender labels, 2))
scenario_scope = absolute_scope(acuity, tone, setting, visit type,
                                scenario, or chronic-condition signals, 6)
task_scope = absolute_scope(available task signals, 4)
clinical_scope_breadth = mean(department_scope,
                                       diagnosis_scope,
                                       procedure_scope,
                                       demographic_scope,
                                       scenario_scope,
                                       task_scope)
```

Interpretation: high score means the synthetic dataset is broad across clinical
departments, diagnoses, procedures, demographics, scenarios, and reusable task
signals. This is different from `medical_diversity`: a narrow HIV longitudinal
dataset can be internally diverse while still scoring low on clinical scope.

## 7. Clinical Groundedness

```text
source_attribution_rate = count(source_id present and valid) / count(S)
evidence_support_score = mean_s |tokens(claim_s) intersect tokens(evidence_s)| / |tokens(claim_s)|
clinical_groundedness = mean(source_attribution_rate, evidence_support_score)
```

Interpretation: high score means generated claims are traceable to source
records and lexically supported by evidence. Current support is token-based; a
semantic evidence checker is a planned extension.

## 8. Clinical Validity

```text
age_validity = count(0 <= age <= 120) / count(S)
non_empty_diagnosis_rate = count(diagnosis present) / count(S)
icd10_format_validity = count(all ICD-10-like codes valid) / count(rows with codes)
icd9_format_validity = count(all ICD-9-like codes valid) / count(rows with codes)
procedure_completeness = count(procedures present) / count(rows with procedure field)
acuity_validity = count(acuity in allowed vocabulary) / count(rows with acuity)
laterality_validity = count(laterality in allowed vocabulary) / count(rows with laterality)
dept_consistency = count(dept or expected_dept matches source dept) / count(source-linked rows with source dept)
diagnosis_source_overlap = mean token overlap between synthetic diagnosis and source diagnosis
clinical_validity = mean(available metrics above)   # absent fields = n/a, NOT 1.0
```

Interpretation: high score means basic medical fields are structurally coherent
and source-consistent. Checks for fields a dataset does not expose return `n/a`
(not 1.0), so sparse datasets are not rewarded for having nothing to violate.
Specialty-specific clinical rule packs should be added for stronger claims.

## 9. Medical Interoperability

Let `D_core = {person, visit_occurrence, condition_occurrence,
procedure_occurrence, drug_exposure, measurement}`.

```text
omop_domain_coverage = |declared omop_domains intersect D_core| / |D_core|
standard_vocabulary_rate = count(records with only standard vocabularies) /
                            count(records with declared vocabularies)
temporal_traceability = count(records with valid event date) /
                        count(records with event date fields)
relational_integrity = count(records with case_id and encounter/visit/source link) /
                       count(records with relationship fields)
medical_interoperability = mean(omop_domain_coverage,
                                standard_vocabulary_rate,
                                temporal_traceability,
                                relational_integrity)
```

Interpretation: high score means a structured synthetic dataset is easy to map
into OMOP-like observational analytics. This axis is `n/a` for datasets that do
not expose structured interoperability fields; `n/a` is excluded from the
overall score.

## Overall Score

```text
overall_score = mean(axis scores enabled by the preset)
```

Interpretation: the overall score is a ranking convenience. Scientific claims
should be made from the axis scores and raw metrics.

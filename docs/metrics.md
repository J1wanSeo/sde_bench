# Metrics

SDE-Bench reports a seven-axis medical synthetic-data profile. Each axis exposes
raw metrics and a bounded `score` in `[0, 1]`. The score is intended for quick
comparison; papers should report the raw metrics as well.

## Medical Benchmark Axes

### Medical Fidelity

Measures how closely synthetic records resemble the reference distribution.

- `column_similarity`: mean per-column similarity. Numeric columns use
  `1 - KS distance`; categorical columns use `1 - total variation distance`.
- `pairwise_similarity`: mean pairwise categorical relation similarity.
- `columns_compared`, `pairs_compared`: support counts, not included in score.

### Clinical Task Utility

Measures clinical task usefulness when task labels are available.

- `label_accuracy`: agreement between `expected_*` and `predicted_*` fields.
- `target_population_rate`: fraction of synthetic records with a non-empty
  target field.
- `label_support`: support count, not included in score.

Future modules should add TSTR/TRTR, AUROC/F1 gap, or task-specific retrieval
metrics when real holdout labels are available.

### Privacy

Measures simple memorization risk without requiring attack models.

- `exact_duplicate_rate`: exact synthetic/reference duplicates after excluding
  id/provenance fields.
- `median_distance_to_reference`: median mixed-type nearest-reference distance.
- `records_compared`: support count.

Future modules should add membership inference and attribute disclosure risk.

### Equity

Measures whether sensitive group distributions are preserved.

- `sensitive_distribution_similarity`: similarity for sensitive columns.
- `group_target_parity`: target distribution parity across sensitive groups
  when enough groups exist.

### Medical Diversity

Measures whether synthetic records cover the reference support and avoid
degenerate repetition.

- `category_coverage`: coverage of reference categorical values.
- `entropy_ratio`: synthetic/reference entropy ratio.
- `unique_record_ratio`: fraction of unique synthetic record fingerprints.

### Clinical Groundedness

Designed for LLM/RAG synthetic datasets.

- `source_attribution_rate`: fraction of synthetic records with valid source
  attribution.
- `evidence_support_score`: token-level support of `claim` by `evidence`.
- `evidence_support_n`: support count.

### Clinical Validity

Designed for clinical case and EHR-like datasets.

- `age_validity`: if `age` exists, values must be in `[0, 120]`.
- `non_empty_diagnosis_rate`: non-empty `diagnosis` field rate.
- `icd10_format_validity`: all provided ICD-10 codes match the ICD-10 code
  shape.
- `procedure_completeness`: non-empty procedure field rate when the field is
  present.
- `acuity_validity`: acuity belongs to the accepted emergency/elective/routine
  vocabulary.
- `laterality_validity`: laterality belongs to the accepted side vocabulary.
- `dept_consistency`: synthetic department agrees with source department.
- `diagnosis_source_overlap`: token overlap between generated and source
  diagnosis fields.

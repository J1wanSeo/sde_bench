# KMUC Synthetic Lay Dataset Interpretation

Command:

```bash
PYTHONPATH=src python3 -m sde_bench kmuc-export \
  --repo-root .. \
  --predictions ../layer3_datasets/patient_dataset/eval/H_kurev1_real_synth_v3.json \
  --out-dir reports/kmuc_export \
  --format jsonl

PYTHONPATH=src python3 -m sde_bench evaluate \
  --real reports/kmuc_export/reference.jsonl \
  --synthetic reports/kmuc_export/synthetic_lay.jsonl \
  --source reports/kmuc_export/source.jsonl \
  --target dept \
  --sensitive sex \
  --json-out reports/kmuc_sde_report.json \
  --md-out reports/kmuc_sde_report.md
```

Input size:

- Reference records: 150
- Source records: 150
- Synthetic lay records: 750
- Utility-labeled records with predictions: 150

## Result

| Axis | Score | Meaning |
|---|---:|---|
| `medical_fidelity` | 1.0000 | Structured fields copied through the adapter preserve the reference distribution exactly. This is a structural-field result, not a natural-language realism score. |
| `clinical_task_utility` | 0.7467 | Department matching remains useful: `label_accuracy=0.7467` on 150 predicted lay cases. Target-field presence is reported as metadata, not counted as utility. |
| `privacy` | 0.5000 | No exact duplicate fingerprints were found, but nearest-reference distance is zero because structured fields are retained from source cases. This flags source closeness. |
| `equity` | 0.8474 | Sex distribution is preserved (`1.0000`), while department distribution differs across sex groups (`group_target_parity=0.6949`). |
| `medical_diversity` | 1.0000 | The synthetic set covers the reference categorical support and has unique text records. |
| `clinical_scope_breadth` | 0.9770 | The dataset spans broad departments, diagnosis groups, procedure labels, age/sex groups, scenarios, and task signals. This is the main axis separating KMUC from narrow disease-specific synthetic datasets. |
| `clinical_groundedness` | 0.5028 | Every record has source attribution, but lexical evidence overlap is low (`0.0056`) because Korean lay text is compared against abbreviated mixed-language EMR text. |
| `clinical_validity` | 0.9408 | Age, diagnosis, ICD-10 shape, acuity, laterality, department, and diagnosis-source checks mostly pass; procedure completeness is lower (`0.5267`). |
| `overall_score` | 0.8143 | Mean of the eight available axis scores. Use it only as a compact summary, not as the core scientific claim. |

## Paper-Level Reading

1. The strongest current claim is not "perfect synthetic data"; it is that the
   generated lay dataset is broad in clinical scope, department-task-useful,
   source-attributed, and structurally clinically valid under explicit checks.
2. The weakest current axis is lexical `clinical_groundedness`; this should be
   upgraded with semantic evidence support or clinician review before making
   strong factual-grounding claims.
3. The privacy score should be framed as a lightweight duplicate/nearest-distance
   screen. It is not a membership-inference result.

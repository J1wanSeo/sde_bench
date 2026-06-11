# KMUC Adapter Example

SDE-Bench is intentionally standalone and not tied to KMUC. This page shows how
one local LLM/RAG patient-case dataset can be adapted into the universal schema.
The same pattern should be used for other hospitals or public synthetic medical
datasets.

To evaluate the KMUC synthetic patient case data, export the internal JSONL
files into flat JSONL records with these recommended columns:

| Column | Meaning |
|---|---|
| `case_id` | synthetic case identifier |
| `source_id` | seed/source case identifier |
| `age` | patient age if available |
| `sex` | sensitive/demographic field for equity checks |
| `dept` | generated or expected department |
| `diagnosis` | generated diagnosis |
| `claim` | generated clinical statement to verify |
| `evidence` | retrieved/source passage supporting the claim |
| `expected_dept` | gold department label |
| `predicted_dept` | model or matching pipeline output |

Export KMUC files:

```bash
python3 -m sde_bench kmuc-export \
  --repo-root .. \
  --predictions ../layer3_datasets/patient_dataset/eval/H_kurev1_real_synth_v3.json \
  --out-dir reports/kmuc_export \
  --format jsonl
```

Evaluate the exported dataset:

```bash
python3 -m sde_bench evaluate \
  --real reports/kmuc_export/reference.jsonl \
  --synthetic reports/kmuc_export/synthetic_lay.jsonl \
  --source reports/kmuc_export/source.jsonl \
  --target dept \
  --sensitive sex \
  --json-out reports/kmuc_sde_report.json \
  --md-out reports/kmuc_sde_report.md
```

Recommended paper framing:

1. Report the full seven-axis table.
2. Treat `clinical_groundedness` and `clinical_validity` as the LLM+RAG-specific
   contribution beyond GAN/tabular synthetic EHR benchmarks.
3. Report `clinical_task_utility` using the real downstream matching metrics whenever
   possible: top-1, hit@k, MRR, ICD/procedure coverage.
4. Keep TSTR/TRTR and MIA as future real-holdout modules until TEE-derived real
   validation data exists.

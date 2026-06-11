# KMUC Usage

SDE-Bench is intentionally standalone. To evaluate the KMUC synthetic patient
case data, export the internal JSONL files into flat CSV/JSONL records with
these recommended columns:

| Column | Meaning |
|---|---|
| `case_id` | synthetic case identifier |
| `source_id` | seed/source case identifier |
| `age` | patient age if available |
| `sex` | sensitive/demographic field for fairness checks |
| `dept` | generated or expected department |
| `diagnosis` | generated diagnosis |
| `claim` | generated clinical statement to verify |
| `evidence` | retrieved/source passage supporting the claim |
| `expected_dept` | gold department label |
| `predicted_dept` | model or matching pipeline output |

Recommended first-pass command:

```bash
python3 -m sde_bench evaluate \
  --real exported/reference_cases.csv \
  --synthetic exported/synthetic_cases.csv \
  --source exported/source_cases.csv \
  --target dept \
  --sensitive sex \
  --json-out reports/kmuc_sde_report.json \
  --md-out reports/kmuc_sde_report.md
```

Recommended paper framing:

1. Report the full seven-axis table.
2. Treat `groundedness` and `domain_consistency` as the LLM+RAG-specific
   contribution beyond GAN/tabular synthetic EHR benchmarks.
3. Report `utility` using the real downstream matching metrics whenever
   possible: top-1, hit@k, MRR, ICD/procedure coverage.
4. Keep TSTR/TRTR and MIA as future real-holdout modules until TEE-derived real
   validation data exists.


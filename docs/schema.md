# Universal Medical Record Schema

SDE-Bench is dataset-agnostic. Any synthetic medical dataset can be evaluated
after it is mapped to JSON, JSONL, or CSV records with a shared set of columns.
JSONL is recommended for clinical text.

## Required Inputs

1. `--real`
   - Reference or target-distribution records.
   - This can be a real holdout set, a trusted synthetic reference, or a
     canonical source table depending on the study design.

2. `--synthetic`
   - Synthetic records being evaluated.

## Optional Inputs

3. `--source`
   - Source/provenance records keyed by `source_id`, `case_id`, or `id`.
   - Required for source-attribution and source-consistency checks.

4. `--target`
   - Clinical task column, for example `dept`, `mortality`, `readmission`, or
     `diagnosis_group`.

5. `--sensitive`
   - Comma-separated demographic columns for equity checks, for example
     `sex,age_group,race`.

## Recommended Columns

| Column | Type | Meaning |
|---|---|---|
| `case_id` | string | Record identifier |
| `source_id` | string | Provenance key linking synthetic record to source |
| `age` | number | Patient age |
| `sex` | string | Demographic field for equity checks |
| `age_group` | string | Optional binned age field |
| `dept` | string | Clinical department or service label |
| `diagnosis` | string | Primary diagnosis text |
| `icd10_codes` | string/list | ICD-10 codes, separated by comma/semicolon/pipe if string |
| `procedures` | string/list | Procedures or interventions |
| `clinical_codes` | string/list | Native clinical codes when not limited to ICD-10 |
| `omop_domains` | string/list | OMOP-style domains represented by the record |
| `standard_vocabularies` | string/list | Declared vocabularies such as ICD-10, SNOMED CT, LOINC, RxNorm, CPT, HCPCS |
| `encounter_id` | string | Visit/encounter identifier for relational integrity |
| `encounter_start` | string | Encounter start date, preferably ISO `YYYY-MM-DD` |
| `condition_start` | string | Condition start date, preferably ISO `YYYY-MM-DD` |
| `procedure_date` | string | Procedure date, preferably ISO `YYYY-MM-DD` |
| `acuity` | string | One of `routine`, `elective`, `urgent`, `emergency` |
| `laterality` | string | One of `left`, `right`, `bilateral`, `none`, `midline`, `unknown` |
| `claim` | string | Generated clinical statement or note |
| `evidence` | string | Source passage supporting `claim` |
| `expected_<target>` | string | Gold label for clinical utility |
| `predicted_<target>` | string | Model/pipeline prediction for clinical utility |

## Universal Use

For a new dataset, write a small adapter that maps its native files to this
schema. The benchmark command stays the same:

```bash
python3 -m sde_bench evaluate \
  --real exported/reference.jsonl \
  --synthetic exported/synthetic.jsonl \
  --source exported/source.jsonl \
  --target dept \
  --sensitive sex \
  --json-out reports/dataset_sde_report.json \
  --md-out reports/dataset_sde_report.md
```

Dataset-specific commands such as `kmuc-export` are examples, not the benchmark
interface itself.

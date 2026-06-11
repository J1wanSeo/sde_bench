from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters.kmuc import export_kmuc_records
from .core import benchmark, evaluate
from .io import load_records, load_source, write_json, write_markdown, write_records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sde-bench", description="Synthetic Medical Dataset Effectiveness Benchmark")
    sub = parser.add_subparsers(dest="command", required=True)

    eval_parser = sub.add_parser("evaluate", help="evaluate one synthetic dataset")
    eval_parser.add_argument("--real", required=True, type=Path)
    eval_parser.add_argument("--synthetic", required=True, type=Path)
    eval_parser.add_argument("--source", type=Path, default=None)
    eval_parser.add_argument("--target", default=None)
    eval_parser.add_argument("--sensitive", default="", help="comma-separated sensitive columns")
    eval_parser.add_argument("--preset", default="full_eval", help="preset name or config JSON path")
    eval_parser.add_argument("--json-out", type=Path, default=None)
    eval_parser.add_argument("--md-out", type=Path, default=None)

    bench_parser = sub.add_parser("benchmark", help="rank multiple synthetic datasets from a directory")
    bench_parser.add_argument("--real", required=True, type=Path)
    bench_parser.add_argument("--synthetic-dir", required=True, type=Path)
    bench_parser.add_argument("--source", type=Path, default=None)
    bench_parser.add_argument("--target", default=None)
    bench_parser.add_argument("--sensitive", default="")
    bench_parser.add_argument("--preset", default="full_eval", help="preset name or config JSON path")
    bench_parser.add_argument("--json-out", type=Path, default=None)

    kmuc_parser = sub.add_parser("kmuc-export", help="export KMUC patient-case JSONL files to SDE-Bench records")
    kmuc_parser.add_argument("--repo-root", type=Path, default=Path(".."), help="path to the 2026_kmuc_dataset repository")
    kmuc_parser.add_argument("--enriched", type=Path, default=None, help="KMUC enriched patient cases JSONL")
    kmuc_parser.add_argument("--lay", type=Path, default=None, help="KMUC lay-variant patient cases JSONL")
    kmuc_parser.add_argument("--predictions", type=Path, default=None, help="optional KMUC evaluation JSON with per_case predictions")
    kmuc_parser.add_argument("--out-dir", required=True, type=Path)
    kmuc_parser.add_argument("--format", choices=["jsonl", "json", "csv"], default="jsonl")

    args = parser.parse_args(argv)

    if args.command == "kmuc-export":
        repo_root = args.repo_root
        enriched_path = args.enriched or repo_root / "layer3_datasets/patient_dataset/parsed/patient_cases.v2.enriched.jsonl"
        lay_path = args.lay or repo_root / "layer3_datasets/patient_dataset/parsed/patient_cases.v2.lay.jsonl"
        prediction_rows = _load_kmuc_predictions(args.predictions)
        exported = export_kmuc_records(
            load_records(enriched_path),
            lay_variants=load_records(lay_path) if lay_path.exists() else None,
            per_case_predictions=prediction_rows,
        )
        args.out_dir.mkdir(parents=True, exist_ok=True)
        suffix = f".{args.format}"
        write_records(exported["reference"], args.out_dir / f"reference{suffix}")
        write_records(exported["source"], args.out_dir / f"source{suffix}")
        write_records(exported["synthetic"], args.out_dir / f"synthetic_lay{suffix}")
        print(
            f"exported reference={len(exported['reference'])} source={len(exported['source'])} "
            f"synthetic={len(exported['synthetic'])} to {args.out_dir}"
        )
        return 0

    sensitive_columns = [item.strip() for item in args.sensitive.split(",") if item.strip()]

    if args.command == "evaluate":
        report = evaluate(
            real=load_records(args.real),
            synthetic=load_records(args.synthetic),
            source=load_source(args.source),
            target=args.target,
            sensitive_columns=sensitive_columns or None,
            config=args.preset,
            name=args.synthetic.stem,
        )
        if args.json_out:
            write_json(report, args.json_out)
        if args.md_out:
            write_markdown(report, args.md_out)
        if not args.json_out and not args.md_out:
            from json import dumps

            print(dumps(report, ensure_ascii=False, indent=2))
        return 0

    synthetic_sets = {
        path.stem: load_records(path)
        for path in sorted(args.synthetic_dir.iterdir())
        if path.suffix.lower() in {".csv", ".json", ".jsonl"}
    }
    report = benchmark(
        real=load_records(args.real),
        synthetic_sets=synthetic_sets,
        source=load_source(args.source),
        target=args.target,
        sensitive_columns=sensitive_columns or None,
        config=args.preset,
    )
    if args.json_out:
        write_json(report, args.json_out)
    else:
        from json import dumps

        print(dumps(report, ensure_ascii=False, indent=2))
    return 0


def _load_kmuc_predictions(path: Path | None) -> list[dict]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("per_case"), list):
        return data["per_case"]
    if isinstance(data, list):
        return data
    return []


if __name__ == "__main__":
    raise SystemExit(main())

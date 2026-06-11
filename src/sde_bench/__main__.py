from __future__ import annotations

import argparse
from pathlib import Path

from .core import benchmark, evaluate
from .io import load_records, load_source, write_json, write_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sde-bench", description="Synthetic Dataset Effectiveness Benchmark")
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

    args = parser.parse_args(argv)
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


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""CLI entry point for the control gap analyzer.

Usage:
    python cli.py --catalog data/nist_csf2_catalog.csv \
                   --implementation data/sample_control_implementation.csv \
                   --out-md reports/gap_report.md \
                   --out-csv reports/gap_report.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

from gap_analyzer.catalog import join
from gap_analyzer.scorer import score_all
from gap_analyzer.report import write_markdown_report, write_csv_export


def main() -> None:
    parser = argparse.ArgumentParser(description="NIST CSF 2.0 control gap analyzer")
    parser.add_argument("--catalog", default="data/nist_csf2_catalog.csv")
    parser.add_argument("--implementation", default="data/sample_control_implementation.csv")
    parser.add_argument("--out-md", default="reports/gap_report.md")
    parser.add_argument("--out-csv", default="reports/gap_report.csv")
    parser.add_argument("--framework", default="NIST CSF 2.0")
    args = parser.parse_args()

    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)

    records = join(args.catalog, args.implementation)
    scored = score_all(records)

    write_markdown_report(scored, args.out_md, framework=args.framework)
    write_csv_export(scored, args.out_csv)

    gaps = [s for s in scored if s.priority != "None"]
    critical = [s for s in scored if s.priority == "Critical"]
    print(f"Assessed {len(scored)} controls — {len(gaps)} open gaps ({len(critical)} critical).")
    print(f"Markdown report: {args.out_md}")
    print(f"CSV export:      {args.out_csv}")


if __name__ == "__main__":
    main()

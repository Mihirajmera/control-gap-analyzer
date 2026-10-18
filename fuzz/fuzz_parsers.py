"""Fuzz the implementation-CSV path end to end: load, join with a catalog, score, export.

The implementation file is supplied by users. Malformed input must raise ValueError
(including ImplementationFileError) or csv.Error; any other exception, hang or crash is a bug.
"""
import csv
import sys
import tempfile
from pathlib import Path

import atheris

with atheris.instrument_imports():
    from gap_analyzer.catalog import join
    from gap_analyzer.report import write_csv_export, write_markdown_report
    from gap_analyzer.scorer import score_all

TMP = Path(tempfile.mkdtemp())
CATALOG = TMP / "catalog.csv"
CATALOG.write_text(
    "function,category_id,category_name,subcategory_id,subcategory_description\n"
    "GOVERN,GV.OC,Organizational Context,GV.OC-01,Mission informs risk management\n"
    "PROTECT,PR.AA,Identity Management,PR.AA-01,Identities and credentials are managed\n",
    encoding="utf-8",
)
IMPL = TMP / "impl.csv"


def TestOneInput(data: bytes) -> None:
    IMPL.write_bytes(data)
    try:
        scored = score_all(join(CATALOG, IMPL))
    except (ValueError, csv.Error):
        return
    write_csv_export(scored, TMP / "out.csv")
    write_markdown_report(scored, TMP / "out.md")


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

import csv
from pathlib import Path

from gap_analyzer.catalog import join
from gap_analyzer.report import function_order, write_markdown_report
from gap_analyzer.scorer import score_all

DATA = Path(__file__).resolve().parents[1] / "data"


def _rows(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_ai_rmf_catalog_has_all_72_subcategories():
    rows = _rows("nist_ai_rmf_catalog.csv")
    counts = {fn: sum(r["function"] == fn for r in rows) for fn in ("GOVERN", "MAP", "MEASURE", "MANAGE")}
    assert counts == {"GOVERN": 19, "MAP": 18, "MEASURE": 22, "MANAGE": 13}
    assert len({r["subcategory_id"] for r in rows}) == 72


def test_iso42001_catalog_has_all_38_annex_a_controls():
    rows = _rows("iso42001_annexA_catalog.csv")
    assert len({r["subcategory_id"] for r in rows}) == 38


def test_report_uses_the_frameworks_own_functions(tmp_path):
    scored = score_all(join(DATA / "nist_ai_rmf_catalog.csv", DATA / "sample_ai_rmf_implementation.csv"))
    assert function_order(scored) == ["GOVERN", "MAP", "MEASURE", "MANAGE"]
    out = tmp_path / "r.md"
    write_markdown_report(scored, out, framework="NIST AI RMF 1.0")
    text = out.read_text(encoding="utf-8")
    assert "## Gaps by NIST AI RMF 1.0 Function" in text and "| MEASURE |" in text and "IDENTIFY" not in text


def test_iso_functions_sort_naturally():
    scored = score_all(join(DATA / "iso42001_annexA_catalog.csv", DATA / "sample_iso42001_implementation.csv"))
    order = function_order(scored)
    assert order[0].startswith("A.2") and order[-1].startswith("A.10")


def test_csf_report_still_lists_all_six_functions():
    scored = score_all(join(DATA / "nist_csf2_catalog.csv", DATA / "sample_control_implementation.csv"))
    assert function_order(scored) == ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"]

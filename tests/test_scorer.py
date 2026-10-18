import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gap_analyzer.catalog import ControlRecord
from gap_analyzer.scorer import score_control


def make_record(**kwargs) -> ControlRecord:
    base = dict(
        function="PROTECT", category_id="PR.AA", category_name="Identity Management",
        subcategory_id="PR.AA-01", subcategory_description="test",
        control_owner="Test", implementation_status="Not Implemented",
        maturity_level=1, criticality="High", last_assessed="2026-01-01",
    )
    base.update(kwargs)
    return ControlRecord(**base)


def test_not_implemented_high_criticality_is_critical_priority():
    rec = make_record(implementation_status="Not Implemented", criticality="High", maturity_level=1)
    scored = score_control(rec)
    assert scored.priority in ("Critical", "High")
    assert scored.risk_score > 0


def test_implemented_control_has_no_priority():
    rec = make_record(implementation_status="Implemented", maturity_level=5, criticality="Low")
    scored = score_control(rec)
    assert scored.priority == "None"
    assert scored.risk_score == 0


def test_partial_scores_between_implemented_and_not_implemented():
    implemented = score_control(make_record(implementation_status="Implemented", maturity_level=4))
    partial = score_control(make_record(implementation_status="Partial", maturity_level=4))
    not_impl = score_control(make_record(implementation_status="Not Implemented", maturity_level=4))
    assert implemented.risk_score < partial.risk_score < not_impl.risk_score


def _impl(tmp_path, body):
    p = tmp_path / "impl.csv"
    p.write_text(body, encoding="utf-8")
    return p


def test_maturity_out_of_range_is_rejected(tmp_path):
    # maturity 10 used to drive the risk score to 0 and hide a Not Implemented, High control
    import pytest
    from gap_analyzer.catalog import ImplementationFileError, load_implementation
    p = _impl(tmp_path, "subcategory_id,implementation_status,maturity_level,criticality\n"
                        "PR.AA-01,Not Implemented,10,High\n")
    with pytest.raises(ImplementationFileError, match="line 2: maturity_level must be 0-5"):
        load_implementation(p)


def test_bad_maturity_and_missing_column_are_clear_errors(tmp_path):
    import pytest
    from gap_analyzer.catalog import ImplementationFileError, load_implementation
    with pytest.raises(ImplementationFileError, match="whole number"):
        load_implementation(_impl(tmp_path, "subcategory_id,maturity_level\nPR.AA-01,high\n"))
    with pytest.raises(ImplementationFileError, match="subcategory_id"):
        load_implementation(_impl(tmp_path, "id,maturity_level\nPR.AA-01,2\n"))


def test_csv_export_neutralizes_formulas(tmp_path):
    import csv
    from gap_analyzer.report import write_csv_export
    from gap_analyzer.scorer import score_all
    rec = make_record(control_owner='=HYPERLINK("http://evil.example","x")')
    out = tmp_path / "out.csv"
    write_csv_export(score_all([rec]), out)
    row = list(csv.DictReader(out.open(encoding="utf-8")))[0]
    assert row["owner"].startswith("'=")

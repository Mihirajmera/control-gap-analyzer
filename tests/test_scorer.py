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

"""Risk-score control gaps by combining implementation status, maturity, and criticality.

Scoring model (transparent and intentionally simple, matching how a GRC risk register
typically weighs likelihood x impact):

  status_weight:      Not Implemented = 3, Partial = 2, Implemented = 0, Not Assessed = 3
  maturity_penalty:   (5 - maturity_level) / 5   -> low maturity increases risk
  criticality_weight: High = 3, Medium = 2, Low = 1

  risk_score = status_weight * criticality_weight * (1 + maturity_penalty)

Higher score = higher priority to remediate. Scores are not calibrated against any
specific organization's risk appetite; adjust the weights in this module to match yours.
"""
from __future__ import annotations

from dataclasses import dataclass

from .catalog import ControlRecord

STATUS_WEIGHT = {
    "Implemented": 0,
    "Partial": 2,
    "Not Implemented": 3,
    "Not Assessed": 3,
}

CRITICALITY_WEIGHT = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


@dataclass
class ScoredControl:
    record: ControlRecord
    risk_score: float
    priority: str


def score_control(record: ControlRecord) -> ScoredControl:
    status_w = STATUS_WEIGHT.get(record.implementation_status, 3)
    crit_w = CRITICALITY_WEIGHT.get(record.criticality, 2)
    maturity_penalty = (5 - record.maturity_level) / 5 if record.maturity_level else 1.0

    risk_score = status_w * crit_w * (1 + maturity_penalty)

    if risk_score >= 12:
        priority = "Critical"
    elif risk_score >= 7:
        priority = "High"
    elif risk_score >= 3:
        priority = "Medium"
    elif risk_score > 0:
        priority = "Low"
    else:
        priority = "None"

    return ScoredControl(record=record, risk_score=round(risk_score, 2), priority=priority)


def score_all(records: list[ControlRecord]) -> list[ScoredControl]:
    return sorted(
        (score_control(r) for r in records),
        key=lambda s: s.risk_score,
        reverse=True,
    )

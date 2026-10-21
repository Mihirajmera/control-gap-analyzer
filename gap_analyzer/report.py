"""Render gap analysis results as a Markdown report and a CSV export."""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from .scorer import ScoredControl

PRIORITY_EMOJI = {
    "Critical": "\U0001F534",
    "High": "\U0001F7E0",
    "Medium": "\U0001F7E1",
    "Low": "\U0001F7E2",
    "None": "✅",
}


def _md(value) -> str:
    """Escape text for a Markdown table cell so a '|' can't break the row."""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _csv_safe(value):
    """Neutralize spreadsheet formulas (CSV injection): a cell that starts with = + - @ or a
    control character is prefixed with ' so Excel and Sheets treat it as text."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


CSF_FUNCTIONS = ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"]
AI_RMF_FUNCTIONS = ["GOVERN", "MAP", "MEASURE", "MANAGE"]


def function_order(scored: list[ScoredControl]) -> list[str]:
    """Functions to report, in the framework's own order: all six for NIST CSF, the AI RMF's
    four, and natural order (A.2, A.3 ... A.10) for anything else, such as ISO 42001 Annex A."""
    present = {s.record.function for s in scored}
    if present <= set(CSF_FUNCTIONS):
        return CSF_FUNCTIONS
    if present <= set(AI_RMF_FUNCTIONS):
        return AI_RMF_FUNCTIONS
    return sorted(present, key=lambda f: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", f)])


def summarize_by_function(scored: list[ScoredControl]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for s in scored:
        summary[s.record.function][s.priority] += 1
    return summary


def write_markdown_report(scored: list[ScoredControl], out_path: str | Path, framework: str = "NIST CSF 2.0") -> None:
    total = len(scored)
    gaps = [s for s in scored if s.priority != "None"]
    critical = [s for s in scored if s.priority == "Critical"]
    high = [s for s in scored if s.priority == "High"]

    lines: list[str] = []
    lines.append(f"# Control Gap Analysis Report — {framework}")
    lines.append("")
    lines.append(f"_Generated {date.today().isoformat()}_")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **{total}** controls assessed")
    lines.append(f"- **{len(gaps)}** controls with an open gap ({len(gaps) / total:.0%})")
    lines.append(f"- **{len(critical)}** Critical priority, **{len(high)}** High priority")
    lines.append("")

    lines.append(f"## Gaps by {framework} Function")
    lines.append("")
    lines.append("| Function | Critical | High | Medium | Low | Closed |")
    lines.append("|---|---|---|---|---|---|")
    summary = summarize_by_function(scored)
    for fn in function_order(scored):
        row = summary.get(fn, {})
        lines.append(
            f"| {_md(fn)} | {row.get('Critical', 0)} | {row.get('High', 0)} | "
            f"{row.get('Medium', 0)} | {row.get('Low', 0)} | {row.get('None', 0)} |"
        )
    lines.append("")

    lines.append("## Prioritized Remediation Backlog")
    lines.append("")
    lines.append("| Priority | Subcategory | Description | Owner | Status | Maturity | Risk Score |")
    lines.append("|---|---|---|---|---|---|---|")
    for s in gaps:
        r = s.record
        emoji = PRIORITY_EMOJI.get(s.priority, "")
        lines.append(
            f"| {emoji} {s.priority} | `{_md(r.subcategory_id)}` | {_md(r.subcategory_description)} | "
            f"{_md(r.control_owner)} | {_md(r.implementation_status)} | {r.maturity_level}/5 | {s.risk_score} |"
        )
    lines.append("")

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def write_csv_export(scored: list[ScoredControl], out_path: str | Path) -> None:
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["function", "category_id", "subcategory_id", "description", "owner",
             "status", "maturity", "criticality", "risk_score", "priority"]
        )
        for s in scored:
            r = s.record
            writer.writerow([_csv_safe(v) for v in (
                r.function, r.category_id, r.subcategory_id, r.subcategory_description,
                r.control_owner, r.implementation_status, r.maturity_level, r.criticality,
                s.risk_score, s.priority)])

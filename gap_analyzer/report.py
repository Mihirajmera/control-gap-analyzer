"""Render gap analysis results as a Markdown report and a CSV export."""
from __future__ import annotations

import csv
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

    lines.append("## Gaps by NIST CSF 2.0 Function")
    lines.append("")
    lines.append("| Function | Critical | High | Medium | Low | Closed |")
    lines.append("|---|---|---|---|---|---|")
    summary = summarize_by_function(scored)
    for fn in ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"]:
        row = summary.get(fn, {})
        lines.append(
            f"| {fn} | {row.get('Critical', 0)} | {row.get('High', 0)} | "
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

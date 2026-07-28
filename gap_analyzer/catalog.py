"""Load and join control catalogs with an organization's implementation status."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ControlRecord:
    function: str
    category_id: str
    category_name: str
    subcategory_id: str
    subcategory_description: str
    control_owner: str = "Unassigned"
    implementation_status: str = "Not Assessed"
    maturity_level: int = 0
    criticality: str = "Medium"
    last_assessed: str = ""


def load_catalog(path: str | Path) -> dict[str, ControlRecord]:
    """Load the framework catalog (function/category/subcategory) keyed by subcategory id."""
    records: dict[str, ControlRecord] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records[row["subcategory_id"]] = ControlRecord(
                function=row["function"],
                category_id=row["category_id"],
                category_name=row["category_name"],
                subcategory_id=row["subcategory_id"],
                subcategory_description=row["subcategory_description"],
            )
    return records


def load_implementation(path: str | Path) -> dict[str, dict]:
    """Load an organization's self-reported implementation status keyed by subcategory id."""
    impl: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            impl[row["subcategory_id"]] = row
    return impl


def join(catalog_path: str | Path, implementation_path: str | Path) -> list[ControlRecord]:
    """Join the framework catalog with implementation status into a single control list.

    Subcategories present in the catalog but missing from the implementation file are
    surfaced as "Not Assessed" so they show up as gaps rather than silently disappearing.
    """
    catalog = load_catalog(catalog_path)
    impl = load_implementation(implementation_path)

    joined: list[ControlRecord] = []
    for sub_id, rec in catalog.items():
        row = impl.get(sub_id)
        if row:
            rec.control_owner = row.get("control_owner", "Unassigned")
            rec.implementation_status = row.get("implementation_status", "Not Assessed")
            rec.maturity_level = int(row.get("maturity_level", 0) or 0)
            rec.criticality = row.get("criticality", "Medium")
            rec.last_assessed = row.get("last_assessed", "")
        joined.append(rec)
    return joined

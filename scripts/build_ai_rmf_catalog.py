"""Rebuild data/nist_ai_rmf_catalog.csv from NIST's official AI RMF Playbook JSON.

    python scripts/build_ai_rmf_catalog.py path/to/playbook.json

Download playbook.json from https://airc.nist.gov/airmf-resources/playbook (AI RMF 1.0 Core,
72 subcategories). NIST publications are US government works in the public domain, so the
subcategory text is used verbatim. Category names are short labels written for this tool.
"""
import csv
import hashlib
import json
import pathlib
import sys

CATEGORY_LABELS = {
    'GOVERN 1': 'Policies, processes and procedures', 'GOVERN 2': 'Accountability structures',
    'GOVERN 3': 'Workforce diversity and inclusion', 'GOVERN 4': 'Risk culture and communication',
    'GOVERN 5': 'Engagement with relevant AI actors', 'GOVERN 6': 'Third-party and supply chain risk',
    'MAP 1': 'Context is established and understood', 'MAP 2': 'Categorization of the AI system',
    'MAP 3': 'Capabilities, benefits and costs', 'MAP 4': 'Risks of third-party components',
    'MAP 5': 'Impacts on individuals, groups and society',
    'MEASURE 1': 'Methods and metrics', 'MEASURE 2': 'Evaluation for trustworthy characteristics',
    'MEASURE 3': 'Tracking risks over time', 'MEASURE 4': 'Feedback on measurement efficacy',
    'MANAGE 1': 'Risk prioritization and response', 'MANAGE 2': 'Maximizing benefits, minimizing harms',
    'MANAGE 3': 'Third-party risk management', 'MANAGE 4': 'Treatment, recovery and communication',
}


def main(src):
    raw = pathlib.Path(src).read_bytes()
    entries = json.loads(raw)
    rows = []
    for e in entries:
        sub = e['title'].strip()                      # e.g. "GOVERN 1.1"
        cat = sub.split('.')[0]                        # "GOVERN 1"
        rows.append([e['type'].upper(), cat, CATEGORY_LABELS[cat], sub, ' '.join(e['description'].split())])
    order = {'GOVERN': 0, 'MAP': 1, 'MEASURE': 2, 'MANAGE': 3}
    rows.sort(key=lambda r: (order[r[0]], int(r[1].split()[1]), int(r[3].split('.')[1])))
    out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'nist_ai_rmf_catalog.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['function', 'category_id', 'category_name', 'subcategory_id', 'subcategory_description'])
        w.writerows(rows)
    print(f'{len(rows)} subcategories from playbook.json (sha256 {hashlib.sha256(raw).hexdigest()}) -> {out}')


if __name__ == '__main__':
    main(sys.argv[1])

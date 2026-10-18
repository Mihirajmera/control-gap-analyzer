# Changelog

## 1.0.1 (2026-10-18)

- **Fixed:** a `maturity_level` above 5 drove the risk score to zero or below, hiding the gap. Values must be whole numbers 0-5; errors name the line.
- **Fixed:** a missing `subcategory_id` column now gives a clear error instead of a traceback.
- **Security:** CSV export neutralizes spreadsheet formulas (CSV injection); Markdown cells escape `|`.
- Continuous fuzzing with ClusterFuzzLite.

## 1.0.0 (2026-10-17)

First tagged release. NIST CSF 2.0 control gap analysis with risk scoring and a prioritized remediation backlog.

- CI on Python 3.11 / current Terraform tooling with every GitHub Action pinned to a commit SHA
- Dependencies pinned by version and hash (`requirements.in` → `requirements.txt`)
- CodeQL, OpenSSF Scorecard and Dependabot
- Security policy with private vulnerability reporting

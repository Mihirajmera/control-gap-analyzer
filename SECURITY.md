# Security policy

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Please **don't open a public issue** for security problems. Report them privately through GitHub's private vulnerability reporting:

**https://github.com/Mihirajmera/control-gap-analyzer/security/advisories/new**

What to expect:

- **Acknowledgement within 5 business days.**
- **An assessment within 14 days**: whether it's accepted as a vulnerability, its severity, and a planned fix.
- **Coordinated disclosure**: a fix is released and the advisory published together, normally within 90 days of the report. You'll be credited in the advisory unless you'd rather not be.

## Scope

Reads control catalogs and implementation CSVs. Especially relevant: a crafted CSV that causes code execution, formula injection in exported reports, or writes outside the output folder.

## Supply chain

GitHub Actions are pinned to commit SHAs, dependencies are pinned by hash, and CodeQL, OpenSSF Scorecard and Dependabot run on this repository.

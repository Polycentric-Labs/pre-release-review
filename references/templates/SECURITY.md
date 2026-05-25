# Security policy (bootstrap-emitted; 1B in v5.1)

> Closes OpenSSF OSPS-VM-01 (CVD policy), OSPS-VM-02 (security contacts), and OSPS-VM-03 (confidential reporting channels) at Maturity 2.

## Supported versions

| Version | Supported | Security updates until |
|---|---|---|
| `<MAJOR>.<MINOR>.x` (latest) | ✅ | <YYYY-MM-DD> |
| `<MAJOR-1>.<MINOR>.x` | ⚠ critical fixes only | <YYYY-MM-DD> |
| Older | ❌ | — |

See `EOL.md` for the full support / end-of-life policy.

## Reporting a vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Preferred channels (in order):

1. **GitHub Security Advisories (private)**: open a draft advisory at `https://github.com/<OWNER>/<REPO>/security/advisories/new`. This gives the maintainer time to coordinate a fix before public disclosure.
2. **Email** (alternative): `<security-contact-email>` — use the PGP key at `<PGP_KEY_URL>` if your finding involves an exploit chain.

When reporting, please include:

- Affected version(s)
- Reproduction steps
- Impact assessment (CVSS vector if you have it; we'll compute one if not)
- Whether you intend to disclose publicly (and target date if so)

## Coordinated disclosure timeline

| Phase | Target |
|---|---|
| Acknowledgement | ≤ 72 hours from report |
| Triage + severity assessment | ≤ 7 days |
| Fix in main branch | ≤ 30 days for CRITICAL/HIGH, ≤ 90 days for MEDIUM, best-effort for LOW |
| Coordinated disclosure | Aligned with reporter; default 90 days from report |
| GitHub Security Advisory published | At disclosure |
| CVE requested (if applicable) | Via GitHub's CNA for CRITICAL/HIGH |

## Out of scope

- Issues in dependencies — please report upstream
- DoS via resource exhaustion on a self-hosted instance (configure resource limits)
- Reports requiring physical access to the user's machine
- Reports that only impact disabled / opt-in features

## Recognition

Researchers who report valid issues are acknowledged in the GitHub Security Advisory (with permission) and in the next release's CHANGELOG. We don't currently offer a paid bounty.

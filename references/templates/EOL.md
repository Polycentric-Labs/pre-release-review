# End-of-life policy (bootstrap-emitted; 1C in v5.1)

> Closes OpenSSF OSPS-DO-04 (document scope + duration of support per released version) and OSPS-DO-05 (communicate when security-update cessation occurs) at Maturity 3.

## Support windows

| Version line | Released | General support until | Security-only support until | EOL |
|---|---|---|---|---|
| `<MAJOR>.<MINOR>.x` (latest) | <YYYY-MM-DD> | <YYYY-MM-DD> | <YYYY-MM-DD> | <YYYY-MM-DD> |
| `<MAJOR-1>.<MINOR>.x` | <YYYY-MM-DD> | <YYYY-MM-DD> (passed) | <YYYY-MM-DD> | <YYYY-MM-DD> |

**Default policy** (override per-project as needed):

- **General support**: 12 months from initial minor release. Covers bug fixes, feature additions, dependency bumps, security patches.
- **Security-only support**: an additional 6 months after general support ends. Covers ONLY CRITICAL and HIGH severity vulnerabilities; bug fixes and dependency bumps stop.
- **EOL**: 18 months from initial minor release. No further updates; users must upgrade.

## What "supported" means

| Activity | General support | Security-only | EOL |
|---|---|---|---|
| Bug fix releases | ✅ | ❌ | ❌ |
| Dependency bumps (cosmetic) | ✅ | ❌ | ❌ |
| Dependency bumps (security) | ✅ | ✅ (CVE-required only) | ❌ |
| CVE patches (CRITICAL / HIGH) | ✅ | ✅ | ❌ |
| CVE patches (MEDIUM / LOW) | ✅ | ❌ | ❌ |
| New features | ✅ | ❌ | ❌ |
| Documentation updates | ✅ | ❌ | ❌ |
| Compatibility shims for newer ecosystems | best-effort | ❌ | ❌ |

## EOL communication

When a version reaches **security-only**: announce 90 days in advance in CHANGELOG + GitHub Release notes + pinned issue.

When a version reaches **EOL**: announce 90 days in advance per the above + publish a GitHub Security Advisory tagged with `lifecycle:EOL` so dependency-scanners flag downstream users.

## Pre-1.0 caveat

Pre-1.0 versions (`0.X.Y`) follow the same policy in principle but with shorter windows: general support 6 months, security-only 3 months, EOL 9 months. This is consistent with SemVer's "anything may change" pre-1.0 signal.

# Project governance (bootstrap-emitted; 1C in v5.1)

> Closes OpenSSF OSPS-GV-01 (publish project roles + responsibilities) and OSPS-BR-07 (credential management policy) at Maturity 2.

## Roles

| Role | Holder | Responsibilities |
|---|---|---|
| Maintainer / Project lead | <NAME> | Final decision authority on roadmap, releases, and breaking changes. Holds publishing credentials. |
| Security contact | <NAME> | First responder for security reports (see `SECURITY.md`). |
| Release manager | <NAME> | Runs `/pre-release-review` pre-tag; owns release-checklist. Typically same as maintainer for solo projects. |
| Contributors | Community | Submit PRs, file issues. No commit access by default. |

For solo-dev projects: all roles held by the same person; this is an **honest declaration**, not a deficiency. The skill's pre-push gate compensates for the structural absence of independent review (see `references/compliance-mapping.md` §honest-gap field).

## Decision-making

| Decision type | Who decides | How |
|---|---|---|
| Bug fixes | Maintainer | Direct merge after `/code-review` + `/security-review` pass |
| Feature additions (minor bumps) | Maintainer | RFC issue → comment period → decision |
| Breaking changes (major bumps) | Maintainer | RFC issue → 30-day comment period → DMADV variant of `/pre-release-review` (v5.1 1K) |
| Security incident response | Security contact, escalating to maintainer | Per `SECURITY.md` coordinated disclosure timeline |
| Project archival / hand-off | Maintainer | Public announcement ≥ 90 days before; per `EOL.md` |

## Credential management policy (closes OSPS-BR-07)

| Credential | Storage | Rotation | Access |
|---|---|---|---|
| Publishing tokens (PyPI / npm / cargo) | OIDC Trusted Publisher (no long-lived token) | N/A | GitHub Actions workflow only |
| Signing keys (cosign / Sigstore) | Sigstore keyless OIDC | N/A | GitHub Actions workflow only |
| GitHub Personal Access Tokens | Encrypted secret store (1Password / SOPS / similar) | Quarterly | Maintainer only |
| API keys (3rd party services) | Encrypted secret store | Per-vendor cadence, minimum annual | Maintainer only |

**Hard rule**: no credentials transit through chat tools, AI assistant context, shell history, or browser inspector. Rotate any credential that has passed through any of these surfaces.

## Code-review policy

- **All changes** require either `/security-review` + `/code-review` (solo dev) OR independent human reviewer (multi-maintainer projects). Solo-dev attests honest-gap on multi-reviewer per compliance-mapping.md.
- **Pre-push gate** (`references/pre-push-gate.md` 19-row runbook) is mandatory; bypass requires verbatim phrase per `references/bypass-protocol.md`.

## Conflict of interest

Any contributor or maintainer who has a financial or competitive interest in a project decision must disclose it in the PR / RFC. For solo-dev projects this is also an honest declaration: the maintainer is the sole beneficiary; the project's open-source release is the conflict-mitigation mechanism.

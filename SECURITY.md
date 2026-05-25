# Security policy

## Reporting a vulnerability

If you discover a security vulnerability in this skill — particularly
in the **Guideline #12 hard rule + bypass-protocol** logic, the **pre-
push gate** runbook, the **`/security-review-scoped` wrapper**, or any
other security-critical surface — please **do not open a public issue**.

### Preferred reporting channel

**GitHub Security Advisories**: [Open a private advisory](https://github.com/Polycentric-Labs/pre-release-review/security/advisories/new)

This routes directly to the maintainers + keeps the disclosure private
until coordinated.

### What to include

- A description of the issue
- Steps to reproduce (skill invocation that triggers the issue + the
  expected vs actual behavior)
- The skill version (visible in the `SKILL.md` frontmatter or `version:`
  field — currently `2026.05.24-v5.1`)
- Your assessment of impact (confidentiality / integrity / availability
  / mechanism-bypass severity)
- Any proposed fix or mitigation

### Response expectations

- Acknowledgment within 7 days
- Initial triage + impact assessment within 14 days
- Coordinated fix + advisory publication when ready
- Credit in the advisory (unless you prefer to remain anonymous)

## Scope

### In scope

- The skill's mechanical hard rules (Guideline #12 freshness gate;
  bypass-phrase enforcement; pre-push gate row failures)
- The `references/` content as it drives operator behavior
- The `scripts/control_chart.py` helper
- The bundled `companion-skills/security-review-scoped/` wrapper
- The `references/templates/` files (templates emit into operator
  repos; bugs here propagate)

### Out of scope

- Operator misuse (e.g., typing the wrong bypass phrase intentionally)
- Issues in Claude Code itself, in the Anthropic API, or in any
  third-party tool the skill orchestrates (`gh`, `pytest`, `osv-scanner`,
  `cosign`, `grype`, etc.) — report those upstream
- Operator-side configuration drift (e.g., `enforce_admins: false` on
  a project that needs `true`) — this is by-design operator choice

## Discovered-during-use issues

The skill is designed to be **self-improving**: running it against a
real project surfaces issues with the skill itself, captured as
**SF-* findings** (skill iteration findings) in each ship's
`docs/security-review-vX.Y.Z.md`. These are tracked in this repo's
issues / discussions, not as security advisories, unless they have a
security implication.

Example: [examples/v0.10.4-walkthrough.md](examples/v0.10.4-walkthrough.md)
documents 9 skill iteration findings discovered during the v5.1
prototype run; these flow into v5.1.x candidate work.

## Supply-chain security

This skill ships as Markdown + Python helpers + YAML templates. No
binary distributions; no compiled artifacts. Tampering at install
time is mitigated by:

- Cloning from `https://github.com/Polycentric-Labs/pre-release-review`
  over TLS
- Reviewing the diff before pulling updates (the skill is designed to
  be auditable; the maintenance rubric in [references/maintenance.md](references/maintenance.md)
  enforces audit-grade discipline)
- The `scripts/control_chart.py` helper is stdlib-only — no transitive
  dependencies

For deeper supply-chain assurance (signed releases, SBOM,
reproducibility), see the skill's own [references/step-7-post-tag.md](references/step-7-post-tag.md)
which captures the SLSA L3 + NIST SSDF PS.3.1 verification surface the
skill encourages operators to ship.

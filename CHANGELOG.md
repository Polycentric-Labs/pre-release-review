# Changelog

All notable changes to the `/pre-release-review` skill are documented
in this file.

Versioning is calendar-based (`YYYY.MM.DD-v<major>[.<minor>]`) — the
date reflects the design lock-in date, not the publish date.

## [2026.05.24-v5.1] — 2026-05-24

**Theme**: Project-shape portability ships + Phase B audit landings.

### Added (substantive changes vs v5.0.1)

- **Compliance mapping expansion** (8 additions):
  - SLSA v1.2 (with v1.0 baseline)
  - NIST SP 800-218A AI Profile (scope-corrected to AI-coding subset
    rather than full AI-model-development surface)
  - OpenSSF OSPS Baseline 8-family enumeration (AC / BR / DO / GV /
    LE / QA / SA / VM)
  - NIST SSDF v1.2 IPD forward-readiness watch (Dec 17 2025 draft)
  - CMMI honest-claim guidance
  - Expanded honest-gap field with AI-as-force-multiplier framing
- **5 compliance-closure templates** (bootstrap-emitted at first-run):
  - DORA Art. 17 incident-severity matrix
  - SECURITY.md + security.txt + GHSA enable instructions
  - GOVERNANCE.md + EOL.md + risk-appetite.md
  - A.6.3 training log
  - OSPS-DO-03 verification recipe
- **Row 20 pre-push gate**: OSPS-QA-05 binary-in-VCS check
- **Row 6 amendment**: test gate now enforces coverage threshold per
  `target_tier` from `config.yaml` (default Silver 80%; Gold 90%)
- **Step 7.4.5**: reproducible-build verify (when `config.yaml
  reproducible_build: true`)
- **Step 6.E business-case prompt** (3 questions: why now / who suffers
  if delayed / rollback path)
- **Goddard / Parasuraman / Cerbos / CodeRabbit / Apiiro citations**
  in bypass-protocol.md establishing the empirical / academic basis
  for the 4-hour freshness ceiling
- **FAIR Loss Magnitude column** added to bug-bucketing rubric
- **`repo_risk_tier` parameterization** in bypass-protocol freshness:
  `high` (15min/1hr), `medium` (1hr/2hr), `low` default (2hr/4hr)
- **Context-sensitive invalidation triggers** for stale-review checks
- **`scripts/control_chart.py`** (stdlib-only): I-MR / u-chart /
  g-chart / DPMO over per-run JSONs
- **DMADV 5th variant** for major-version bumps (0.x → 1.0;
  1.x → 2.0; new product tiers)

### Prototype validation

- **First Evidentia ship under v5.1**: v0.10.4 (2026-05-24); 17th
  consecutive PROCEED-CLEAN of the v0.7.x → v0.10.x line; 9 skill-
  iteration findings (SF-1 through SF-11) surfaced and documented
  in [examples/v0.10.4-walkthrough.md](examples/v0.10.4-walkthrough.md)

## [2026.05.23-v5.0.1] — 2026-05-23

**Theme**: Project-shape portability lands.

### Added (substantive changes vs v4)

- **Guideline #12** (hard rule): AI cannot surface push commands
  without a fresh per-run JSON (< 4h) AND the user's explicit per-
  action approval. Bypass requires one of 3 verbatim phrases.
- **Project-shape detection** (Step 1.0): auto-detects Python / Node /
  Rust / Go / Java / Ruby / PHP / Elixir / .NET; persists to
  `.local/pre-release-review/project-shape.json`
- **First-run bootstrap wizard**: generates skeletons + `config.yaml`
  + initial `doc-inventory.yaml` + initial `publish-targets.yaml`
- **`/security-review-scoped` wrapper**: per-subsystem security
  review with explicit `--files` list; closes v4 failure mode
- **`publish-targets.yaml`** (9 supported kinds): drives Step 7
  sub-step generation
- **`doc-inventory.yaml` + Row 19 documentation-freshness gate**:
  catches stale in-scope docs at pre-push time
- **Row 18 branch-protection bypass audit**: captures + flags;
  never hard-fails
- **EPSS auto-lookup** via FIRST.org API + **CWE auto-populate**
  from `/security-review` output
- **G6 verification gates rewritten in Python**: cross-platform
  parity (replaces GNU coreutils bash dependencies)
- **Auto-generate `docs/security-review-vX.Y.Z.md`** at Step 7.10
  from per-run JSON
- **Stale-review lockout**: WARN at 2h, REFUSE at 4h

### Prototype validation

- Designed at Evidentia v0.10.4 cycle entry after v4 deep-review
  identified 20 gaps

## [2026.04.30-v4] — 2026-04-30

**Theme**: 7th step (post-tag verification) + mandatory `/security-review`.

### Added (substantive changes vs v3)

- **Step 7 post-tag verification** (NEW): SLSA L3 / NIST SSDF PS.3.1
  audit-loop closure
- **Mandatory `/security-review`** at 3 boundaries (Step 3 + Step 4 +
  Step 6.C)
- **17-row pre-push gate** (vs v3's lighter rows)
- **CVSS / CWE / EPSS columns** on bug-bucket findings
- **Container CVE scanning** (Trivy, later Grype in v5.0.1 after
  March 2026 Trivy compromise)
- **License/SCA enforcement** (SPDX allowlist)
- **Threat-model existence check** (refuses minor release if
  `docs/threat-model.md` missing or > 180 days stale)
- **DAST runtime probing** in Step 4 (Schemathesis + Playwright)
- **Reproducible-build verification** (rebuild + sha256sum match)
- **Skill file architecture split**: monolithic SKILL.md → entry-point
  + per-step references in `references/`

### Prototype validation

- Evidentia v0.7.5 (April 2026) → v0.10.3 (May 2026)
- Cycle where the v4 `/security-review` #2-skipped failure mode +
  the AI-bypasses-push-gate failure mode surfaced (both drove v5)

## [2026.04.25-v3] — 2026-04-25

**Theme**: First formal pre-release-review skill (6 steps).

### Initial design

- 6-step structure: process review → project review → re-test commits
  → capability matrix → refinements → release-checklist + tag
- 11 binding guidelines
- Skip-by-reuse criteria for Step 2 (positioning doc) and Step 4
  (capability matrix)
- 3 reference deliverables (positioning-and-value.md, capability-
  matrix.md, release-checklist.md)

### Prototype validation

- Evidentia v0.7.0 (April 2026). Surfaced 18 bugs across 4 buckets
  (5 CRITICAL, 5 HIGH, 5 MEDIUM, 3 LOW)

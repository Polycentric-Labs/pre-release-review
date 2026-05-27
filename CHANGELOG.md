# Changelog

All notable changes to the `/pre-release-review` skill are documented
in this file.

Versioning is calendar-based (`YYYY.MM.DD-v<major>[.<minor>[.<patch>]]`)
— the date reflects the design lock-in date, not the publish date.

## [2026.05.27-v5.1.4] — 2026-05-27

**Theme**: Reflect the Evidentia-side refactor that externalizes the
phrase-audit pattern set out of the public-tracked script source.

### Changed

- **Step 5.D.3 description prose** — Rephrased to:
  - rename the 4th invariant from the old descriptive identifier
    to the topic-neutral `phrase_audit` (matching the renamed check
    in the script);
  - replace topic-specific descriptions of the pattern set with
    topic-neutral phrasing ("forbidden-phrase matches" / "forbidden
    phrases") wherever the specific subject of filtering isn't
    load-bearing for the reader;
  - update the cutoff SHA reference from `32df7fa` → `f1dac4e` (the
    last commit containing literal patterns in public-tracked
    Evidentia source);
  - document the new fallback behavior: if the project under review
    has no `private/check-docs-health-patterns.yaml`, the 4 phrase-
    related checks emit one advisory WARN and the 4 doc-health
    invariants still run normally;
  - rename the bypass env var from `EVIDENTIA_ALLOW_TIER_VOCAB_IN_COMMIT`
    → `EVIDENTIA_ALLOW_PHRASE_BYPASS` (legacy var still honored for
    one cycle).

### Rationale

The v5.1.3 description prose itself contained the phrases the gate
was designed to filter for, which leaked vocab via the skill list +
the Skill tool's read-on-invocation. The v5.1.4 prose is neutral.
The script invocation is unchanged.

## [2026.05.27-v5.1.3] — 2026-05-27

**Theme**: Publicly-facing-surface extension of the v5.1.2 docs-health
gate — prevent forbidden phrasing from leaking into commit messages,
annotated tag bodies, or GitHub Release bodies.

### Changed

- **Step 5.D.3** — Extended the comprehensive docs-health check in
  [references/steps-5-6.md §Step 5 sub-passes](references/steps-5-6.md)
  from 5 invariants to 8 by adding 3 publicly-facing-surface checks.
  Same script invocation as v5.1.2 (`scripts/check_docs_health.py
  --strict`); the 3 new checks are auto-included via the script's
  extended scope. No new Step 5.D.4 is added — a separate step would
  be confusing duplication.

### Added (the 3 new publicly-facing-surface checks)

- **commit_msg_audit** — scans `git log <cutoff>..HEAD` bodies for
  the same regex set as `phrase_audit`. Cutoff SHA `f1dac4e` (Allen
  2026-05-27 decision) treats earlier history as immutable;
  v0.10.5 tag + earlier are allowlisted.
- **tag_msg_audit** — scans annotated tag bodies for the same regex
  set. Older tags are allowlisted as immutable because a force-update
  would break cosign signatures bound to those SHAs.
- **release_body_audit** — uses `gh api` to inspect the latest
  GitHub Release body. Advisory mode (gracefully WARNs if `gh` is
  unauthenticated or rate-limited rather than blocking).
- **Companion local commit-msg hook** — defense-in-depth pattern:
  Evidentia's `.githooks/commit-msg` (activated via `bash
  scripts/setup-githooks.sh`) catches forbidden phrasing at `git
  commit` time BEFORE the skill's pre-tag gate fires. The Step 5.D.3
  `commit_msg_audit` is the belt-and-suspenders catch for the 1% case
  where the hook was bypassed (`git commit --no-verify`) or where a
  commit arrived via a different path (rebase / squash / merge
  commit / cherry-pick).

### Originating directive

- **Allen's 2026-05-27 follow-on directive** (same-day extension of
  the v5.1.2 docs-health gate). The v5.1.2 baseline covered the
  tracked `.md` files; commit messages, annotated tag bodies, and
  GitHub Release bodies are *also* publicly visible prose written
  under the same prose-discipline rules but were not previously
  covered by any automated check. The 3 new checks close that gap.
  Project-side reference implementation ships in Evidentia at commit
  `f1dac4e` (extends commit `32df7fa`'s v5.1.2 baseline).

### Companion lessons-learned entry

- A companion lessons-learned entry would normally land at the
  project's `.local/pre-release-review/lessons-learned.yaml` as
  LL-V107-2 but Evidentia v0.10.7 hasn't shipped yet — flag for the
  v0.10.7 cycle's Step 7.G to add the entry alongside the v5.1.2
  LL-V107-1 entry.

## [2026.05.27-v5.1.2] — 2026-05-27

**Theme**: Comprehensive docs-health gate — prevent docs-only regressions
from shipping silently in a tag.

### Added

- **Step 5.D.3** — Comprehensive docs-health check in
  [references/steps-5-6.md §Step 5 sub-passes](references/steps-5-6.md).
  Runs the target project's `scripts/check_docs_health.py --strict`
  from the project's working directory. The check enforces 5 health
  invariants across every tracked `.md` file:
  1. **parse_validity** — every `.md` is valid UTF-8
  2. **cross_link_resolve** — every relative markdown link resolves
     (code-fence-aware + per-file allowlist + per-line allowlist +
     wiki-stub auto-downgrade to WARN)
  3. **readme_size_guard** — `README.md` at or below byte budget
  4. **phrase_audit** — no forbidden-phrase matches in tracked
     public files (pattern set loaded from project-local gitignored
     config; per-file allowlist for legitimate prose)
  5. **private_path_leak** — no public `.md` file links to `private/`
     paths
  Exits 0 on PASS / 2 on FAIL under `--strict`. Also supports
  `--advisory` (exits 0 even with FAILs; dev preview) and `--json`
  (machine-readable for per-run JSON `docs_health` field). Blocks
  Step 5.D on FAIL; bypass via `STALE REVIEW ACCEPTED — <reason>`
  per [bypass-protocol.md §B2](references/bypass-protocol.md). SKIP
  with yellow flag when the script is absent rather than blocking;
  surface a recommendation to author one.

### Originating directive

- **Allen's 2026-05-27 directive** (Evidentia v0.10.7 docs-cleanup
  cycle): the cycle surfaced ~50 broken cross-links + 35 forbidden-
  phrase matches that would have shipped silently in the next tag
  without a dedicated docs invariant gate. The existing pre-push gate rows
  (test gate, security review, etc.) do not catch docs-only
  regressions because the prose compiles fine and runs no code. The
  v5.1.2 Step 5.D.3 gate plugs that hole. Project-side script ships
  in Evidentia at commit `32df7fa` as the reference implementation;
  other projects need to author their own (byte budgets and
  allowlists are project-specific).

### Companion lessons-learned entry

- A companion lessons-learned entry would normally land at the
  project's `.local/pre-release-review/lessons-learned.yaml` as
  LL-V107-1 but Evidentia v0.10.7 hasn't shipped yet — flag for the
  v0.10.7 cycle's Step 7.G to add the entry.

## [2026.05.27-v5.1.1] — 2026-05-27

**Theme**: LL-V105-1 prevention — new-PyPI-project pending-publisher
pre-flight check.

### Added

- **Step 5.D.2** — New-PyPI-project pending-publisher check in
  [references/steps-5-6.md §Step 5 sub-passes](references/steps-5-6.md).
  For projects with a `pypi-trusted-publisher` target, GETs
  `https://pypi.org/pypi/<pkg>/json` for every workspace package.
  HTTP 404 → NEW PyPI project; operator must confirm a pending
  publisher row exists at https://pypi.org/manage/account/publishing/
  before Step 6.F surfaces `git tag`. Blocks if any NEW package is
  un-confirmed at gate close. Skips on rate-limit / network error
  with a yellow flag. Skips entirely when `publish-targets.yaml`
  has no `pypi-trusted-publisher` target.

### Originating incident

- **LL-V105-1** (Evidentia v0.10.5 partial-publish, 2026-05-26):
  `evidentia-eval` was the 8th workspace package, added in v0.10.5
  Phase 9. No PyPI pending publisher was pre-configured. When
  `release.yml` fired, the OIDC Trusted Publisher upload step hit
  HTTP 400 (`Non-user identities cannot create new projects`) at the
  4th alphabetical package; 5 of 8 packages published, 3 missing,
  no GHCR container, no GitHub Release until recovery. Recovery
  required Allen manually configuring the pending publisher on PyPI's
  UI + `gh run rerun --failed` (~10 min total). PyPI version slots
  for the 5 already-uploaded packages were burned irreversibly. This
  v5.1.1 check is designed to surface the same condition at Step 5.D
  BEFORE the tag is created, when remediation is cheap.

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

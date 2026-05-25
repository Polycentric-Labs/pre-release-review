# Steps 5–6: Refinements + release-checklist + tag

## Step 5 — Project-wide refinements

Polish every visible surface for consistency, professionalism, UX.

### 5.1 Commit-decomposition rubric

When staging any sub-pass that touches >5 files or >300 LOC:

1. Each commit must produce a buildable state on its own.
2. Group by dependency depth, not by file path. Foundation
   primitives (audit, exceptions, types) commit first; callers next;
   docs last. Verify by reading imports.
3. Conventional-commit prefix per the project's convention:
   `feat(<scope>):` / `fix(<scope>):` / `chore(release|lint|refinements):`
   / `docs(<scope>):` / `ci(<scope>):`.
4. One thematic concern per commit. Cross-cutting fixes touching
   unrelated subsystems should split. Exception: pure-mechanical
   lint sweeps in their own `chore(lint):` commit.
5. **Verify the chain by running the test gate after EACH commit.**
   `pytest -q` after every `git commit`. If a commit breaks the
   build, reorder or split before pushing.
6. Skip the rubric for trivially small changes (1-3 files, single
   thematic concern, < 50 LOC) — one commit is fine.

### 5.2 Sub-passes (commit each separately)

- **5.A** — Apply MEDIUM fixes from Steps 3 + 4 in a single commit
- **5.B** — Write `docs/vX.Y.Z+1-plan.md` (forward-looking next
  release scope; capture HIGH-bucket items + design rationale)
- **5.C** — Documentation refresh: CHANGELOG (rename `[Unreleased]`
  → `[X.Y.Z] - DATE` + fresh `[Unreleased]` block + release-summary),
  ROADMAP (mark this version SHIPPED), README (test counts, status
  banners, version-callout), per-package READMEs if material.
  **v5 addition (per Q11)**: also runs the doc-inventory iteration
  per [documentation-freshness.md §Step 5.C iteration logic](documentation-freshness.md#step-5c-iteration-logic).
  For each in-scope doc per `.local/pre-release-review/doc-inventory.yaml`
  that wasn't already touched in this release, surface "review this
  doc? (Y/n/skip-with-rationale)". Pre-fills the gate for Row 19
  (documentation-freshness) at Step 6.C. Forces zero stale docs at
  ship time without the operator having to remember which docs are
  in scope.
- **5.D** — Deletion review (deprecated scripts, stale fixtures,
  orphaned files); add `[DEPRECATED <date>]` headers to historical
  one-shot scripts retained for transparency
- **5.E** — Doc merging review (consolidate identical-purpose docs)
- **5.F** — UI/UX refinements (CLI output consistency, web UI design
  tokens, accessibility per WCAG 2.1 AA)
- **5.G** — Multi-industry sample data (synthetic; **triple-check no
  real customer data is incorporated**); often deferred to next
  release

### 5.3 Verification gate (G6)

`git bisect run pytest -q` across the new commits passes at every
commit in the chain. Verifies the rubric.

**STOP for approval** at each commit boundary if user prefers;
default is to batch within each sub-pass.

---

## Step 6 — Release-checklist creation + final review + tag

Goal: create the canonical per-release checklist (run for every
future release), do a final test+scour pass, surface a comprehensive
overview for explicit tag approval.

### 6.A Write `docs/release-checklist.md`

11-step self-referential checklist:

- Step 0 = Review and update this checklist itself
- Steps 1–7 = pre-release (scope confirm / version bumps /
  CHANGELOG / docs / test gate / scour / external repo review)
- Step 8 = Tag + push (the irreversible step; STOPS for explicit
  user approval)
- Step 9 = Post-release verification (delegated to Step 7 of THIS
  skill — see [step-7-post-tag.md](step-7-post-tag.md))
- Step 10 = Post-release housekeeping
- Step 11 = Quarterly cadence (independent of releases)

Standards alignment section: NIST SSDF + OpenSSF Scorecard +
CISA Secure by Design + PEP 740 + SLSA L3 + ISO 27001:2022 +
SOC 2 Type II + DORA. See [compliance-mapping.md](compliance-mapping.md).

### 6.B `MEMORY.md` pointer file for the release checklist

Single-line entry pointing to `docs/release-checklist.md`.

### 6.C Final gate — runs the [19-row pre-push gate](pre-push-gate.md) PLUS:

1. Third `/security-review` invocation (per-G12) — full HEAD vs
   prev-tag scope. See [security-review-integration.md](security-review-integration.md).
2. `ruff check` + `mypy --strict` + `pytest` + `uv build` +
   `twine check` (full clean run, no `-q`)
3. Reproducible-build check (NEW per G10): build twice + diff
   sha256sum across `dist/*.whl` — must match. SOURCE_DATE_EPOCH
   + deterministic wheel build flags.
4. `.gitignore` audit — confirm `.env*`, `*.pem`, `*.key`,
   `*.crt`, `*.p12`, common secret-store filenames covered.
5. 3-pass scour grep across the diff (credentials per the
   pre-push gate, prior-version strings that should be bumped,
   TODO/FIXME/XXX that landed accidentally).
6. External service review:
   - `gh repo view --json description,topics,homepageUrl` —
     About text, topics, homepage current
   - `gh secret list --env=<each-env>` — legacy long-lived
     secrets deleted (e.g. `PYPI_API_TOKEN` after OIDC migration)
   - `gh api repos/<owner>/<repo>/environments` — environment
     protection rules in place
   - `gh search commits --author=<email>` — email-leak audit
7. Code-scanning alert delta (pre-push gate Row 12) — fail on
   any HIGH alert created since prev-tag without ack.
8. Container CVE scan (pre-push gate Row 13) — **Grype default** per
   v5.0.1 (post-Trivy-compromise CVE-2026-33634); fail on any HIGH
   unacked. Trivy opt-in via `config.yaml container_cve_tool: trivy`
   if operator explicitly wants it (post-incident-rotation accepted).
9. Vulnerability aging SLO (pre-push gate Row 14) — `gh api
   /repos/.../dependabot/alerts` filtered to HIGH > 14 days
   unpatched.
10. License/SCA enforcement (pre-push gate Row 15) — pip-licenses
    + SPDX allowlist, no GPL/AGPL inbound, Tier-C placeholder
    catalog content not bundled in wheels.
11. Secret-rotation cadence (pre-push gate Row 16) — `gh api
    user/keys` + `gh secret list` `created_at` > 90 days warning.
12. **Pre-tag CHANGELOG-presence gate** (pre-push gate Row 17, NEW
    post-Evidentia-v0.10.3). Run the project's CHANGELOG-block
    extraction script against the bumped-but-not-yet-tagged version
    BEFORE creating the annotated tag. Reject the tag if extraction
    fails or returns < 1500 bytes. Failing this gate at tag time is
    cheap (re-author the `[X.Y.Z]` CHANGELOG block); failing it AT
    `release.yml` runtime is expensive (PyPI publish has already
    fired and is irreversible — the next-version slot is consumed —
    forcing a move-tag re-fire to land the GitHub Release + container).
    Complements any project-side workflow-layer gate (e.g.,
    Evidentia's `verify-changelog.yml`) — the workflow layer catches
    the drift in CI before tagging is even attempted; this Step 6.C
    check is the operator's local-machine belt-and-suspenders. See
    Evidentia v0.10.3 ship incident
    (`docs/security-review-v0.10.3.md` §Step 6 ship incident +
    recovery) for the canonical example.
13. **Branch-protection bypass audit** (pre-push gate Row 18,
    NEW v5 per Q5). Parse the actual `git push` remote output for
    "Bypassed rule violations" string. AUDIT EVENT, not hard-fail
    — admin bypass is sometimes legitimate. Capture to per-run JSON
    `bypass_events[]`; yellow-flag at Step 6.D; surface in Step 7.10
    MEMORY.md SHIPPED entry. Bypass-rate > 1 per release across
    multiple cycles is a process smell flagged at the next
    Quarterly cadence review.
14. **Documentation freshness gate** (pre-push gate Row 19, NEW v5
    per Q11). Hard-fail when any doc in
    `.local/pre-release-review/doc-inventory.yaml` is stale per
    its policy: `every-release` docs untouched / `N-releases`
    policies exceeded / `must_match_version: true` docs not
    referencing current version / `refresh_required_on: [bump-shape]`
    untouched. Pre-filled by Step 5.C iteration. Bypass via
    `DOC FRESHNESS BYPASS — <reason>` per
    [bypass-protocol.md §B3](bypass-protocol.md#b3--doc-freshness-bypass--reason).

### 6.D Surface comprehensive pre-tag overview

To the user: commit list, test results, build artifacts, scour
findings, external state, known deferrals, all 20 pre-push gate
row outcomes (v5.1 added Row 20 OSPS-QA-05 binary-in-VCS check),
all G6 verification-gate outcomes. Also surfaces: publish targets
that will fire from `publish-targets.yaml` (so the operator sees
what Step 7 will verify), any bypass events accumulated during
Step 6.C, the per-run JSON path for audit reference.

### 6.E STOP for explicit tag-creation approval

Per the publishing-authority protocol in `~/.claude/CLAUDE.md`,
tag creation + push requires explicit per-action user approval.

**Business-case prompt (NEW v5.1; 1E)** — surface these 3 questions
to the operator BEFORE asking for tag approval. The operator should
answer briefly (1-2 lines each) into the per-run JSON
`business_case` field; the answers persist alongside the security-review
doc as the durable "why" record. Refusal-to-answer is itself a yellow
flag — if you can't articulate the case in 30 seconds, the release
may not be ready.

1. **Why now / why this version**: what's the value-delivery argument
   for shipping today rather than waiting one more cycle? Concrete
   user / customer / regulatory pressure, OR a windowed opportunity
   (a downstream library is pinned to this version, an event date,
   etc.).
2. **Who suffers if delayed**: name the actual humans / orgs blocked
   by the absence of this release. "I want to ship" is not an answer;
   "the federal-SI walk-through next Tuesday needs the OCSF mapping"
   is. If no one is blocked, consider whether the release would be
   better deferred + bundled with more changes.
3. **What's the rollback if it goes wrong**: name the specific revert
   path. PyPI yanks (not deletes); container tag deletion (cosign
   signatures are immutable); CHANGELOG correction commit; deprecation
   notice in next release. If the answer is "we can't roll back" the
   risk-appetite review (template/risk-appetite.md) becomes ship-blocking
   rather than informational.

After the answers land, the standard publishing-authority approval
ritual fires: surface the exact `git tag` + `git push origin <tag>`
commands, explain effects, and wait for explicit operator yes.

### 6.F Tag + push + monitor `release.yml`

Only after approval: `git tag vX.Y.Z && git push origin vX.Y.Z`.
Monitor the release workflow run via `gh run watch`.

The skill's tool layer captures the `git push` output to
`.local/pre-release-review/last-push-output.txt` for Row 18 bypass-
audit post-processing.

### 6.G Hand off to Step 7 (post-tag verification, publish-targets driven)

NEW in v4 — see [step-7-post-tag.md](step-7-post-tag.md). Runs
automatically after `release.yml` completes.

**v5 change (per Q8)**: Step 7's sub-step list is now generated
dynamically from `.local/pre-release-review/publish-targets.yaml`
per [publish-targets.md §Step 7 sub-step generation](publish-targets.md#step-7-sub-step-generation).
Same skill drives PyPI+GHCR projects (e.g. Evidentia) AND Vercel-
hosted Next.js apps AND Rust-cargo+homebrew-tap projects without
per-project skill edits.

### 6.H Post-release housekeeping (deferred to Step 7's tail)

Archive deprecated repos, yank deprecated artifacts, delete legacy
secrets — delegated to Step 7.6.

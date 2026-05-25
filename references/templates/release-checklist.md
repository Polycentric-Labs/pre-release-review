# Release checklist — {PROJECT_NAME}

> Skill-bootstrapped template (v5 first-run-bootstrap deliverable).
> 11-step self-referential checklist run for every release. Step 0 reviews + updates this checklist itself.

## Step 0 — Review + update this checklist

Re-read this file end-to-end before every release. Update commands when the project's tooling changes. Note any new gates added since the last release.

## Step 1 — Scope confirmation

- [ ] Bump shape: patch / minor / major
- [ ] Variant of `/pre-release-review`: Pre-tag / Pre-push / Pre-merge / Quarterly
- [ ] Scope: Diff + 1-hop closure / Full re-read / Diff only / Other
- [ ] `.local/pre-release-review/runs/<this-run>.json` initialized

## Step 2 — Version bumps

- [ ] `{VERSION_BUMP_COMMAND}` (per `_shape-routes.json:version_extract` for the project shape)
- [ ] All `{VERSION_FILES}` (per `_shape-routes.json:version_files`) updated atomically
- [ ] Inter-package pins (multi-package projects) updated to match
- [ ] Lockfile regenerated: `{LOCKFILE_REGEN_COMMAND}`

## Step 3 — CHANGELOG

- [ ] `[Unreleased]` block renamed to `[X.Y.Z] - YYYY-MM-DD`
- [ ] Fresh `[Unreleased]` block added at top
- [ ] Block content is ≥ 1500 bytes (pre-push gate Row 17 enforces this)
- [ ] `python scripts/extract_changelog_block.py X.Y.Z` smoke-test passes

## Step 4 — Documentation

- [ ] Doc-inventory iteration per `.local/pre-release-review/doc-inventory.yaml`
- [ ] All `every-release` policy docs touched
- [ ] All `must_match_version: true` docs reference vX.Y.Z
- [ ] All `refresh_required_on: [bump-shape]` docs touched per bump
- [ ] README badges + status banners updated

## Step 5 — Test gate

- [ ] `{TEST_COMMAND}` (per `_shape-routes.json:test`): all pass
- [ ] `{LINT_COMMAND}` (per `_shape-routes.json:lint`): clean
- [ ] `{BUILD_COMMAND}` (per `_shape-routes.json:build`): all artifacts produced
- [ ] `osv-scanner --sbom` clean (or all findings allowlisted with expiry)

## Step 6 — Scour pass

- [ ] No `TODO` / `FIXME` / `XXX` landed accidentally
- [ ] No prior-version strings left unbumped
- [ ] No credentials in diff (pre-push gate Row 1)
- [ ] No Claude attribution in diff or commit messages (pre-push gate Row 2 + 3)

## Step 7 — External repo review

- [ ] `gh repo view --json description,topics,homepageUrl` current
- [ ] `gh secret list --env=<env>` legacy long-lived secrets deleted
- [ ] `gh api repos/<owner>/<repo>/branches/main/protection` rules intact
- [ ] `gh search commits --author=<email>` email-leak audit clean

## Step 8 — Tag + push (THE IRREVERSIBLE STEP)

- [ ] STOP: explicit user approval received per publishing-authority protocol
- [ ] STOP: Guideline #12 freshness check passed (per-run JSON < 4h)
- [ ] STOP: 19-row pre-push gate passes (or all failures explicitly bypassed via verbatim phrase)
- [ ] `git tag vX.Y.Z -m 'Release vX.Y.Z'`
- [ ] `git push origin vX.Y.Z`
- [ ] `gh run watch <run-id>` until release.yml completes

## Step 9 — Post-release verification

Delegated to `/pre-release-review` Step 7 per `~/.claude/skills/pre-release-review/references/step-7-post-tag.md`. Driven by `.local/pre-release-review/publish-targets.yaml`.

## Step 10 — Post-release housekeeping

- [ ] Archive deprecated artifacts (yank pre-release wheels, etc.)
- [ ] Delete legacy long-lived secrets superseded by OIDC
- [ ] Update `MEMORY.md` with SHIPPED-vX.Y.Z entry
- [ ] Update `doc-inventory.yaml` `last_reviewed_*` for every doc touched

## Step 11 — Quarterly cadence (independent of releases)

- [ ] If > 90 days since last Step 2 positioning refresh: schedule one
- [ ] If > 180 days since last threat-model touch: refresh per G5
- [ ] If `bypass_events[]` rate > 1 per release: investigate process smell

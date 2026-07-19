# Pre-push gate (21 rows in v5.2.1)

Checks that MUST run before any `git push` (in-flight branch push,
PR merge, or tag push). The full pre-tag flow rolls these into
Step 6.C; the **pre-push variant** runs them as the named gate.

v5 adds **Row 18** (branch-protection-bypass audit per Q5) and
**Row 19** (documentation-freshness per Q11) to the v4 17-row
baseline (which included the post-Evidentia-v0.10.3 Row 17 CHANGELOG-
presence gate). **v5.1 adds Row 20** (OSPS-QA-05 binary-in-VCS check)
and amends **Row 6** (test gate now enforces coverage threshold per
OpenSSF Gold/Silver tier). **v5.2.1 (2026-07-02) adds Row 21**
(release-workflow first-live-run audit) after the Evidentia
v0.10.14/v0.10.15 double ghost-tag incident: a PROCEED-CLEAN review
preceded two tag-time failures inside publish jobs that are
structurally unreachable in PR CI (see Evidentia
`.local/pre-release-review/lessons-learned.yaml` LL-V1016-1).

## The 20-row table

| # | Check | Pass criterion |
|---|---|---|
| 1 | Credential pattern sweep of diff content | 0 hits |
| 2 | Claude attribution sweep of diff content | 0 hits |
| 3 | Commit-message attribution sweep (run AFTER staging commits) | 0 hits |
| 4 | `.gitignore` audit for secret-store patterns | Matches found (≥ `.env*` covered) |
| 5 | Staged secret-store files check | Only intentional files |
| 6 | **(AMENDED v5.1; 1I) Test gate with coverage threshold** | All pass AND coverage ≥ `target_tier` from `config.yaml` (default Silver 80%; Gold 90%). Enforced via `--cov-fail-under=<threshold>` (pytest) / `nyc --check-coverage --lines <threshold>` (Node) / equivalent per project-shape. Closes OpenSSF Best Practices Silver/Gold tier requirement. |
| 7 | Type/lint gate on touched paths | Clean (or pre-existing baseline noise documented) |
| 8 | Build sanity | All artifacts produced |
| 9 | Identity check | Matches user's canonical identity per `~/.claude/CLAUDE.md` |
| 10 | Branch sanity | Confirm pushing to the right branch |
| 11 | `gh secret list --env=<env>` (when secrets exist) | Legacy long-lived secrets deleted |
| 12 | **(NEW v4) Code-scanning alert delta** since prior tag | 0 NEW HIGH alerts unacked |
| 13 | **(NEW v4; v5.0.1 default switched to Grype) Container CVE scan** | 0 NEW HIGH unacked CVEs vs prior image. **Default tool: `anchore/grype`** (same vendor as Syft, already used by v5). Trivy retained as opt-in via `config.yaml container_cve_tool: trivy`; the v5.0.1 switch was driven by the **March 2026 Trivy supply-chain compromise** (CVE-2026-33634, CVSS 9.4; vulnerability DB updates suspended through late March; see Aqua Security GHSA-69fq-xp46-6x23). |
| 14 | **(NEW v4) Vulnerability aging SLO** | 0 HIGH/CRITICAL deps unpatched > 14 days |
| 15 | **(NEW v4) License/SCA enforcement** | SPDX allowlist clean; no GPL/AGPL inbound; no Tier-C content in wheels |
| 16 | **(NEW v4) Secret rotation cadence** | 0 secrets > 90 days old without ack |
| 17 | **(NEW post-Evidentia-v0.10.3) Pre-tag CHANGELOG-presence gate** | `python scripts/extract_changelog_block.py <next-version>` (or project equivalent) exits 0 AND emits ≥ 1500 bytes. Mitigates the failure mode where `release.yml` fires, PyPI publish succeeds (irreversible — version slot consumed), and the CHANGELOG-extract step then fails — forcing a move-tag re-fire to land GitHub Release + container. See Evidentia v0.10.3 ship incident 2026-05-23. |
| 18 | **(NEW v5 per Q5) Branch-protection bypass audit** | Push remote-output parsed for "Bypassed rule violations" string; any hit is logged to per-run JSON `bypass_events[]` + yellow-flagged at Step 6.D. Audit event, NOT a hard-fail — bypass is sometimes legit (admin acks for hot-fixes). Surfaces in Step 7.10 MEMORY.md SHIPPED entry. See [bypass-protocol.md §Q5](bypass-protocol.md). |
| 19 | **(NEW v5 per Q11) Documentation freshness gate** | All in-scope docs per `.local/pre-release-review/doc-inventory.yaml` are fresh enough: `staleness_policy: every-release` docs were touched this release; `N-releases` policies satisfied; `must_match_version: true` docs reference the current version; `refresh_required_on: [bump-shape]` honored. Hard-fail unless bypassed via `DOC FRESHNESS BYPASS — <reason>`. See [documentation-freshness.md](documentation-freshness.md). |
| 20 | **(NEW v5.1; 1O) OSPS-QA-05 binary-in-VCS check** | 0 hits: `git ls-files \| xargs file \| grep -E 'ELF\|Mach-O\|PE32'` returns empty. Closes OpenSSF OSPS-QA-05 at all maturity levels. Allowlist via `config.yaml binary_in_vcs_allowlist: [path, ...]` for legitimate cases (e.g., test fixtures, icons). |
| 21 | **(NEW v5.2.1; LL-V1016-1) Release-workflow first-live-run audit** | Fires ONLY when the release/publish workflow file(s) changed since the last **successfully published** tag (`git diff <last-good-tag>..HEAD -- .github/workflows/<release>.yml` non-empty). Publish jobs are structurally unreachable in PR CI — a tag is their first execution, on an irreversible trigger. Before tagging, simulate every post-build job step in execution order and verify: (a) every shell command's tool is installed **in that job** (or runner-preinstalled — `gh`/`jq`/`python`/`docker` yes; `uv`/`uvx`/`cosign`/`syft`/`grype` NO); (b) every pinned action's inputs/outputs exist in its `action.yml` **at the pinned SHA** (fetch it — do not trust comments); (c) artifact upload/download names + paths match across jobs; (d) any `environment:` deployment policy allows **tag refs** (a main-only policy reds every tag run); (e) every event trigger is reachable — a Release created with `GITHUB_TOKEN` NEVER fires `release:` workflows (dead gate); (f) no cache-enabled action in the publish path (cache-poisoning; zizmor). Findings block the tag. Origin: Evidentia v0.10.14 (HashMismatch — pip-compile reuses an existing output-file's hashes) + v0.10.15 (exit 127 — `uvx` never installed in publish-pypi), both caught by the atomic gate with nothing published. |

## Runbook

```bash
# Pre-conditions
gh auth status >/dev/null 2>&1 || echo "WARN: gh not authenticated; rows 11/12/13/14/16 + Step 6.C external review will be skipped"

DIFF_RANGE="${1:-HEAD}"
PREV_TAG="$(git describe --tags --abbrev=0 2>/dev/null || echo '')"

# Row 1: credential pattern sweep (0 = pass)
git diff "$DIFF_RANGE" | grep -ciE "AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|BEGIN.*PRIVATE.*KEY|password\s*[=:]\s*[A-Za-z0-9]{8,}|api[_-]?key\s*[=:]\s*[A-Za-z0-9]{8,}"

# Row 2: Claude attribution sweep of diff content (0 = pass)
git diff "$DIFF_RANGE" | grep -ciE "Co-Authored-By:.*Claude|Co-Authored-By:.*noreply@anthropic|🤖 Generated with"

# Row 3: commit-message attribution sweep (0 = pass)
git log --format="%B" "${PREV_TAG}..HEAD" | grep -ciE "Co-Authored-By:.*Claude|🤖"

# Row 4: .gitignore audit (matches found = pass)
grep -iE "\.env|\.pem|\.key|\.crt|\.p12|secret" .gitignore

# Row 5: staged secret-store files (only intentional files = pass)
git ls-files --cached | grep -iE "\.(env|pem|key|crt|p12)$|\.env\.|secret"

# Row 6-8: test/lint/build gate (project-specific)
# Row 6 (AMENDED v5.1; 1I): test gate now enforces coverage threshold.
# Tier read from .local/pre-release-review/config.yaml `target_tier`
# (default "silver" = 80%; "gold" = 90%; "passing" = no threshold).
TIER="$(python -c 'import yaml; print(yaml.safe_load(open(".local/pre-release-review/config.yaml")).get("target_tier", "silver"))' 2>/dev/null || echo silver)"
case "$TIER" in
  gold)    COV_THRESHOLD=90 ;;
  silver)  COV_THRESHOLD=80 ;;
  passing) COV_THRESHOLD=0  ;;
  *)       COV_THRESHOLD=80 ;;
esac
if [ "$COV_THRESHOLD" -gt 0 ]; then
  pytest -q --cov --cov-fail-under="$COV_THRESHOLD"
else
  pytest -q
fi
mypy --strict-optional <touched-paths>
ruff check <touched-paths>
uv build --all-packages

# Row 9-10: identity + branch sanity
git config user.name && git config user.email
git branch --show-current

# Row 11: legacy-secret check (gh-auth required)
if gh auth status >/dev/null 2>&1; then
  gh secret list --repo <owner>/<repo>
fi

# Row 12 (NEW v4): code-scanning alert delta
if gh auth status >/dev/null 2>&1 && [ -n "$PREV_TAG" ]; then
  prev_tag_date="$(git log -1 --format=%cI "$PREV_TAG")"
  gh api "repos/<owner>/<repo>/code-scanning/alerts" --paginate \
    -q ".[] | select(.state==\"open\" and .rule.security_severity_level==\"high\" and .created_at > \"$prev_tag_date\") | {n: .number, name: .rule.name, path: .most_recent_instance.location.path}"
  # Pass = 0 results OR all listed have explicit ack in .local/security-acks.txt
fi

# Row 13 (NEW v4; v5.0.1 default = Grype): container CVE scan.
# Trivy was compromised March 19+22 2026 (CVE-2026-33634; CVSS 9.4;
# DB updates suspended through late March). v5.0.1 flips default to
# Grype (Anchore — same vendor as Syft already used by Step 7.6).
# Trivy retained as opt-in via config.yaml `container_cve_tool: trivy`.
if [ -f Dockerfile ]; then
  docker build -t <image>:gate-test . >/dev/null
  TOOL="$(python -c 'import yaml; print(yaml.safe_load(open(".local/pre-release-review/config.yaml")).get("container_cve_tool", "grype"))' 2>/dev/null || echo grype)"
  case "$TOOL" in
    grype) grype <image>:gate-test --fail-on high ;;
    trivy) trivy image --severity HIGH,CRITICAL --exit-code 1 --no-progress <image>:gate-test ;;
    *) echo "ERROR: Unknown container_cve_tool=$TOOL"; exit 2 ;;
  esac
fi

# Row 14 (NEW v4): vulnerability aging SLO
if gh auth status >/dev/null 2>&1; then
  gh api "repos/<owner>/<repo>/dependabot/alerts" --paginate \
    -q ".[] | select(.state==\"open\" and .security_advisory.severity==\"high\" and ((now - (.created_at | fromdateiso8601)) > 14*86400)) | {n: .number, advisory: .security_advisory.cve_id, age_days: ((now - (.created_at | fromdateiso8601)) / 86400 | floor)}"
fi

# Row 15 (NEW v4): license/SCA enforcement
pip-licenses --format=json --packages "$(uv pip list --format=freeze | cut -d= -f1 | tr '\n' ' ')" | \
  jq -r '.[] | select(.License | test("(GPL|AGPL|SSPL|BUSL)"; "i")) | "FAIL: \(.Name) \(.License)"'
# Tier-C placeholder content check (project-specific)
grep -rE "Tier-C placeholder catalog" packages/*/src/ && echo "FAIL: Tier-C content in src" || true

# Row 16 (NEW v4): secret rotation cadence
if gh auth status >/dev/null 2>&1; then
  gh api user/keys -q '.[] | select(((now - (.created_at | fromdateiso8601)) > 90*86400)) | "WARN: PAT \(.title) > 90 days old"'
fi

# Row 17 (NEW post-Evidentia-v0.10.3): Pre-tag CHANGELOG-presence gate.
# Mitigates the failure mode where release.yml fires, PyPI publish
# succeeds (IRREVERSIBLE — that version slot is now consumed), and the
# CHANGELOG-extract step then fails because the version's block is
# missing — forcing a move-tag re-fire to land GitHub Release +
# container. Skill-layer mitigation; complements the workflow-layer
# gate (e.g., Evidentia's verify-changelog.yml). Adapt the version-
# detection to your project: here we read the workspace meta
# `[project] version` from the root pyproject.toml.
if [ -f "scripts/extract_changelog_block.py" ] && [ -f "CHANGELOG.md" ] && [ -f "pyproject.toml" ]; then
  NEXT_VER="$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])' 2>/dev/null || echo '')"
  if [ -n "$NEXT_VER" ]; then
    CHANGELOG_BYTES="$(python scripts/extract_changelog_block.py "$NEXT_VER" 2>/dev/null | wc -c)"
    if [ "$CHANGELOG_BYTES" -lt 1500 ]; then
      echo "FAIL Row 17: CHANGELOG.md [$NEXT_VER] block missing or < 1500 bytes (got $CHANGELOG_BYTES)."
      echo "  Add the [$NEXT_VER] block to CHANGELOG.md before tagging."
      echo "  Skipping this gate would publish to PyPI then fail at the release-notes step,"
      echo "  forcing a move-tag re-fire (see Evidentia v0.10.3 ship incident 2026-05-23)."
    fi
  fi
fi

# Row 18 (NEW v5): branch-protection bypass audit.
# Parses the `git push` remote output for "Bypassed rule violations"
# AFTER the push completes. Always logged; never fails. Surfaces in
# per-run JSON bypass_events[] + Step 7.10 MEMORY.md entry.
#
# Implementation note: the actual bypass capture happens in the
# skill's tool layer (it owns the `git push` invocation). This
# runbook stub documents the check for non-skill invocations.
if [ -f .local/pre-release-review/last-push-output.txt ]; then
  if grep -q "Bypassed rule violations" .local/pre-release-review/last-push-output.txt; then
    echo "AUDIT Row 18: branch-protection bypass detected on last push."
    echo "  Capturing to .local/pre-release-review/runs/<latest>.json bypass_events[]."
    # The Python helper for actually appending the event:
    python -m pre_release_review.bypass_audit --log-from .local/pre-release-review/last-push-output.txt
  fi
fi

# Row 19 (NEW v5): documentation freshness gate per doc-inventory.yaml.
# Hard-fails on stale in-scope docs unless DOC FRESHNESS BYPASS phrase
# was logged earlier in the session. See documentation-freshness.md.
if [ -f .local/pre-release-review/doc-inventory.yaml ]; then
  if ! python -m pre_release_review.doc_freshness --check; then
    echo "FAIL Row 19: documentation-freshness gate (see output above)."
    echo "  Either review the flagged docs OR ack the bypass:"
    echo "    DOC FRESHNESS BYPASS — <reason>"
  fi
fi

# Row 20 (NEW v5.1; 1O): OSPS-QA-05 binary-in-VCS check.
# Detects ELF / Mach-O / PE32 / PE32+ binaries committed to VCS.
# Allowlist via config.yaml `binary_in_vcs_allowlist: [path, ...]`
# for legitimate fixtures (test binaries, icons, etc.).
# Closes OpenSSF OSPS-QA-05 at all maturity levels.
ALLOWLIST="$(python -c 'import yaml; print(" ".join(yaml.safe_load(open(".local/pre-release-review/config.yaml")).get("binary_in_vcs_allowlist", [])))' 2>/dev/null || echo '')"
BINARIES="$(git ls-files | while read -r f; do
  # Skip if explicitly allowlisted
  for allowed in $ALLOWLIST; do
    [ "$f" = "$allowed" ] && continue 2
  done
  # Skip non-existent (rare; race condition with deletes)
  [ -f "$f" ] || continue
  file --brief --mime-type "$f" | grep -qE '^application/(x-executable|x-mach-binary|vnd\.microsoft\.portable-executable)$' && echo "$f"
done)"
if [ -n "$BINARIES" ]; then
  echo "FAIL Row 20: binaries detected in VCS (OSPS-QA-05 violation):"
  echo "$BINARIES" | sed 's/^/  /'
  echo "  Either remove the file(s), use Git LFS, or add to config.yaml binary_in_vcs_allowlist[]."
fi
```

## Windows-specific fallbacks

If `uv run pytest` fails with "trampoline failed to canonicalize
script path" (a known uv issue when the venv was created on a
different shell), invoke directly via
`./.venv/Scripts/python.exe -m pytest`. Same pattern for mypy /
ruff.

## Monorepo `uv build` note

`uv build` from a workspace root may build only the workspace
meta-package, not all member packages. For multi-package repos,
the `--all-packages` flag is needed to build all members; verify
by inspecting `dist/` for all expected wheels.

## STOP rules

**STOP** if any check fails. Fix in-place; never bypass. Never
`--no-verify`.

For pre-tag releases, additionally run the irreversible-action
checks in Step 6.C (3-pass scour grep, external service review,
`gh search commits` email-leak audit).

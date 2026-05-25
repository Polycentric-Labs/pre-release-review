# Steps 3–4: Commit re-test + capability matrix

## Step 3 — Re-test every commit since the prior tag with enterprise lens

Goal: validate that every commit in the upcoming release does what
its message claims, with enterprise-grade implementation quality.

### 3.1 Mandatory `/security-review` invocation (NEW in v4 per G12)

**Run BEFORE commit-by-commit re-read.** The `/security-review`
builtin is diff-scoped per call; at Step 3 it runs against
`<prev-tag>..HEAD` to surface security-relevant findings the
reviewer should keep in mind during the per-commit pass.

```
/security-review
```

The skill's built-in prompt scopes to current-branch changes; pass
the diff range explicitly if you need a custom scope. Capture
findings in the per-run JSON log + the in-progress
`docs/security-review-vX.Y.Z.md` deliverable (CRITICAL/HIGH go to
the bug-bucket; MEDIUM/LOW are noted but deferred).

See [security-review-integration.md](security-review-integration.md)
for the 3-invocation pattern across Steps 3, 4, 6.C.

### 3.2 `/code-review` auto-fire trigger evaluation (NEW in v4)

Evaluate the 4 triggers at Step 3 entry:

```bash
prev_tag="$(git describe --tags --abbrev=0)"
diff_range="${prev_tag}..HEAD"

# Trigger 1: new public API/CLI/route
git diff "$diff_range" -- '*/routers/*.py' '*/cli/*.py' '*/schemas.py' \
  | grep -cE '^\+.*(@router\.|@app\.|@cli\.command|class.*BaseModel)' || true

# Trigger 2: new file under packages/*/src/
git diff --diff-filter=A --name-only "$diff_range" -- 'packages/*/src/'

# Trigger 3: >500 lines changed
git diff --shortstat "$diff_range" | awk '{print $4 + $6}'

# Trigger 4: security-relevant subsystem touched
git diff --name-only "$diff_range" \
  | grep -E 'security/|network_guard|oscal/(signing|sigstore)|secret|audit'
```

If ANY trigger fires, run `/code-review` against the diff. See
[code-review-integration.md](code-review-integration.md) for
per-trigger handling + opt-out pattern.

### 3.3 Per-commit re-read

For each commit in `git log --oneline <prev-tag>..HEAD`:

1. `git show --stat <sha>` — files-touched
2. Read the touched files; verify the change matches the commit
   message
3. Look for enterprise-grade gaps:
   - typed exception handling vs bare `except`
   - `@with_retry` for transient failures
   - structured logging via the project's audit module
   - audit-trail metadata on outputs
   - BLIND_SPOTS-style explicit-scope-limit lists for collectors
4. Validate documentation discrepancies (counts, claims) with
   grep + Bash
5. Check inter-package version pins are atomically updated (the
   bug-prone step — version field bumped without the inter-package
   dep range bumped → within-release version mismatch for raw pip
   users)
6. Check supply-chain dep ranges aren't allowing compromised
   versions

### 3.4 Scope expansion per Q1.4 answer

Per the user's scope choice in Step 1.4:

| Q1.4 answer | Step 3 behavior |
|---|---|
| Diff + dependency closure | After per-commit re-read, identify every file imported by a touched file (1-hop). Re-read those files for downstream-impact. |
| Full re-read | After per-commit, re-read every file in `packages/*/src/`. Catches drift unrelated to the diff. |
| Diff only | Per-commit re-read only; rely on `/security-review` at Step 4 to compensate for breadth. |
| Other | Honor the user's specific narrowing/expansion. |

### 3.5 Categorize findings into 4 buckets

| Bucket | Definition | Action |
|---|---|---|
| **CRITICAL** | Blocks a credibility-relevant release claim, OR introduces a security vulnerability, OR breaks downstream installs | Fix in-step before proceeding |
| **HIGH** | Real enterprise-grade gap but design-decision-laden | Defer to next release with explicit design-rationale doc |
| **MEDIUM** | Documentation accuracy, internal consistency, code-quality | Bundle into Step 5.A single fix commit |
| **LOW** | Nice-to-have | Document with "won't fix" rationale or accept |

CVSS / CWE / EPSS columns mandatory on all SECURITY-related
findings — see [bug-bucketing.md](bug-bucketing.md).

### 3.6 Verification gate (G6)

Before advancing to Step 4:

- Lines-reviewed / lines-changed coverage ≥ user-set threshold
  (default 100% for diff scope, ≥ 80% for closure scope)
- All commits in `<prev-tag>..HEAD` have a checkmark in the per-run
  log
- All CRITICAL findings have an associated commit fixing them OR
  an explicit "deferred-to-vX.Y.Z+1" note with risk acceptance

### 3.7 STOP for approval

After fixes land: re-run `pytest -q` + `mypy --strict-optional` +
`ruff check .` + `uv build --all-packages` + `uvx twine check
dist/*`.

**STOP for approval** before applying any CRITICAL fix or before
advancing to Step 4.

---

## Step 4 — Full capability test (functional + code review + adversarial + DAST)

Goal: per the user's depth choice, test every public capability
surface in the project. v4 makes this **mandatory on every minor
release** (v3 allowed skip-by-reuse).

### 4.1 Mandatory `/security-review-scoped` invocation (REWORKED v5 per Q3)

v4 specified a second `/security-review` invocation scoped per
subsystem, but the builtin auto-scopes to current-branch-vs-main
diff and doesn't accept a custom scope arg — so this invocation was
effectively skipped in 4 consecutive Evidentia v0.10.x cycles.

v5 uses [security-review-scoped-wrapper.md](security-review-scoped-wrapper.md)
to make the per-subsystem invocation actually run. The wrapper
accepts an explicit file list:

```
/security-review-scoped --label "ai-features" \
    --files packages/evidentia-ai/src/evidentia_ai/risk_statements.py \
            packages/evidentia-ai/src/evidentia_ai/eval/dfa_harness.py
```

Default subsystem partition per project-shape (operator can override
in `.local/pre-release-review/config.yaml` per
[security-review-scoped-wrapper.md §Per-subsystem partitioning](security-review-scoped-wrapper.md#per-subsystem-partitioning-default-step-4-list)):

- AI features (LLM call paths, structured-output validation,
  caching, air-gap behavior)
- Cryptographic signing + verify pipelines (GPG / Sigstore /
  digest checks)
- Secret-scrubber regex coverage
- Collectors / integrations (typed catches, retry, credential
  handling)
- Network-egress code (any direct socket open; SSRF surfaces)

Each subsystem invocation produces its own findings list. Append
to `docs/security-review-vX.Y.Z.md` under a `## /security-review-scoped
(Step 4 invocation #2) — <label>` sub-section.

**Patch-release shortcut**: for patch releases where the diff is
small + entirely within one subsystem, the builtin's diff-scoped
Step 3 invocation IS the per-subsystem check. The skill detects
this + skips Step 4 invocation #2 with explicit log.

### 4.2 Capability matrix output

**`docs/capability-matrix.md`** — 5 risk tiers + 5 surface tiers
covered, each row ✅/⚠/❌ with notes, plus the 5-bucket bug
categorization.

Risk-first ordering (most security-relevant first):

1. AI features
2. Cryptographic signing + verify pipelines
3. Air-gap enforcement (any `--offline` flag and its dependencies)
4. Secret-scrubber regex coverage
5. Collectors / integrations
6. Output formats + exporters (round-trip via reference impls
   if available)
7. CLI commands
8. REST API (HTTP probe via TestClient per route)
9. Web UI pages (Vitest + DAST per §4.4)
10. Configuration precedence chain (CLI > env > yaml > default)

### 4.3 Adversarial probing per surface

Per surface tier:

- bad input (oversized, malformed, encoding errors)
- missing dependency
- network failure (timeout, refusal, partial response)
- expired credential
- malformed config
- concurrent request / race condition
- large-input DoS

### 4.4 DAST runtime probing (NEW in v4 per G11)

Mandatory on releases that touch the API or UI surface:

- **Schemathesis** against the FastAPI OpenAPI spec
  (`schemathesis run http://localhost:8000/openapi.json
  --checks all`)
- **Playwright** against `evidentia serve` for XSS / CSRF /
  open-redirect probes (test corpus in `tests/dast/playwright/`)
- **Race-condition probe** on stateful endpoints (e.g.,
  `/api/gap/analyze` parallel hits with shared inventory)

### 4.5 Verification gate (G6)

Before advancing to Step 5:

- Surface-coverage % from capability-matrix.md ≥ 90% (every
  documented public surface has a row + ✅/⚠/❌ verdict)
- Adversarial probe coverage ≥ 6 of 7 attack vectors per surface
- DAST run completed (or explicit skip with rationale for non-API/
  non-UI releases)

### 4.6 STOP for approval

**STOP for approval** before applying CRITICAL fixes from this
step. Per-bucket actions: see Step 3.5.

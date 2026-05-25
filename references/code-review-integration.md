# `/code-review` integration (4 auto-fire triggers)

The `/code-review` skill (`engineering:code-review` plugin or
the user's custom equivalent) reviews code changes for security,
performance, and correctness. v4 wires it into Step 3 entry as
auto-fire on ANY of 4 triggers, in addition to manual invocation
on user request.

## When `/code-review` auto-fires

v5 makes the trigger patterns project-shape-aware per
[project-shape-detection.md](project-shape-detection.md). The
trigger script uses shape-specific globs (Python `*/cli/*.py` vs
Node `*/controllers/*.ts` vs Rust `crates/*/src/main.rs`).

1. **New public API / CLI / route** — diff adds a FastAPI route,
   Typer CLI command, Pydantic schema field, or top-level package
   export (Python); OR a Next.js API route handler, NestJS
   controller, Express router (Node); OR a `#[cargo::bin]`
   entry, public trait, or `#[derive(Serialize)]` struct (Rust);
   etc.
2. **New file under the project's source root** — per
   project-shape, e.g., `packages/*/src/` (Python uv-workspace),
   `apps/*/src/` + `packages/*/src/` (Node pnpm-workspace),
   `crates/*/src/` (Rust cargo-workspace)
3. **>500 lines changed** — language-agnostic; `git diff
   --shortstat <prev-tag>..HEAD` added+removed total exceeds 500
4. **Security-relevant subsystem touched** — language-specific
   patterns. Python: `security/`, `network_guard`,
   `oscal/(signing|sigstore)`, `secret`, `audit`. Node: `auth/`,
   `crypto/`, `session/`, anything matching `/api/.*sensitive/`.
   Rust: anything that derives `Deserialize` from untrusted input,
   uses `unsafe`, calls `std::process::Command::new`.

If ANY trigger fires, run `/code-review` against the diff. Each
trigger is logged with the value that fired it (e.g., "fired:
1 new public API at `routers/tprm.py:42`, 3 new source files
under `evidentia_core/security/`, 612 LOC delta").

## Per-trigger handling

| Trigger | Findings handling |
|---|---|
| New public API/CLI/route | Surface backwards-compatibility implications + breaking-change risk |
| New source file | Verify follows existing module conventions (typed exceptions, audit logging, BLIND_SPOTS doc if collector) |
| >500 LOC | Flag for HIGH-bucket items hidden in volume; explicit bisect candidates |
| Security subsystem | Cross-check against `docs/threat-model.md` STRIDE table for the touched asset |

## Opt-out pattern

User can opt out of any trigger with explicit ack:
"ack: trigger 3 skipped because <reason>". The ack + rationale
appends to the per-run JSON log.

## Trigger evaluation script

```bash
#!/usr/bin/env bash
# Run at Step 3 entry. Exits 0 if no trigger fired (skip /code-review),
# 1 if any trigger fired (run /code-review on the diff).
set -euo pipefail

PREV_TAG="${1:-$(git describe --tags --abbrev=0)}"
DIFF_RANGE="${PREV_TAG}..HEAD"
FIRED=()

# Trigger 1: new public API/CLI/route
NEW_API=$(git diff "$DIFF_RANGE" -- '*/routers/*.py' '*/cli/*.py' '*/schemas.py' \
  | grep -cE '^\+.*(@router\.|@app\.|@cli\.command|class.*BaseModel)' || true)
if [ "$NEW_API" -gt 0 ]; then
  FIRED+=("trigger-1: $NEW_API new public API additions")
fi

# Trigger 2: new file under packages/*/src/
NEW_FILES=$(git diff --diff-filter=A --name-only "$DIFF_RANGE" -- 'packages/*/src/' | wc -l)
if [ "$NEW_FILES" -gt 0 ]; then
  FIRED+=("trigger-2: $NEW_FILES new source files")
fi

# Trigger 3: >500 LOC delta
LOC=$(git diff --shortstat "$DIFF_RANGE" | awk '{print $4 + $6}')
LOC=${LOC:-0}  # default to 0 if no insertions/deletions
if [ "$LOC" -gt 500 ]; then
  FIRED+=("trigger-3: $LOC LOC changed (> 500 threshold)")
fi

# Trigger 4: security-relevant subsystem touched
SEC_FILES=$(git diff --name-only "$DIFF_RANGE" \
  | grep -cE 'security/|network_guard|oscal/(signing|sigstore)|secret|audit' || true)
if [ "$SEC_FILES" -gt 0 ]; then
  FIRED+=("trigger-4: $SEC_FILES security-subsystem files touched")
fi

if [ "${#FIRED[@]}" -gt 0 ]; then
  echo "/code-review auto-fire — $(IFS='; '; echo "${FIRED[*]}")"
  exit 1
else
  echo "/code-review skipped — no trigger fired"
  exit 0
fi
```

Save as `.local/pre-release-review/eval-code-review-triggers.sh`
(per-project; gitignored under `.local/`). The skill reads the
script's exit code + output to decide whether to invoke
`/code-review`.

## Output handling

Findings flow into the same bug-bucket pipeline as Step 3
(CRITICAL/HIGH/MEDIUM/LOW with CVSS/CWE/EPSS columns per
[bug-bucketing.md](bug-bucketing.md)). Append to
`docs/security-review-vX.Y.Z.md` under a "## /code-review
auto-fires" sub-section per
[deliverables.md](deliverables.md#docs-security-review-vxyzmd-structure-new-v4).

## Cross-check against `/security-review`

`/code-review` and `/security-review` overlap but cover different
ground:

- `/security-review` — security-specific (CodeQL-style: injection,
  deserialization, weak crypto, secret exposure)
- `/code-review` — broader (correctness, performance, edge cases,
  N+1 queries, error handling, missing tests)

Both run at Step 3 in v4 (security-review unconditional, code-review
conditional on the 4 triggers). Findings from each go into the
same bug-bucket pipeline; cross-link findings that surface in both
to avoid duplicate triage.

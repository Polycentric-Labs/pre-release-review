# External tool prerequisites

The v4 skill assumes a number of external tools are available on
the system path. Most are optional per gate row; the runbook
gracefully degrades when a tool is missing (logs WARN, skips that
specific check) but the FULL pre-tag flow expects all of them.

## Required (skill won't function without these)

| Tool | Used by | Install (Windows) | Install (Linux/macOS) |
|---|---|---|---|
| `git` | every step | `winget install Git.Git` | `apt install git` / `brew install git` |
| `python ≥ 3.10` | verification-gates.md `bc` fallback | `winget install Python.Python.3.12` | `apt install python3` / `brew install python@3.12` |
| `gh` (GitHub CLI) | rows 11, 12, 14, 16; Step 6.C external state | `winget install GitHub.cli` | `apt install gh` / `brew install gh` |

## Required for full pre-tag (gracefully degrades if missing)

| Tool | Used by | Install |
|---|---|---|
| `pypi-attestations` | Step 7.3 PEP 740 verify | `pip install pypi-attestations` |
| `osv-scanner` | Step 7.6 SBOM CVE scan + row 14 | https://github.com/google/osv-scanner/releases |
| `cosign` | Step 7.5 container verify | `winget install sigstore.cosign` / `brew install cosign` |
| `grype` (default in v5.0.1+) | Pre-push gate row 13 (container CVE) — default after Trivy supply-chain compromise CVE-2026-33634 March 2026 | `winget install Anchore.Grype` / `brew install grype` / https://github.com/anchore/grype#installation |
| `trivy` (opt-in alternative) | Pre-push gate row 13 (container CVE) — only when `config.yaml container_cve_tool: trivy` is set (post-incident-rotation accepted) | https://aquasecurity.github.io/trivy/latest/getting-started/installation/ |
| `pip-licenses` | Pre-push gate row 15 (license/SCA) | `pip install pip-licenses` |
| `docker` | Pre-push gate row 13 + Step 7.5 | https://docs.docker.com/desktop/install/windows-install/ |
| `jq` | per-run JSON parsing | `winget install stedolan.jq` / `apt install jq` |

## Required for DAST sub-step (Step 4 G11)

| Tool | Used by | Install |
|---|---|---|
| `schemathesis` | API fuzzing | `pip install schemathesis` |
| `playwright` | UI XSS/CSRF/open-redirect probes | `pip install playwright && playwright install` |

## Skill-internal pre-flight check

Run at Step 1 entry to verify availability + log degradation
warnings:

```bash
#!/usr/bin/env bash
echo "Checking external tools…"
for cmd in git python gh pypi-attestations osv-scanner cosign grype \
           pip-licenses docker jq schemathesis playwright; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ✓ $cmd"
  else
    echo "  ✗ $cmd  — install per references/tools-prerequisites.md"
  fi
done
```

Save as `.local/pre-release-review/tools-preflight.sh`. Output is
appended to the per-run JSON under `tool_availability`. The skill
flags any missing required tool as a HARD STOP at Step 1; missing
optional tools become WARN and the corresponding gate row is
skipped with rationale.

## Per-tool version pin recommendations

For reproducibility across releases, pin the tool versions used by
the skill in the project's CI (e.g., `.github/workflows/release.yml`):

| Tool | Pin pattern |
|---|---|
| `pypi-attestations` | `pypi-attestations>=0.0.16,<0.1` |
| `osv-scanner` | SHA-pin the binary in CI (see [Pinned-Dependencies §SHA-pinning](pre-push-gate.md#row-12-15)) |
| `cosign` | install `v2.x` from sigstore release page; verify via `cosign version` |
| `grype` (default v5.0.1+) | install `v0.x` from anchore/grype releases page; verify via `grype version`. Refuses to run with stale DB by default — safer than Trivy's silent-stale-DB behavior post-March-2026 incident. |
| `trivy` (opt-in) | install only when `config.yaml container_cve_tool: trivy` set; pin a post-incident version (≥ 0.69.7); verify via `trivy --version`; never pull `latest` |

The skill itself does not attempt to install these — that's the
project's responsibility. Pinning prevents version drift from
breaking the gate's commands between releases.

## Running multiple reviews in parallel via `git worktree` (NEW v5)

`/pre-release-review` doesn't manage worktrees, but it works correctly
when invoked from a worktree. When operating on multiple releases or
multiple branches concurrently (e.g., reviewing v0.10.4 + a hot-fix
branch + a long-running feature branch at the same time), use
`git worktree` to keep the reviews isolated:

```bash
# Add a worktree for the v0.10.4 review
git worktree add ../evidentia-v0.10.4 main

# Add a worktree for the hot-fix on develop
git worktree add ../evidentia-hotfix develop

# Run /pre-release-review from each, in separate Claude sessions or
# terminal panes. Per-run JSON state is isolated under each
# worktree's .local/pre-release-review/runs/
```

Why this matters:

- Each worktree has its own `.local/pre-release-review/runs/`
  directory + per-run JSON, so reviews don't pollute each other
- `git stash` operations during one review (e.g., Step 4.1 scoped
  /security-review file-list staging) don't disrupt the other
- Tag history is shared across worktrees, so `<prev-tag>..HEAD`
  resolution stays consistent

Worktree lifecycle is operator-managed; the skill makes no
assumptions about whether it's running in a worktree or the main
checkout. Per-run JSON paths are always
`.local/pre-release-review/runs/` relative to the CWD.

After the worktree's review finishes:

```bash
git worktree remove ../evidentia-v0.10.4
```

(Don't `rm -rf` the worktree directory directly — that leaves a
dangling worktree ref that Git complains about until pruned with
`git worktree prune`.)

## Python ≥ 3.11 is now a hard prereq (NEW v5)

v5 verification gates ([verification-gates.md](verification-gates.md))
+ EPSS lookup ([bug-bucketing.md](bug-bucketing.md)) +
project-shape detection ([project-shape-detection.md](project-shape-detection.md))
require **Python ≥ 3.11** for `tomllib`. The skill's Step 1
pre-flight check refuses to advance on older Python.

For projects pinned to older Python in their lockfile, the skill
runs its own gates in a 3.12 venv it creates under
`.local/pre-release-review/.gates-venv/` — the project's runtime
Python is unaffected.

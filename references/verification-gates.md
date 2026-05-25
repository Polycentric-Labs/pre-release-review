# Programmatic step-output verification gates (G6 — Python in v5)

Each step boundary has an automated verifier that must pass before
the gate opens (in addition to user STOP-for-approval). DevOps
W-model best practice: verify each level's output before advancing
to the next level. Removes "I'll just eyeball it" failure mode.

v4 used bash + jq + GNU coreutils (`paste`, `wc -w`, `bc`) which broke
on minimal Windows shells. v5 rewrites every gate in Python (already
a hard prereq per [tools-prerequisites.md](tools-prerequisites.md))
for cross-platform consistency.

## Pattern

Each gate is a self-contained Python check. The skill invokes via:

```bash
python -m pre_release_review.gates --step <N>
```

OR equivalently for inline use (the skill's tool layer can invoke the
gate as a one-liner):

```bash
python -c "from pre_release_review.gates import step_N; raise SystemExit(0 if step_N() else 1)"
```

Each `step_N()` function returns `(bool, dict)` — `(passed, metrics)`.
Metrics get appended to the per-run JSON.

## Step-2 verification

```python
def step_2() -> tuple[bool, dict]:
    """Word count + citation count + section count on positioning-and-value.md."""
    from pathlib import Path
    import re

    doc = Path("docs/positioning-and-value.md")
    if not doc.exists():
        return False, {"error": "doc missing"}

    text = doc.read_text(encoding="utf-8")
    word_count = len(text.split())
    citations = len(re.findall(r"https?://\S+", text))
    canonical_sections = {
        "Executive summary", "What it is", "Current capabilities",
        "Intellectual ancestry", "Competitive landscape", "Differentiation",
        "Industry tailwinds", "Positioning frame", "AI posture",
        "12-month direction", "Risk register", "Sources",
    }
    sections_found = sum(
        1 for section in canonical_sections
        if re.search(rf"^## {re.escape(section)}", text, re.MULTILINE)
    )

    metrics = {
        "word_count": word_count,
        "citations": citations,
        "sections_found": sections_found,
        "sections_required": 7,
    }
    passed = word_count >= 8000 and citations >= 30 and sections_found >= 7
    return passed, metrics
```

**Pass criterion**: ≥ 8000 words, ≥ 30 URL citations, ≥ 7 of the 12 canonical sections present.

**First-run leniency**: if `.local/pre-release-review/runs/` is empty AND `docs/positioning-and-value.md` was created in the current session (first-run bootstrap), the gate passes with `metrics.first_run_pass: true` — the real thresholds apply from run #2 onward.

## Step-3 verification

```python
def step_3() -> tuple[bool, dict]:
    """Lines-reviewed vs lines-changed coverage against the scope-confirmed threshold."""
    import subprocess
    import json
    from pathlib import Path

    prev_tag = subprocess.check_output(
        ["git", "describe", "--tags", "--abbrev=0"], text=True
    ).strip()
    shortstat = subprocess.check_output(
        ["git", "diff", "--shortstat", f"{prev_tag}..HEAD"], text=True
    ).strip()
    # shortstat shape: "47 files changed, 1320 insertions(+), 220 deletions(-)"
    import re
    nums = [int(m.group(1)) for m in re.finditer(r"(\d+)\s+(?:insertion|deletion)", shortstat)]
    lines_changed = sum(nums) if nums else 0

    latest_run = sorted(Path(".local/pre-release-review/runs/").glob("*.json"))[-1]
    run_data = json.loads(latest_run.read_text(encoding="utf-8"))
    lines_reviewed = sum(
        c.get("lines", 0)
        for c in run_data.get("commits", [])
        if c.get("reviewed")
    )

    scope = run_data.get("scope_target", "Diff + 1-hop dep closure")
    threshold_pct = 100.0 if "Diff only" in scope or "Diff + 1-hop" in scope else 80.0

    coverage_pct = (lines_reviewed / max(lines_changed, 1)) * 100
    metrics = {
        "lines_changed": lines_changed,
        "lines_reviewed": lines_reviewed,
        "coverage_pct": round(coverage_pct, 2),
        "threshold_pct": threshold_pct,
        "scope": scope,
    }
    return coverage_pct >= threshold_pct, metrics
```

**Pass criterion**: lines-reviewed ≥ scope-derived threshold.

## Step-4 verification

```python
def step_4() -> tuple[bool, dict]:
    """Surface-coverage % from capability-matrix.md ≥ 90%."""
    from pathlib import Path
    import re

    doc = Path("docs/capability-matrix.md")
    if not doc.exists():
        return False, {"error": "capability-matrix.md missing"}

    text = doc.read_text(encoding="utf-8")
    # Rows with a verdict marker (✅ ⚠ ❌)
    rows_with_verdict = len(re.findall(r"^\| [✅⚠❌] ", text, re.MULTILINE))
    # Total rows (any table row starting with |)
    rows_total = len(re.findall(r"^\| ", text, re.MULTILINE))
    coverage_pct = (rows_with_verdict / max(rows_total, 1)) * 100

    metrics = {
        "rows_with_verdict": rows_with_verdict,
        "rows_total": rows_total,
        "coverage_pct": round(coverage_pct, 2),
    }
    return coverage_pct >= 90, metrics
```

**Pass criterion**: surface-coverage ≥ 90%.

## Step-5 verification

```python
def step_5() -> tuple[bool, dict]:
    """`git bisect run pytest -q` (or shape-equivalent) passes across new commits."""
    import subprocess
    import json
    from pathlib import Path

    prev_tag = subprocess.check_output(
        ["git", "describe", "--tags", "--abbrev=0"], text=True
    ).strip()
    shape = json.loads(Path(".local/pre-release-review/project-shape.json").read_text())
    routes = json.loads(Path("references/_shape-routes.json").read_text())  # skill-shipped
    test_cmd = routes[shape["primary_shape"]]["test"]

    # Run bisect; success path = "no bad commits"
    try:
        subprocess.run(
            ["git", "bisect", "start", "HEAD", prev_tag],
            check=True, capture_output=True,
        )
        result = subprocess.run(
            ["git", "bisect", "run", "sh", "-c", test_cmd],
            capture_output=True, text=True,
        )
        bisect_output = result.stdout + result.stderr
        passed = "first bad commit" not in bisect_output
    finally:
        subprocess.run(["git", "bisect", "reset"], capture_output=True)

    return passed, {"bisect_output_tail": bisect_output[-500:]}
```

**Pass criterion**: no bisect-reported bad commits.

## Step-6 verification

```python
def step_6() -> tuple[bool, dict]:
    """All 19 rows of the pre-push gate pass (17 base + Row 18 bypass-audit + Row 19 doc-freshness)."""
    from pre_release_review.pre_push_gate import run_all_rows

    results = run_all_rows()
    passed = all(r.passed for r in results)
    metrics = {
        "rows_passed": sum(1 for r in results if r.passed),
        "rows_total": len(results),
        "failures": [r.row_id for r in results if not r.passed],
        "bypasses_applied": [r.row_id for r in results if r.bypassed],
    }
    return passed, metrics
```

**Pass criterion**: 19 of 19 rows pass (OR have explicit bypass per [bypass-protocol.md](bypass-protocol.md)).

## Step-7 verification

```python
def step_7() -> tuple[bool, dict]:
    """All publish-targets.yaml-derived sub-steps pass."""
    import json
    from pathlib import Path
    from pre_release_review.step7 import run_sub_steps_from_publish_targets

    targets_file = Path(".local/pre-release-review/publish-targets.yaml")
    results = run_sub_steps_from_publish_targets(targets_file)
    passed = all(r.passed for r in results)
    metrics = {
        "sub_steps_passed": sum(1 for r in results if r.passed),
        "sub_steps_total": len(results),
        "failures": [r.id for r in results if not r.passed],
    }
    return passed, metrics
```

**Pass criterion**: all publish-targets-driven sub-steps pass.

## Per-run JSON schema for gates

Each gate appends to `.local/pre-release-review/runs/<utc-iso>.json`:

```json
{
  "verification_gates": {
    "step_2": {"passed": true, "metrics": {"word_count": 12345, "citations": 47, "sections_found": 12}},
    "step_3": {"passed": true, "metrics": {"lines_changed": 612, "lines_reviewed": 612, "coverage_pct": 100.0, "threshold_pct": 100.0, "scope": "Diff + 1-hop dep closure"}},
    "step_4": {"passed": true, "metrics": {"rows_with_verdict": 47, "rows_total": 50, "coverage_pct": 94.0}},
    "step_5": {"passed": true, "metrics": {"bisect_output_tail": "..."}},
    "step_6": {"passed": true, "metrics": {"rows_passed": 19, "rows_total": 19, "failures": [], "bypasses_applied": []}},
    "step_7": {"passed": true, "metrics": {"sub_steps_passed": 12, "sub_steps_total": 12, "failures": []}}
  }
}
```

## Failure handling

If any verification gate fails:

1. STOP the skill flow
2. Surface the failure metric + threshold to the user
3. Wait for explicit "remediate-now" or "lower-threshold-with-rationale" choice
4. If lowering threshold: append explicit rationale + risk-acceptance owner to the per-run JSON
5. Resume only after the chosen action completes

## Skill-internal module

All gate functions live in `references/_gates.py` (skill-shipped, importable from the project's `.local/`-prepended PYTHONPATH at runtime). The module is pure-Python stdlib + `tomllib` (3.11+) — no third-party deps.

For projects using Python ≥ 3.11 (the v5 hard prereq per [tools-prerequisites.md](tools-prerequisites.md)), the gates run natively. For projects using older Python, the skill falls back to running them in a 3.12 venv it creates under `.local/pre-release-review/.gates-venv/`.

## Cross-platform parity

| Platform | Gate execution |
|---|---|
| Windows + uv | `uv run python -c "..."` |
| Windows + system Python | `py -3 -c "..."` |
| Linux + uv | `uv run python -c "..."` |
| Linux + system Python | `python3 -c "..."` |
| macOS + uv | `uv run python -c "..."` |
| macOS + Homebrew Python | `python3 -c "..."` |

The skill detects available Python invocations at Step 1 and picks the first viable one.

## What this replaces from v4

| v4 gate | v5 replacement |
|---|---|
| `wc -w < file` | `len(text.split())` |
| `grep -cE 'pattern' file` | `len(re.findall(pattern, text, re.MULTILINE))` |
| `paste -sd+ | python -c "..."` | direct Python list-comprehension |
| `bc` arithmetic | Python `round()` + arithmetic |
| `jq` JSON parsing | `json.loads` |
| `git bisect run pytest -q` (raw) | wrapped + cleanup-on-exception |

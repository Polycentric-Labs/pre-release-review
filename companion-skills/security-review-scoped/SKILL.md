---
name: security-review-scoped
version: 2026.05.23-v1
description: |
  Per-subsystem security review wrapper. Mirrors the builtin
  /security-review's tuned rubric but accepts an explicit file
  list via --files instead of auto-scoping to the current
  branch's diff. Created 2026-05-23 to fix the v4
  /pre-release-review Step 4 invocation #2 that was effectively
  skipped 4 Evidentia v0.10.x cycles running. Invoked by
  /pre-release-review Step 4.1; also callable directly for
  ad-hoc per-subsystem reviews.

  Usage:
    /security-review-scoped --label <subsystem-name> --files <path1> <path2> ...

  Output: same markdown finding format the builtin produces,
  prefixed with the --label for cross-referencing across multi-
  subsystem batches.
---

# /security-review-scoped (v1)

Per-subsystem security review for projects where the builtin
`/security-review`'s diff auto-scoping is the wrong shape.

> **Purpose**: solve the v4 /pre-release-review failure mode where
> Step 4 invocation #2 (per-subsystem review) was effectively
> skipped because the builtin can't accept a custom scope arg. The
> 4 Evidentia v0.10.x cycles noted "delta unchanged from Step 3;
> same 0-finding verdict applies" — the actual per-subsystem check
> never fired. This wrapper makes it fire.

## When to use this skill

- **Step 4 of /pre-release-review** — per-subsystem review against
  partitioned file lists (AI features / crypto / secret-scrubber
  / collectors / network-egress)
- **Ad-hoc per-subsystem deep-dive** — when you suspect a specific
  area needs review without scoping the whole branch diff
- **Pre-merge focus** — reviewing only the auth-touched files in
  a sprawling PR

## When NOT to use this skill

- **Standard branch-vs-main review** — use the builtin `/security-review`
  (its diff auto-scoping is what you want)
- **Full HEAD-vs-prev-tag review** — same, use the builtin
- **Reviewing a single file in isolation** — pass it directly to
  the model with a one-shot prompt; no need for the wrapper

## How it works

1. Validates each `--files` path exists + is within the project root
   (prevents path traversal)
2. `Read`s each file in full (no truncation; review needs complete
   context)
3. Builds a prompt mirroring the builtin's 8-category rubric:
   - Input Validation Vulnerabilities (SQL/XSS/path traversal/etc.)
   - Authentication & Authorization Issues
   - Crypto & Secrets Management
   - Injection & Code Execution (deserialization / eval)
   - Data Exposure (PII / debug info / etc.)
   - Plus 3 more per the builtin (cf. `/security-review` first-line
     prompt in its skill SKILL.md if visible; otherwise mirrors
     widely-published OWASP categories)
4. Applies the same false-positive filter (HARD EXCLUSIONS for DOS,
   secrets-on-disk, rate limiting, regex DOS, etc. per the
   builtin's published instruction set)
5. Returns markdown findings prefixed with `--label` for cross-
   referencing

## Output format

```markdown
## /security-review-scoped: <label>

### Vuln 1: <category> — <file>:<line>
* Severity: High / Medium / Low
* Description: ...
* Exploit Scenario: ...
* Recommendation: ...
* Confidence: 8

(or)

## /security-review-scoped: <label>

No HIGH or MEDIUM findings with confidence ≥ 8.
```

## Failure-mode handling

- CRITICAL finding → STOP, surface to operator, wait for explicit
  "fix-now" or "defer-with-rationale" choice
- File unreadable → log as `BLOCKED_BY_READ_ERROR`, surface to
  operator (do NOT silently skip)
- Model unreachable → mark "/security-review-scoped invocation
  SKIPPED — model unreachable", proceed; flag at parent skill's
  Step 6.D if /pre-release-review is the caller

## Per-run JSON additions

When invoked by /pre-release-review, output is appended to the
parent skill's per-run JSON:

```json
{
  "security_review_invocations": [
    {
      "step": 4,
      "kind": "scoped-wrapper",
      "sub_invocations": [
        {
          "label": "ai-features",
          "scope_files": ["packages/...ai/risk_statements.py", "..."],
          "findings": [...],
          "fired_at": "2026-05-23T20:30:00Z"
        }
      ]
    }
  ]
}
```

## Maintenance

The wrapper's prompt rubric should be reviewed quarterly to stay in
sync with the builtin `/security-review`'s prompt updates (which
Anthropic ships in updates to the Claude Code skill bundle). When
the builtin's prompt changes, mirror the change here.

Cross-reference: `~/.claude/skills/pre-release-review/references/security-review-scoped-wrapper.md`
for the design rationale + per-shape default partitions.

## Versioning

`v1` — initial release, mirrors the v4 / v5 era /security-review
builtin rubric. Bumping requires re-validating against the latest
builtin prompt content + extending the rubric coverage if Anthropic
adds new categories.

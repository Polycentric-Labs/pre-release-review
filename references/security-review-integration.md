# `/security-review` integration (G12)

The `/security-review` builtin scopes to the current branch's diff
per call. To get full-project coverage in v4, the skill invokes it
**3 times per pre-tag run** with 3 different scopes.

## Builtin scope limitation (important)

The `/security-review` builtin auto-detects the current branch's
diff vs. the merge-base. It does **not** accept a custom diff
range as an argument. To run it against a non-default scope, you
must construct the desired diff state in the working tree before
invoking:

- For "diff vs prev-tag" (Step 3 + Step 6.C): branch from prev-tag
  + cherry-pick all release commits + invoke; OR temporarily check
  out a tag, then re-apply the release branch on top.
- For "per-subsystem file lists" (Step 4): use `git stash` +
  `git checkout` per subsystem, OR drive the security review via
  manual prompts that point at specific files (the underlying
  Claude session can read individual files even without the builtin
  doing the diff scoping).

The simpler path most of the time: keep the working tree at HEAD
(post-release-commits, pre-tag) and rely on the builtin's default
"current branch vs main" auto-scope. The 3 invocations differ
mostly in **what findings get logged where** (Step 3 surfaces feed
the per-commit re-test bucket; Step 4 feed the capability-matrix
bucket; Step 6.C feed the final-gate bucket).

## Invocation #1 — Step 3 entry (commit-by-commit pass)

**Scope**: `<prev-tag>..HEAD` diff.

**Why**: surface security-relevant findings before the per-commit
re-read so the reviewer keeps them in mind during the deeper
inspection.

**Output handling**: append findings to the in-progress
`docs/security-review-vX.Y.Z.md` deliverable. CRITICAL/HIGH go
into the bug-bucket pipeline. MEDIUM/LOW noted but deferred.

```
/security-review
```

## Invocation #2 — Step 4 entry (capability-matrix pass) — `/security-review-scoped` (v5)

**Scope**: per-subsystem file lists (NOT diff). Run separately
against AI features, cryptographic surfaces, secret-scrubber,
collectors, etc.

**v5 change**: uses [security-review-scoped-wrapper.md](security-review-scoped-wrapper.md)
instead of the builtin. The builtin auto-scopes to current-branch
diff and can't accept a custom file list — that broke per-subsystem
invocations in v4 (effectively skipped 4 cycles running). The
wrapper accepts `--files <list> --label <subsystem-name>` and
mirrors the builtin's tuned prompt with the explicit scope.

**Why**: Step 4 is full-project, not diff. Each subsystem deserves
a dedicated review pass. The wrapper makes this actually run rather
than be noted-as-skipped.

**Output handling**: append per-subsystem findings to
`docs/security-review-vX.Y.Z.md` under
`## /security-review-scoped (Step 4 invocation #2) — <label>` sub-
sections. Cross-link from capability-matrix.md row to the
subsystem's findings list.

## Invocation #3 — Step 6.C (final pre-tag pass)

**Scope**: full HEAD vs prev-tag diff (broadest possible).

**Why**: catches anything that landed during Step 5 refinements.
Final gate before tag creation.

**Output handling**: append to `docs/security-review-vX.Y.Z.md`.
This is the last opportunity to surface a CRITICAL before the
irreversible tag.

## Failure mode handling

If `/security-review` surfaces a CRITICAL finding at any of the
3 invocations:

- STOP the skill flow
- Surface the finding to the user with full context
- Wait for explicit "fix-now" or "defer-with-rationale" choice
- Apply the chosen path before resuming
- Append the decision + rationale to the per-run JSON log

A CRITICAL finding without explicit user ack is a hard-stop on
tag creation.

## Per-run JSON schema for security-review findings

Each invocation appends to `.local/pre-release-review/runs/<utc-iso>.json`:

```json
{
  "security_review_invocations": [
    {
      "step": 3,
      "scope": "v0.7.4..HEAD",
      "started_at": "2026-04-30T10:00:00Z",
      "completed_at": "2026-04-30T10:42:00Z",
      "findings": [
        {
          "severity": "HIGH",
          "category": "py/path-injection",
          "location": "packages/foo/bar.py:42",
          "description": "...",
          "cvss_v3_1": 7.5,
          "cwe": "CWE-22",
          "epss": 0.0042,
          "disposition": "fix-now",
          "fix_commit": "abc1234"
        }
      ]
    }
  ]
}
```

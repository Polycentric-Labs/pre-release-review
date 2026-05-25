# Bypass protocol (NEW in v5)

> **Purpose**: Make the publish-without-review failure mode mechanically hard to commit. Adds Guideline #12 to the skill's binding guidelines + defines the 3 verbatim bypass phrases the user can type when bypassing one of the v5 hard rules is legitimate.

Closes the v4 failure mode where the AI driver could surface `git push` commands without `/pre-release-review` having run in the current session. The v4 skill described the order correctly (Step 6.F push happens AFTER Step 6.E approval AFTER Step 6.C gate passes), but treated each push as just another command — nothing structurally prevented an AI run from skipping the gate.

## Guideline #12 (binding; supersedes ad-hoc judgment)

> **NEVER surface `git push`, `git push --tags`, `gh pr merge`, package-publish, or any other irreversible-publish command to the user without having completed AT MINIMUM the 17-row pre-push gate (full or scoped, per the variant table) AND having the current per-run JSON freshness within 4 hours.**

This rule is mechanical, not advisory. The skill's tool-use layer is expected to refuse to emit such commands when the rule is violated. The bypass phrases below are the only escape valves.

## Evidence base for the 4-hour freshness bound (NEW in v5.1; 1G + 1T)

The 4-hour stale-review refusal threshold is a policy parameter informed by, not dictated by, research. It sits between two empirical anchor points: human-vigilance literature (which argues for stricter bounds in high-security contexts) and operational workflow friction (which argues for looser bounds in low-risk contexts).

### Human-vigilance + automation-complacency literature (1G)

| Citation | Finding | Implication for the freshness bound |
|---|---|---|
| **Parasuraman, R., & Manzey, D. H. (2010)**. *Complacency and Bias in Human Use of Automation: An Attentional Integration.* Human Factors, 52(3), 381-410. | Complacency rises with task duration; reliability of human monitoring of automated systems decays over uninterrupted vigilance windows of 30 minutes to several hours. The "first failure effect" is well-documented: humans degrade their checking behavior the longer automation appears to be working. | 4-hour ceiling is **looser** than the empirical anchor (30 min to several hours). High-risk contexts should configure stricter bounds via `1R repo_risk_tier: high`. |
| **Goddard, K., Roudsari, A., & Wyatt, J. C. (2012)**. *Automation bias: a systematic review of frequency, effect mediators, and mitigators.* Journal of the American Medical Informatics Association, 19(1), 121-127. | Automation bias (over-reliance on automated decision support) is robust across professional groups. Mitigators include forced reflection, structured override workflows, and explicit "show your work" prompts. | Bypass-phrase + reason requirement is a structural mitigator per Goddard. The reason field is NOT decorative — it forces reflection per the systematic-review evidence. |

### 2024-era AI-assisted-coding empirical findings (1T)

| Citation | Finding | Implication |
|---|---|---|
| **Cerbos, *State of AI in Engineering 2024*** | Developers using AI coding assistants were 19% slower at task completion yet *believed* themselves to be faster. Subjective speed bias is large + persistent. | Operators may resist the freshness ceiling because they "feel" fast — the bound is calibrated against measured behavior, not perception. |
| **CodeRabbit, *Q3 2024 PR Health Report*** | AI-generated PRs had 10.83 issues/PR vs 6.45 for human-only PRs (1.68× more issues), and approximately 1.4-1.7× more *critical*-severity findings. | AI-assisted code is empirically associated with higher issue densities. The freshness bound compounds this: a stale review approving fresh AI-generated changes is doubly risky. |
| **Apiiro, *AI Code Risk Report (2024)*** | AI-generated code introduced 322% more privilege-escalation paths and 153% more design flaws than human-only code at matched function counts. | Permission-and-design changes deserve **stricter** freshness (closer to `medium_risk` tier) even if the project's general risk tier is low. |

### Net policy stance

The 4-hour default is **conservative, not under-justified**:

- **Longer** than known early vigilance-decrement intervals (Parasuraman & Manzey 2010: 20-60 min)
- **Short enough** to prevent stale approvals carrying across a full afternoon of context drift + fatigue
- **Generous** by general vigilance-literature standards for high-security contexts — hence the v5.1 1R repo-risk-tier parameterization that lets high-risk projects tighten to 1-hour refusal

The 1T-cited AI-coding-specific evidence (Cerbos / CodeRabbit / Apiiro) does NOT have a direct paper establishing an empirical bound for HITL freshness windows on AI-generated code — that publishable gap is tracked at Tier 3 #3O in v3 audit (instrument per-run JSONs across 5-10 cycles to capture elapsed Step 6 sign-off → Step 7 commit times). Until that primary research exists, the 4-hour bound is informed-extrapolation, honestly framed.

## Three verbatim bypass phrases

Each phrase must appear in the user's own message verbatim — paraphrases do NOT count. The bypass is logged to the per-run JSON `bypass_events[]` with full context.

### B1 — `PUSH TO MAIN BYPASS AUTHORIZED`

**Scope**: any push to a protected branch (per Q2 generalization — applies to any branch the project marks as protected, not just `main`; project-shape detection reads GitHub branch-protection rules to identify the set).

**When legitimate**:
- Hot-fix push when the full review would delay an active production incident
- Documentation-only push when the typo-fix has been verified by hand
- Recovery push (e.g., the v0.10.3 move-tag re-fire)

**When NOT legitimate**:
- "I'm in a hurry" — run the pre-push variant (2-4 hours)
- "It's just a small change" — the pre-push gate alone (rows 1-17) takes < 10 minutes

**Logged**: `{type: "push-bypass", phrase: "PUSH TO MAIN BYPASS AUTHORIZED", target_branch: "main", reason: "<user-provided>", ...}`

### B2 — `STALE REVIEW ACCEPTED — <reason>`

**Scope**: a `/pre-release-review` per-run JSON exists but exceeds the freshness threshold per the project's `repo_risk_tier` setting (NEW v5.1; 1R).

**Pass criteria for the threshold (v5.1 risk-tier-parameterized)**:

| `repo_risk_tier` (config.yaml) | Warn after | Refuse after | Typical use |
|---|---|---|---|
| `high` | 15 min | 1 hour | Production-critical financial / health / safety systems |
| `medium` | 1 hour | 2 hours | Customer-facing infrastructure, regulated industries |
| `low` (default) | 2 hours | 4 hours | Internal tooling, OSS libraries, early-stage products |

For projects without an explicit `repo_risk_tier` setting, defaults to `low` (4-hour ceiling).

**Context-sensitive invalidation (NEW v5.1; 1S)** — regardless of clock-time, the per-run JSON is INVALIDATED (treated as if expired) if ANY of:

1. New commits have landed on the reviewed branch since `completed_at`
2. CI / SAST / SCA / Scorecard results have materially changed (any new HIGH+ finding, or any change in passing-test count) since `completed_at`
3. The approving reviewer is also primary author of large AI-generated changes in the diff — high-risk tier projects require either stricter staleness (15-min) OR a second human reviewer (which is the OSPS-GV-04 / QA-07 honest-gap territory for solo dev)

Context-sensitive invalidation hard-fails the freshness gate; bypass requires the B2 phrase. The skill's per-run JSON tracks `invalidation_triggers[]` so the audit log captures WHY the JSON was treated as stale (not just that it was).

**When legitimate**:
- Same-day continuation of a long review session
- Re-shipping a release that failed Step 7 verification (the review is still valid; only the publish needs retry)

**Logged**: `{type: "stale-review-bypass", age_hours: 5.2, repo_risk_tier: "medium", invalidation_triggers: ["new_commits", "scorecard_delta"], original_run_id: "...", reason: "<user-provided>"}`

**When legitimate**:
- Same-day continuation of a long review session
- Re-shipping a release that failed Step 7 verification (the review is still valid; only the publish needs retry)

**Logged**: `{type: "stale-review-bypass", age_hours: 5.2, original_run_id: "...", reason: "<user-provided>"}`

### B3 — `DOC FRESHNESS BYPASS — <reason>`

**Scope**: pre-push gate Row 19 (documentation-freshness gate per [documentation-freshness.md](documentation-freshness.md)) flagged a stale in-scope doc.

**When legitimate**:
- Doc owner is unavailable + this release is patch-only
- The flagged doc is genuinely not affected by this release (refine `scope_triggers` in `doc-inventory.yaml` after the bypass)

**When NOT legitimate**:
- "Docs aren't that important" — they are, that's why this gate exists
- "I'll do it next release" — that's the staleness-stacking failure mode the gate prevents

**Logged**: `{type: "doc-freshness-bypass", stale_docs: [...], reason: "<user-provided>"}`

## Protected-branch auto-suggestion (Q2 follow-on)

When project-shape detection (`references/project-shape-detection.md`) at Step 1 discovers that the project has NO protected branches configured, the skill surfaces a suggestion at Step 1.7 (plan approval STOP):

```
WARNING: This project has no GitHub branch-protection rules configured.
Direct pushes to main currently bypass review by default. The v5 skill
recommends setting up protection on `main` (or your equivalent default
branch) before continuing.

Suggested protection (per OpenSSF Best Practices Silver):
  - Require pull request reviews before merging
  - Dismiss stale reviews when new commits are pushed
  - Require status checks to pass: test.yml, verify-changelog.yml,
    /pre-release-review per-run JSON freshness
  - Restrict who can push to matching branches
  - Do not allow bypassing the above (admins included)

Proposed setup command:
  gh api -X PUT repos/<owner>/<repo>/branches/main/protection \
    -F required_pull_request_reviews.required_approving_review_count=1 \
    -F required_pull_request_reviews.dismiss_stale_reviews=true \
    -F required_status_checks.strict=true \
    -F required_status_checks.contexts[]=test \
    -F enforce_admins=true \
    -F restrictions=null

Choose: (1) apply now, (2) defer with rationale, (3) skip permanently
        (logged to .local/pre-release-review/config.yaml).
```

The skill does NOT auto-apply the protection (it's a publishing-authority-protocol mutation per `~/.claude/CLAUDE.md`). User explicitly approves the `gh` mutation per the global rule.

## Bypass-event audit

All B1/B2/B3 events feed into the per-run JSON:

```json
{
  "bypass_events": [
    {
      "type": "push-bypass",
      "phrase_received": "PUSH TO MAIN BYPASS AUTHORIZED",
      "target_branch": "main",
      "reason": "v0.10.3 move-tag re-fire after CHANGELOG backfill",
      "timestamp": "2026-05-23T18:11:06Z",
      "head_sha_at_bypass": "c0ed3ad..."
    }
  ]
}
```

Step 7.10 memory update appends bypass events to the project's
`MEMORY.md` SHIPPED entry so the audit trail survives across sessions.

Bypass count over time is a quality metric — high counts signal that
the gate thresholds are wrong (too strict) OR that workflow discipline
is slipping. The skill flags bypass-rate > 1 per release at the
quarterly cadence review as a process smell.

## Quarterly cadence + Guideline #12 freshness (QA-2 resolution)

The Quarterly cadence variant runs Steps 2 + 4 + doc-inventory
drift only — no Steps 6/7. But Guideline #12 still applies to any
push that surfaces during or after a Quarterly run (e.g., the
operator pushes a positioning-doc update). Resolution:

- Quarterly runs produce `runs/<id>-quarterly.json` (suffix
  `-quarterly` distinguishes from full-pre-tag JSON)
- Same 4-hour freshness rule applies — a quarterly run's JSON is
  valid as a push gate for 4 hours after `completed_at`
- A Quarterly run satisfies Guideline #12 for pushes scoped to the
  files Step 2/4 actually re-validated (positioning doc, capability
  matrix). For pushes of OTHER files (e.g., a code change touched
  during the Quarterly session), the operator needs either:
  - A separate Pre-push variant run, OR
  - The B1 bypass phrase with rationale

This prevents Quarterly from being used as a soft-bypass for code
pushes that weren't actually reviewed.

## What this does NOT replace

Per the global `~/.claude/CLAUDE.md` publishing-authority protocol,
every irreversible-publish command STILL requires explicit per-action
user approval. The bypass phrases address ORDER (review-before-push),
not AUTHORIZATION (user-says-yes-before-push). Both gates stand.

# Steps 1–2: Process review + project review

## Step 1 — Process review + capability selection + scope-confirm + bug-fix policy

Goal: align on what's being done, by what, with what depth, and with
what handling for findings — before any parallel research or test
work begins.

### 1.0 Project-shape detection + first-run bootstrap (NEW v5)

Run [project-shape-detection.md](project-shape-detection.md) FIRST —
detects language / build system / publish targets / branch-protection
state, persists to `.local/pre-release-review/project-shape.json`.

If the first-run condition holds per
[first-run-bootstrap.md](first-run-bootstrap.md), invoke the
wizard before Step 1.1. The wizard generates skeletons + the
`.local/pre-release-review/config.yaml` + initial
`doc-inventory.yaml` + initial `publish-targets.yaml`. Operator
confirms each artifact before write (Q4 ask-before-write).

On subsequent runs, Step 1.0 silently re-validates the persisted
shape state; user is re-prompted only if a signal changed (e.g., a
new lockfile appeared).

### 1.1 Acknowledge the binding guidelines

Restate the [12 binding guidelines](../SKILL.md#the-12-binding-guidelines-apply-at-every-step)
in writing at the start of the session. v5 adds **Guideline #12**
per [bypass-protocol.md](bypass-protocol.md) — the mechanical hard
rule that the AI cannot surface push commands without a fresh
gate. This anchors expectations + catches any drift on Day 2 of a
multi-session review.

### 1.2 Disclose what's already public

State the irreversible-state baseline so the user knows what is and
isn't reversible:

- Commits already pushed to origin (`git log origin/main..HEAD` for
  unpushed; `git log origin/main` for pushed)
- Tags already pushed (`git tag --sort=-creatordate | head -10`)
- Packages already published (`gh release list --limit 5`; PyPI
  search for the project name)
- Container images already published (`docker manifest inspect
  ghcr.io/<owner>/<image>:<tag>` if applicable)

### 1.3 List capabilities + ask which to use

List available tools relevant to the review:

- Built-in: `Bash`, `Edit`, `Write`, `Read`, `Grep`, `Glob`,
  `WebSearch`, `WebFetch`, `Agent` (general-purpose, Explore, Plan)
- MCP: Perplexity research/reason/ask, Hugging Face, gh API
- Skills: `/security-review` (mandatory at multiple steps),
  `/code-review` (auto-fire on triggers), `research-resync`,
  `commit`

Ask the user to confirm the relevant subset for this run.

### 1.4 Scope-confirm prompt (NEW in v4 — runs every time)

Per the user's standing direction, this prompt runs at every skill
invocation — no skip-by-reuse for scope confirmation:

> "How wide should this run's code/test re-read be?
>
> 1. **Diff + dependency closure** — re-read touched files + every
>    file they import (1-hop). Recommended for minor releases.
> 2. **Full re-read of every source file** in `packages/*/src/`.
>    Recommended for major bumps + first 'enterprise-grade' claims.
> 3. **Diff only**, with `/security-review` compensating. Recommended
>    for hot-fixes + same-day patches.
> 4. **Other** — narrow or expand (e.g., 'diff + 2-hop closure',
>    'subsystem X full but rest diff', 'skip Step 3 entirely, this
>    is docs-only')."

Record the answer in the per-run log
`.local/pre-release-review/runs/<utc-iso>.json`. Future audits can
cite the scope choice.

### 1.5 Threat-model existence check (NEW in v4)

Refuse to advance past Step 1 on a **minor** release if either:

- `docs/threat-model.md` is missing, OR
- The doc's last-modification time is > 180 days ago

Action: prompt the user to either (a) refresh the threat model
inline (block the review until done), or (b) ack the staleness as
an explicit risk-acceptance with rationale logged to the per-run
JSON.

This gate aligns with **CISA Secure by Design Pledge** + **OpenSSF
Best Practices Badge silver-level** requirements for documented
threat modeling.

### 1.5.1 Protected-branch state check (NEW v5 per Q2 follow-on)

After project-shape detection (1.0) populates
`.local/pre-release-review/protected-branches.txt`, check the list.

If empty AND the project has a recognizable default branch (`main`
/ `master` / `develop`), surface the protected-branch auto-suggestion
per [bypass-protocol.md §Protected-branch auto-suggestion](bypass-protocol.md#protected-branch-auto-suggestion-q2-follow-on)
at Step 1.7 plan approval. Operator can apply now, defer with
rationale, or skip permanently (logged to
`.local/pre-release-review/config.yaml`).

Skill never auto-applies the protection — it's a publishing-authority-
protocol mutation per `~/.claude/CLAUDE.md` requiring explicit
per-action approval.

### 1.5.2 Per-run JSON freshness check (NEW v5 per #4)

If `.local/pre-release-review/runs/` contains a JSON whose
`completed_at` is < 4 hours old, the skill notes "review in progress"
and offers to **resume** that run rather than start fresh. This
prevents accidental loss of work on multi-session reviews.

If a per-run JSON exists but is > 4 hours old AND the operator is
about to surface push commands without re-running the gate, the
skill REFUSES per Guideline #12 (see [bypass-protocol.md §B2](bypass-protocol.md#b2--stale-review-accepted--reason)).

WARN at > 2 hours; REFUSE at > 4 hours.

### 1.6 Bug-fix policy

Recommended defaults (tunable per project):

- **Sub-pass ordering**: risk-first (security-relevant surfaces,
  then collectors, then CLI/REST/UI, then formats/config)
- **Bug-fix policy**: surface + queue + keep testing; defer all
  fixes to a single batch at end of each step

Confirm the defaults or let the user override.

### 1.7 STOP for plan approval

Surface a brief plan summarizing:

- Variant chosen
- Scope chosen (Q1.4 answer)
- Capabilities to use
- Expected step boundaries + STOP gates
- Time estimate

**STOP** for explicit user approval before launching parallel work.

---

## Step 2 — Project review (positioning, value, world-class direction)

Goal: build a comprehensive understanding of what the project is,
why it exists, where it sits in its market, what's foundational
vs bleeding-edge vs unclaimed-gap, and where it should go to be
world-class.

### 2.1 Skip-by-reuse criteria

See [variants.md §"Step 2 skip-by-reuse criteria"](variants.md#step-2-skip-by-reuse-criteria-unchanged-from-v3).

If skipped: add a one-line note to the existing
`docs/positioning-and-value.md`'s version-history section + log
the skip-by-reuse decision to the per-run JSON.

### 2.2 If running fresh — research streams

Launch 6–7 parallel research agents covering:

1. **Commercial competitive landscape** — funding rounds, M&A, AI
   features, license posture, real differentiators
2. **OSS ecosystem** — per-project profiles: stars, last-commit,
   language, license, adjacency (competes-with / complements /
   depends-on / obsoletes)
3. **Industry signals + regulatory + M&A** — forcing-function
   dates, market sizing, consolidation pressure, conferences,
   macro trends
4. **Academic + scholarly research** — foundational papers, current
   SOTA, named scholars, research gaps that this project could fill
5. **AI/LLM tools in the domain** — foundational vs bleeding-edge
   vs gap; HF datasets/models that exist or are missing
6. **Industry voices** — top 10 to follow / top 5 to cite / top 5
   to pitch — named individuals with URLs
7. **Internal capability inventory** via Explore agent — every CLI
   / API / web page / library function / config knob the project
   exposes

### 2.3 Synthesis structure

Output: **`docs/positioning-and-value.md`** — exhaustive (target
~10,000–15,000 words for a substantive project), with TL;DR
section summaries at the top of each section.

Required sections:

- Executive summary (≤10 bullets)
- What it is + why it exists + design principles + buyer personas
- Current capabilities (this version)
- Intellectual ancestry (the research streams this project draws
  from — name the canonical paper)
- Competitive landscape (per-tier with profiles)
- Differentiation (genuine), parity (don't oversell), honest gaps
  (with planned remediation or "won't fix" rationale)
- Unclaimed gaps this project fills (the differentiation spine)
- Industry tailwinds + headwinds
- Positioning frame (one memorable line — e.g., "the Terraform of
  GRC")
- AI posture (foundational vs bleeding-edge vs gap; ranked
  contribution opportunities)
- Voices to cite/follow/pitch
- 12-month direction
- Risk register
- Sources (50+ URLs)

### 2.4 Verification gate (NEW in v4 per G6)

Before advancing to Step 3, the per-step verifier checks:

- Word count ≥ 8,000
- Citation count (URL refs) ≥ 30
- All 7 required sections present (parsed by `## ` header)
- Last-modified date is today or yesterday (catches stale-saved
  drafts)

See [verification-gates.md §Step-2](verification-gates.md#step-2-verification).

### 2.5 STOP for approval + memory

**STOP for approval** before committing the doc. After approval:

- `git add docs/positioning-and-value.md && git commit -m "docs(positioning): refresh for vX.Y.Z release"`
- Add a `MEMORY.md` pointer file referencing the in-repo doc
- Append decision + word-count + citation-count to the per-run JSON

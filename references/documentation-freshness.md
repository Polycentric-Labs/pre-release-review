# Documentation freshness guarantee (NEW in v5 per Q11)

> **Purpose**: Allen's standing requirement — *"I never want to have to worry about stale documentation again."* v4 had no inventory of per-project docs + no per-release audit. Doc decay accumulated silently until someone happened to read an out-of-date doc and notice. v5 adds a per-project inventory + scope-triggered review + a hard staleness gate.

## Sub-system at a glance

| Component | Lives at | Role |
|---|---|---|
| Inventory | `.local/pre-release-review/doc-inventory.yaml` | Per-project authoritative list of all docs with policy metadata |
| Bootstrap | [first-run-bootstrap.md](first-run-bootstrap.md) | Generates the inventory on first run by scanning `docs/**/*.md` + repo-root `*.md`; walks operator through `owner` + `staleness_policy` + `must_match_version` for each doc |
| Step 5.C iteration | [steps-5-6.md](steps-5-6.md) §5.C | For each in-scope doc not yet touched this release, surface "review this doc?" prompt |
| Pre-push gate Row 19 | [pre-push-gate.md](pre-push-gate.md) | Hard-fails the gate when in-scope `staleness_policy: every-release` docs OR `must_match_version: true` docs are stale |
| Step 7.10 update | [step-7-post-tag.md](step-7-post-tag.md) §7.10 | Updates `last_reviewed_version` + `last_reviewed_sha` + `last_reviewed_date` for every doc touched this cycle |
| Bypass phrase | [bypass-protocol.md](bypass-protocol.md) §B3 | `DOC FRESHNESS BYPASS — <reason>` for legitimate one-time bypass |

## Inventory schema

```yaml
# .local/pre-release-review/doc-inventory.yaml
schema_version: 1
last_audited_at: 2026-05-23T20:30:00Z
last_audited_version: v0.10.4

docs:
  - path: docs/positioning-and-value.md
    owner: <maintainer>
    scope_triggers:
      - "competitive-landscape"
      - "src/evidentia_*/ai/**"
      - any-minor-bump        # special: in-scope on every minor or larger
    last_reviewed_version: v0.10.3
    last_reviewed_sha: c0ed3ad
    last_reviewed_date: 2026-05-23
    staleness_policy: 3-releases   # warn after 3 releases without review
    refresh_required_on: [minor, major]
    must_match_version: false      # version-string in doc need not equal current

  - path: docs/release-checklist.md
    owner: <maintainer>
    scope_triggers: [any-release]
    last_reviewed_version: v0.10.3
    staleness_policy: every-release
    refresh_required_on: [patch, minor, major]
    must_match_version: true       # doc MUST reference the current version

  - path: docs/threat-model.md
    owner: <maintainer>
    scope_triggers:
      - "src/evidentia_*/security/**"
      - "src/evidentia_*/oscal/(signing|sigstore)/**"
      - any-180-days   # special: in-scope when > 180 days stale (G5 alignment)
    last_reviewed_version: v0.10.0
    staleness_policy: 6-releases
    refresh_required_on: [minor, major]
    must_match_version: false

  - path: README.md
    owner: <maintainer>
    scope_triggers:
      - any-release
      - "src/evidentia/cli/**"   # README often documents CLI
    last_reviewed_version: v0.10.4
    staleness_policy: every-release
    refresh_required_on: [patch, minor, major]
    must_match_version: true     # README badges / status / version callouts

  - path: CHANGELOG.md
    owner: <maintainer>
    scope_triggers: [any-release]
    last_reviewed_version: v0.10.4
    staleness_policy: every-release
    refresh_required_on: [patch, minor, major]
    must_match_version: true
```

### Field semantics

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | Repo-relative path; must exist on disk at audit time |
| `owner` | string | yes | Identity responsible for review; defaults to `git config user.name` at bootstrap |
| `scope_triggers` | list[string] | yes | Glob patterns + special tokens; ANY match → doc is in-scope for this release |
| `last_reviewed_version` | string | yes | Set at Step 7.10; immutable except by skill |
| `last_reviewed_sha` | string | no | Optional commit SHA at review time |
| `last_reviewed_date` | ISO date | yes | Updated by Step 7.10 |
| `staleness_policy` | enum | yes | `every-release` / `N-releases` (where N is integer) / `N-days` |
| `refresh_required_on` | list[enum] | yes | Subset of `[patch, minor, major]` — bump shapes that trigger required-refresh |
| `must_match_version` | bool | yes | If true, doc must reference current version somewhere (regex-detected); enforced by Row 19 |

### Special tokens in `scope_triggers`

| Token | Means |
|---|---|
| `any-release` | In scope for every release |
| `any-minor-bump` | In scope when bump is minor or major |
| `any-major-bump` | In scope when bump is major only |
| `any-180-days` | In scope when doc is > 180 days unreviewed (aligns with G5 threat-model staleness rule) |
| `<glob>` | Standard git-pathspec; checked against `git diff --name-only <prev-tag>..HEAD` |
| `<string>` | Free-text substring; checked against commit messages in `<prev-tag>..HEAD` range |

## Step 5.C iteration logic

```python
# Pseudocode for Step 5.C doc-review iteration
inventory = load_inventory(".local/pre-release-review/doc-inventory.yaml")
diff_files = git_diff_name_only(prev_tag, "HEAD")
commit_messages = git_log_messages(prev_tag, "HEAD")
bump_shape = compute_bump_shape(prev_tag, target_version)  # patch/minor/major

for doc in inventory.docs:
    if doc.path was already touched in this release:
        # Operator already updated it; mark reviewed.
        update_last_reviewed(doc, version=target_version, sha=current_head)
        continue

    in_scope = (
        any_glob_or_string_match(doc.scope_triggers, diff_files, commit_messages)
        or special_token_match(doc.scope_triggers, bump_shape, doc.last_reviewed_date)
    )

    if in_scope:
        prompt_user(f"In-scope doc {doc.path} (owner={doc.owner}) needs review. "
                    f"Last reviewed at {doc.last_reviewed_version}. "
                    f"Options: (1) review now, (2) skip with rationale, (3) defer to next release")
        # On (1): open editor; record review; update last_reviewed_*
        # On (2): log to per-run JSON; check Row 19 doesn't hard-fail this doc
        # On (3): log; this counts toward staleness_policy
```

## Pre-push gate Row 19 enforcement

Row 19 fails when ANY of the following holds for ANY doc in the inventory:

1. `staleness_policy: every-release` AND doc not touched in this release
2. `staleness_policy: N-releases` AND (current_release - last_reviewed) > N
3. `staleness_policy: N-days` AND (today - last_reviewed_date) > N
4. `must_match_version: true` AND the doc text does NOT contain a string matching the current version regex (e.g., `v0.10.4` or `0.10.4`)
5. `refresh_required_on` includes the current bump shape AND doc not touched in this release

### Row 19 implementation

```python
# pre-push-gate Row 19 helper
def check_doc_freshness(inventory, current_version, prev_tag, bump_shape) -> list[Violation]:
    violations = []
    touched = set(git_diff_name_only(prev_tag, "HEAD"))

    for doc in inventory.docs:
        if not Path(doc.path).exists():
            violations.append(f"{doc.path} listed in inventory but missing on disk")
            continue

        is_touched = doc.path in touched

        # Policy 1: every-release
        if doc.staleness_policy == "every-release" and not is_touched:
            violations.append(f"{doc.path} (every-release policy) not touched in v{current_version}")

        # Policy 2: N-releases
        if match := re.match(r"(\d+)-releases", doc.staleness_policy):
            n = int(match.group(1))
            if releases_since(doc.last_reviewed_version, current_version) > n:
                violations.append(f"{doc.path} ({n}-release policy) stale since {doc.last_reviewed_version}")

        # Policy 3: N-days
        if match := re.match(r"(\d+)-days", doc.staleness_policy):
            n = int(match.group(1))
            if (today - doc.last_reviewed_date).days > n:
                violations.append(f"{doc.path} ({n}-day policy) stale {(today - doc.last_reviewed_date).days} days")

        # must_match_version
        if doc.must_match_version:
            content = Path(doc.path).read_text(encoding="utf-8")
            if not re.search(rf"\bv?{re.escape(current_version)}\b", content):
                violations.append(f"{doc.path} (must_match_version) does not reference v{current_version}")

        # refresh_required_on
        if bump_shape in doc.refresh_required_on and not is_touched:
            violations.append(f"{doc.path} (refresh_required_on={doc.refresh_required_on}) not touched on {bump_shape} bump")

    return violations
```

Bypass: `DOC FRESHNESS BYPASS — <reason>` per [bypass-protocol.md §B3](bypass-protocol.md#b3--doc-freshness-bypass--reason).

## First-run inventory wizard

Per [first-run-bootstrap.md](first-run-bootstrap.md), the wizard walks the operator through inventory construction:

```
Found these .md files in the repo:
  1. README.md
  2. CHANGELOG.md
  3. docs/release-checklist.md (just generated by bootstrap)
  4. docs/security-review-v0.1.0.md (just generated)
  5. docs/threat-model.md (just generated)
  6. docs/positioning-and-value.md (just generated)

For each, I need to know:
  - Owner (default: <maintainer> — git config user.name)
  - Staleness policy (every-release / N-releases / N-days)
  - Refresh required on (patch / minor / major bump shapes)
  - Must-match-version (does the doc need to reference the current version?)

Walking through doc 1 of 6: README.md
  Owner [<maintainer>]: <ENTER>
  Staleness policy [every-release / 3-releases / 90-days]: every-release
  Refresh required on [patch+minor+major / minor+major / major]: patch+minor+major
  Must match current version (Y/n) [n]: y
    → README badges/status banners reference v0.10.4 — will fail Row 19 if not bumped
  Confirm? [Y/n]: y
  Saved.

Walking through doc 2 of 6: CHANGELOG.md
  ...
```

Q11 hard requirement: **the user MUST be asked which docs must match version** — no defaults that assume yes/no.

## Discovery + delta over time

Each run, the skill re-scans `docs/**/*.md` + repo-root `*.md`:

- **New docs detected** → surface "Add to inventory? Owner / policy / ..."
- **Inventoried docs missing on disk** → surface "Remove from inventory? It was deleted in <sha>"
- **Operator-edited docs without skill knowledge** → surface "Doc <path> was touched outside the skill; mark reviewed as of <commit>?"

Discovery loop runs at Step 1 entry; deltas surfaced before bootstrap exits (or as a non-blocking note on subsequent runs).

## Cross-references

- [first-run-bootstrap.md](first-run-bootstrap.md) — generates the initial inventory
- [steps-5-6.md](steps-5-6.md) §5.C — runs the iteration
- [pre-push-gate.md](pre-push-gate.md) Row 19 — enforces
- [step-7-post-tag.md](step-7-post-tag.md) §7.10 — updates last_reviewed_*
- [bypass-protocol.md](bypass-protocol.md) §B3 — escape valve

## Compliance alignment

Adding documentation freshness as a structural gate aligns with:

- **ISO 27001:2022** A.5.31 (Documentation of policies and procedures — kept current)
- **NIST SSDF** PO.4 (Documentation produced + maintained)
- **SOC 2 Type II** CC1.5 (Documentation that demonstrates continued operation of controls)
- **OpenSSF Best Practices Badge** Silver level (project description + interface + security MUST be current)

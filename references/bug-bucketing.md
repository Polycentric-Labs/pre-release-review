# Bug-bucket categorization (CVSS/CWE/EPSS — semi-auto in v5)

## The 4 buckets (unchanged from v3/v4)

| Bucket | Definition | Action |
|---|---|---|
| **CRITICAL** | Blocks a credibility-relevant release claim, OR introduces a security vulnerability, OR breaks downstream installs | Fix in-step before proceeding |
| **HIGH** | Real enterprise-grade gap but design-decision-laden | Defer to next release with explicit design-rationale doc |
| **MEDIUM** | Documentation accuracy, internal consistency, code-quality | Bundle into Step 5.A single fix commit |
| **LOW** | Nice-to-have | Document with "won't fix" rationale or accept |

## NEW v5: semi-automated CVSS / CWE / EPSS

For any **security-related** finding, the bug-bucket table gains 3 columns mapping to industry vocabulary. v4 required manual lookup of all three; v5 automates 2 of the 3 and provides a helper for the manual one.

| Column | Source | Range | v5 automation |
|---|---|---|---|
| **CVSS v3.1** (or v4.0) | https://www.first.org/cvss/ | 0.0–10.0 | **Manual** + vector-builder helper (no public API for the calculator) |
| **CWE** | https://cwe.mitre.org/ | CWE-N | **Auto-populate** from `/security-review` output when it provides the CWE (it usually does in `category: <slug>`) |
| **EPSS** | https://api.first.org/data/v1/epss?cve=<CVE> | 0.0–1.0 probability | **Auto-lookup** via FIRST.org API when CVE assigned; cached 24h to `.local/pre-release-review/epss-cache.json` |

This makes findings audit-defensible per **NIST SSDF PW.5** + **ISO 27001:2022 Annex A 8.27** + **SOC 2 Type II CC7.1**.

## EPSS auto-lookup (NEW v5)

```python
# pre_release_review/epss.py
import json
import time
import urllib.request
from pathlib import Path

CACHE_FILE = Path(".local/pre-release-review/epss-cache.json")
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def lookup_epss(cve_id: str) -> dict:
    """Return {'score': float, 'percentile': float, 'fetched_at': float} for a CVE.

    Cached locally so a single review run doesn't re-query the API
    for every finding referencing the same CVE.
    """
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}

    if cve_id in cache:
        entry = cache[cve_id]
        if time.time() - entry["fetched_at"] < CACHE_TTL_SECONDS:
            return entry

    # FIRST.org EPSS API — free, no auth required
    url = f"https://api.first.org/data/v1/epss?cve={cve_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        if data.get("data"):
            row = data["data"][0]
            entry = {
                "score": float(row["epss"]),
                "percentile": float(row["percentile"]),
                "fetched_at": time.time(),
                "source": "first.org/epss",
            }
        else:
            # CVE not yet scored by EPSS
            entry = {"score": None, "percentile": None, "fetched_at": time.time(), "source": "first.org/epss:no-data"}
    except (urllib.error.URLError, TimeoutError) as exc:
        entry = {"score": None, "percentile": None, "fetched_at": time.time(),
                 "source": f"error:{type(exc).__name__}"}

    cache[cve_id] = entry
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return entry
```

API contract is documented at https://www.first.org/epss/api. Free, no auth, rate-limited to ~1/sec which is fine for review-time use.

## CWE auto-populate from `/security-review` (NEW v5)

The builtin `/security-review` skill outputs each finding with a `Category: ` field like:

```
# Vuln 1: SQL injection: foo.py:42
* Severity: High
* Description: ...
* Category: sql_injection
```

The skill ships a slug→CWE mapping table that auto-populates the CWE column:

```python
# pre_release_review/cwe_map.py
CATEGORY_TO_CWE = {
    "sql_injection": "CWE-89",
    "command_injection": "CWE-78",
    "xss": "CWE-79",
    "csrf": "CWE-352",
    "path_traversal": "CWE-22",
    "path_injection": "CWE-22",
    "ssrf": "CWE-918",
    "xxe": "CWE-611",
    "deserialization": "CWE-502",
    "pickle_injection": "CWE-502",
    "yaml_deserialization": "CWE-502",
    "template_injection": "CWE-94",
    "code_execution": "CWE-94",
    "weak_crypto": "CWE-327",
    "hardcoded_credential": "CWE-798",
    "open_redirect": "CWE-601",
    "regex_dos": "CWE-1333",
    "polynomial_redos": "CWE-1333",
    "stack_trace_exposure": "CWE-209",
    "log_injection": "CWE-117",
    "incomplete_url_substring_sanitization": "CWE-20",
    "broken_authentication": "CWE-287",
    "broken_authorization": "CWE-285",
    "jwt_vulnerability": "CWE-345",
    "session_management": "CWE-384",
    "memory_safety": "CWE-787",
    "race_condition": "CWE-362",
    # ... extend as new categories surface
}
```

If `/security-review` reports a category not in the map, the skill surfaces a prompt: "Unmapped category `<slug>`; assign CWE manually?" — operator answers, the map is auto-extended.

## CVSS vector-builder helper (NEW v5)

No public CVSS calculator API exists. The skill provides an interactive helper that walks the operator through the 8 base metrics + emits the vector string + base score:

```python
# pre_release_review/cvss.py
def build_cvss_vector_interactively() -> dict:
    """Walk the operator through CVSS v3.1 base metrics.

    Returns:
        {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
         "base_score": 9.8,
         "severity": "CRITICAL"}
    """
    metrics = {}
    metrics["AV"] = ask("Attack Vector: (N)etwork / (A)djacent / (L)ocal / (P)hysical")
    metrics["AC"] = ask("Attack Complexity: (L)ow / (H)igh")
    metrics["PR"] = ask("Privileges Required: (N)one / (L)ow / (H)igh")
    metrics["UI"] = ask("User Interaction: (N)one / (R)equired")
    metrics["S"]  = ask("Scope: (U)nchanged / (C)hanged")
    metrics["C"]  = ask("Confidentiality Impact: (N)one / (L)ow / (H)igh")
    metrics["I"]  = ask("Integrity Impact: (N)one / (L)ow / (H)igh")
    metrics["A"]  = ask("Availability Impact: (N)one / (L)ow / (H)igh")

    vector = "CVSS:3.1/" + "/".join(f"{k}:{v}" for k, v in metrics.items())
    base_score, severity = _compute_cvss3_base(metrics)   # standard formula
    return {"vector": vector, "base_score": base_score, "severity": severity}
```

For pre-scored CVEs, the skill auto-fetches from NVD (https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=<CVE>) and skips the interactive walk.

## Qualitative FAIR Loss Magnitude column (NEW v5.1; 1F)

FAIR (Factor Analysis of Information Risk) gives a structured frame for *consequence* that CVSS doesn't capture — CVSS scores *exploitability + technical impact*; FAIR estimates *financial / operational consequence*. v5.1 adds a qualitative FAIR Loss Magnitude column to the bug-bucket table. Use FAIR-LITE qualitative bins, not a full quantitative Monte Carlo:

| FAIR LM bin | Description | Typical CVSS pair | Typical disposition |
|---|---|---|---|
| **Critical** | Existential-class loss: regulatory fine triggering ROI failure, large customer exodus, IP exfil of crown jewels | CVSS 9.0+ on Internet-exposed surface, or any CVSS 7+ touching PII / billing / auth | Hard ship-block; fix-or-revert |
| **High** | Material loss: noticeable customer-trust dent, multi-day operational disruption, > $10k direct cost | CVSS 7+ on internal surface OR 5+ on Internet-exposed | Fix-in-step (Step 5.A bundle) |
| **Medium** | Workflow-friction loss: a workaround exists; loss is hours not days; < $10k direct cost | CVSS 4-7 on internal surfaces | Bundle to next minor; document workaround |
| **Low** | Cosmetic / quality loss: no operational or financial impact | CVSS < 4 OR docs / quality findings | Accept with rationale; track count |

**v5.1 stance**: this is QUALITATIVE FAIR. A full quantitative FAIR analysis (PERT distributions for Loss Event Frequency × Loss Magnitude, Monte Carlo to get a Value-at-Risk curve) is out of scope for solo-dev / OSS reviews — it requires more historical data than typical projects have. The qualitative bins capture the FAIR insight ("severity is two dimensions, not one") without the analytical overhead. See https://www.fairinstitute.org/ for the full framework.

## Sample row format

```
| ID | Bucket | Category | Location | CVSS v3.1 | CWE | EPSS | FAIR LM | Disposition |
|---|---|---|---|---|---|---|---|---|
| F-001 | CRITICAL | py/path-injection | gaps.py:48 | 7.5 (HIGH) | CWE-22 | 0.0042 (auto-fetched 2026-05-23) | High | fix-in-S1 (commit 6dfbe27) |
| F-002 | HIGH | py/polynomial-redos | catalog.py:42 | 5.3 (MEDIUM) | CWE-1333 | 0.0011 | Medium | fix-in-S2 (commit 691e096) |
| F-003 | MEDIUM | py/stack-trace-exposure | integrations.py:60 | 4.3 (MEDIUM) | CWE-209 | 0.0008 | Low | fix-in-S3 (commit 3196702) |
| F-004 | LOW | doc-accuracy | README.md:142 | n/a | n/a | n/a | Low | accepted-as-is |
```

## Per-bucket actions (extended in v4, unchanged in v5)

- **CRITICAL** — STOP-and-fix at any of: Step 3 entry, Step 4 entry, Step 6.C, or Step 7. No tag without resolution.
- **HIGH** — defer to v(X.Y.Z+1) plan with explicit design rationale + risk-acceptance owner + target re-check date. Logged to per-run JSON.
- **MEDIUM** — bundle into Step 5.A single fix commit.
- **LOW** — document with "won't fix" rationale OR accept and move on. Track count over time as a quality metric.

## Skill-shipped vs project-side

The `epss.py` + `cvss.py` + `cwe_map.py` modules ship inside the skill at `~/.claude/skills/pre-release-review/lib/`. Projects don't need to install anything beyond stdlib + Python 3.11+ (for `tomllib`). The EPSS cache lives per-project at `.local/pre-release-review/epss-cache.json`.

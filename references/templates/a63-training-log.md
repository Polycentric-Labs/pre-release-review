# ISO 27001 A.6.3 training-currency log (bootstrap-emitted; 1D in v5.1)

> Closes ISO 27001:2022 Annex A.6.3 (Information security awareness, education and training) for solo-dev OSS projects. Also addresses NIST SP 800-218A PO.2.2 (role-based training, with AI-coding-assistant lens). Append a new entry every time a training or awareness activity completes.

## Why this exists

A.6.3 requires "personnel, including external party users, who have access to the organization's information shall receive appropriate information security awareness, education and training and regular updates of organizational policies and procedures, as relevant for their job function." For a solo-dev OSS project, "personnel" = the maintainer; "training" = self-directed learning. Honest documentation of the activity is the only viable attestation.

For AI-coding-assistant training (218A PO.2.2), include any reading / courses / certifications related to AI-assisted code production risks (prompt injection, IP exfil via prompts, AI-generated-code review patterns, etc.).

## Log entries (append-only)

### YYYY-MM-DD — <topic>

- **Activity**: <e.g., "Read OWASP LLM Top 10 v2.0", "Completed Coursera 'Secure Coding for AI Assistants'", "Attended OpenSSF Day 2026">
- **Duration**: <hours>
- **Source / URL**: <link>
- **Key learnings applied**: <what changed in the project as a result>
- **Next refresh**: <YYYY-MM-DD or "annual">

<!-- ↑ duplicate this section per entry, newest at top -->

## Minimum cadence

| Topic | Min frequency |
|---|---|
| OWASP Top 10 (web) refresh | Annual |
| OWASP LLM Top 10 (AI) refresh | Annual |
| Project's primary language secure-coding patterns | Annual |
| CVE feed scanning practice | Quarterly |
| Threat-modeling refresh (STRIDE / PASTA / similar) | Annual |
| AI-coding-assistant risk awareness (Apiiro / CodeRabbit / Cerbos 2024 papers) | Semi-annual (rapidly evolving) |

## Verification at /pre-release-review

The pre-push gate (Step 1 process review) checks this log's most-recent entry. If the freshest entry is > 12 months old for any required topic, the gate WARNS (does not block); maintainer must either add a new entry or explicitly bypass via `STALE REVIEW ACCEPTED — training-currency-deferred` per `references/bypass-protocol.md`.

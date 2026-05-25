# `/security-review-scoped` wrapper (NEW in v5 per Q3)

> **Purpose**: solve the v4 problem where Step 4's `/security-review` invocation #2 was effectively skipped because the builtin auto-detects current-branch-vs-main diff and doesn't accept a custom scope argument. v5 ships a thin wrapper that uses `Read` + an explicit prompt mirroring the builtin's behavior, accepting an explicit file list for per-subsystem scoping.

## Why the wrapper exists

The `/security-review` builtin's value is its tuned security-review prompt + its consistency with `claude.ai/code`-style review output. But its scope is hardcoded to the current branch vs main merge-base. Step 4 of `/pre-release-review` needs per-subsystem invocations against specific file lists (AI features / cryptographic surfaces / secret-scrubber / collectors) — the builtin's auto-scoping can't do that.

In all 4 Evidentia v0.10.x cycles, the v4 skill noted "delta unchanged from Step 3; same 0-finding verdict applies" — Step 4 invocation #2 never actually ran. The skill was passing audit-defensibility paperwork rather than running the check.

v5 builds a 3-state pattern:

1. **Step 3 invocation #1** — uses the builtin directly (scope = diff = exactly what the builtin auto-detects). Unchanged from v4.
2. **Step 4 invocation #2** — uses `/security-review-scoped` per subsystem.
3. **Step 6.C invocation #3** — uses the builtin directly (scope = full HEAD vs prev-tag = the builtin's default). Unchanged from v4.

## The wrapper

`/security-review-scoped` is a thin skill under `~/.claude/skills/security-review-scoped/` (or per-project under `.claude/skills/`). It accepts:

```
/security-review-scoped --files path1.py path2.py --label "subsystem-name"
```

Or via stdin with a heredoc file list:

```
/security-review-scoped --label "ai-features" <<EOF
packages/evidentia-ai/src/evidentia_ai/risk_statements.py
packages/evidentia-ai/src/evidentia_ai/eval/dfa_harness.py
EOF
```

### Internals

The wrapper:

1. Validates each path exists and is within the project root
2. `Read`s each file in full
3. Builds a prompt that mirrors `/security-review`'s rubric (the same 8 categories: input validation / authn-authz / crypto + secrets / injection + code-exec / data exposure / etc.) plus the same false-positive filter
4. Invokes the model with the assembled context
5. Returns the same markdown finding format the builtin produces, prefixed with the `--label` for cross-referencing

### Output handling

Per the v4 pattern in [security-review-integration.md](security-review-integration.md):

- CRITICAL/HIGH → bug-bucket pipeline
- MEDIUM/LOW → noted but deferred to v(X.Y.Z+1)-plan.md
- Findings append to `docs/security-review-vX.Y.Z.md` under a `## /security-review-scoped (Step 4 invocation #2) — <label>` sub-section
- Per-run JSON logs the invocation: `{step: 4, sub_invocation: 2, label: "<label>", scope_files: [...], findings: [...]}`

## Per-subsystem partitioning (default Step 4 list)

The v5 skill uses the project-shape to drive a default partition. For Python projects, the default partition is:

| Label | File pattern |
|---|---|
| `ai-features` | `packages/*-ai/**/*.py`, `**/llm_*.py`, `**/risk_statements.py`, `**/eval/*.py` |
| `crypto` | `**/signing.py`, `**/sigstore.py`, `**/digest.py`, `**/verify.py` |
| `secret-scrubber` | `**/scrubber.py`, `**/audit/*.py` (where structured logging touches PII) |
| `collectors` | `packages/*-collectors/**/*.py` |
| `network-egress` | `**/_block_private_ips.py`, anything that opens a socket directly |

Operator can override per-project in `.local/pre-release-review/config.yaml`:

```yaml
step_4_subsystem_partition:
  ai-features: ["packages/evidentia-ai/**/*.py"]
  crypto: ["packages/evidentia-core/src/evidentia_core/oscal/*.py"]
  secret-scrubber: ["packages/evidentia-core/src/evidentia_core/audit/scrubber.py"]
  collectors: ["packages/evidentia-collectors/src/**/*.py"]
  network-egress: ["**/_block_private_ips.py"]
  custom-tprm: ["packages/evidentia-core/src/evidentia_core/vendor_store.py"]
```

### Per-shape default partitions (v5 ships defaults for 10 shapes)

#### Node (pnpm-workspace + Next.js/NestJS/Express)

| Label | File pattern |
|---|---|
| `auth-session` | `**/auth/**/*.{ts,tsx,js}`, `**/middleware/auth*.{ts,js}`, `**/session*.{ts,js}`, `apps/*/lib/auth.{ts,js}` |
| `api-handlers` | `apps/*/api/**/*.{ts,js}`, `apps/*/app/api/**/route.{ts,js}`, `**/controllers/*.{ts,js}` |
| `crypto` | `**/crypto/*.{ts,js}`, `**/jwt*.{ts,js}`, `**/sign*.{ts,js}`, `**/encrypt*.{ts,js}` |
| `secret-scrubber` | `**/logger*.{ts,js}`, `**/scrub*.{ts,js}`, anything that touches `process.env.*SECRET` |
| `client-state` | `apps/*/app/**/*.{tsx}` using `'use client'`, `**/store/*.{ts,tsx}`, server-action handlers |
| `network-egress` | `**/fetch*.{ts,js}`, `**/api-client/*.{ts,js}`, anything that constructs URLs from user input |

#### Rust (cargo workspace)

| Label | File pattern |
|---|---|
| `unsafe-blocks` | every `*.rs` containing `unsafe ` (grep at partition time) |
| `crypto` | `crates/*/src/crypto/**/*.rs`, anything calling `ring::`, `rustcrypto::`, `sodiumoxide::`, `aes::` |
| `network` | `crates/*/src/net/**/*.rs`, `crates/*/src/http/**/*.rs`, anything using `reqwest::`, `hyper::`, `tokio::net::` |
| `deserialization` | any file with `#[derive(Deserialize)]` on a type that comes from untrusted input |
| `ffi` | `crates/*/src/ffi/**/*.rs`, `extern "C"` blocks |
| `command-execution` | files calling `std::process::Command::new`, `tokio::process::Command::new` |

#### Go

| Label | File pattern |
|---|---|
| `http-handlers` | `**/handlers/**/*.go`, `**/routes/**/*.go`, anything implementing `http.Handler` |
| `crypto` | `**/crypto/**/*.go`, anything importing `crypto/`, `golang.org/x/crypto/` |
| `auth` | `**/auth/**/*.go`, `**/middleware/auth*.go`, `**/jwt*.go` |
| `command-execution` | files calling `os/exec.Command` (`exec.Command` / `exec.CommandContext`) |
| `path-handling` | files using `filepath.Join` with user-supplied components |
| `sql` | files calling `db.Query`, `db.Exec`, `sqlx.*` with non-parameterized strings (grep + manual review) |

#### Java (Maven/Gradle)

| Label | File pattern |
|---|---|
| `controllers` | `**/src/main/java/**/*Controller.java`, `**/*Resource.java` (JAX-RS) |
| `auth` | `**/src/main/java/**/security/**/*.java`, `**/Authentication*.java`, `**/Authorization*.java` |
| `crypto` | `**/src/main/java/**/crypto/**/*.java`, anything using `javax.crypto.*`, `Bouncycastle` |
| `serialization` | files using `ObjectInputStream`, `XStream`, `Jackson` with default typing enabled |
| `sql` | files using `PreparedStatement.execute*` with concatenated SQL strings, or `EntityManager.createQuery` raw |
| `command-execution` | files calling `Runtime.getRuntime().exec`, `ProcessBuilder` |

#### Ruby (Rails / standalone)

| Label | File pattern |
|---|---|
| `controllers` | `app/controllers/**/*.rb` |
| `auth` | `app/controllers/**/sessions_controller.rb`, `**/authentication.rb`, Devise overrides under `config/initializers/devise.rb` |
| `crypto` | `**/encryption/**/*.rb`, anything using `OpenSSL::Cipher`, `bcrypt`, `Sorcery::CryptoProviders` |
| `serialization` | files using `YAML.load` (not `safe_load`), `Marshal.load` on untrusted input |
| `sql` | files using `Model.find_by_sql`, raw `connection.execute` |
| `command-execution` | files using backticks, `system`, `exec`, `Open3.popen3` with untrusted input |

#### Elixir (Phoenix / Plug)

| Label | File pattern |
|---|---|
| `controllers` | `lib/*_web/controllers/**/*.ex` |
| `plugs` | `lib/*_web/plugs/**/*.ex` (custom Plugs handle auth + sanitization) |
| `crypto` | `lib/**/crypto/**/*.ex`, anything using `:crypto`, `Phoenix.Token`, `Guardian` |
| `serialization` | files using `Plug.Crypto.non_executable_binary_to_term/1` vs `:erlang.binary_to_term/1` (the latter is RCE-prone) |
| `genservers-with-state` | any GenServer holding user-attributable session/auth state |

#### PHP (Laravel / Symfony / standalone)

| Label | File pattern |
|---|---|
| `controllers` | `app/Http/Controllers/**/*.php`, `src/Controller/**/*.php` |
| `middleware` | `app/Http/Middleware/**/*.php`, `src/EventListener/**/*.php` |
| `auth` | `app/Auth/**/*.php`, `**/SecurityController.php`, anything using `Auth::*` facade |
| `crypto` | files using `openssl_*`, `password_hash`, `hash_hmac`, `sodium_*` |
| `sql` | files using `DB::raw`, `$pdo->query` with concatenated strings (vs prepared statements) |
| `serialization` | files using `unserialize()` on untrusted input |

#### .NET (C# / F#)

| Label | File pattern |
|---|---|
| `controllers` | `**/Controllers/**/*.cs`, `**/Endpoints/**/*.cs` (Minimal API) |
| `middleware` | `**/Middleware/**/*.cs`, `Program.cs` middleware registrations |
| `auth` | `**/Authentication/**/*.cs`, `**/Authorization/**/*.cs`, JWT bearer config |
| `crypto` | files using `System.Security.Cryptography.*`, custom `IDataProtector` implementations |
| `serialization` | files using `BinaryFormatter` (deprecated; RCE-prone), `XmlSerializer` with unknown types |

#### python-rust-hybrid (e.g., maturin projects)

Union of `python` + `rust` partitions; the wrapper runs both partition sets sequentially. Findings tagged with `--label python:ai-features` vs `--label rust:unsafe-blocks` to keep results disambiguated.

#### Maintenance

When `/security-review` (builtin) adds a new category to its rubric,
this skill's per-shape partitions should be reviewed for whether a
new label is warranted. Tracked in [maintenance.md §v5 extensions](maintenance.md#v5-specific-extensions).

## Failure-mode handling

Same as the builtin:

- CRITICAL finding → STOP, surface, wait for explicit "fix-now" or "defer-with-rationale"
- Wrapper unable to read a file → log as `BLOCKED_BY_READ_ERROR`, list the path, surface to operator (do NOT silently skip)
- Wrapper unable to reach the model → mark Step 4 as "/security-review-scoped invocation #2 SKIPPED — model unreachable", proceed; flag at Step 6.D

## Per-run JSON schema additions

```json
{
  "security_review_invocations": [
    {
      "step": 3,
      "kind": "builtin",
      "scope": "v0.10.3..HEAD",
      "findings": [...]
    },
    {
      "step": 4,
      "kind": "scoped-wrapper",
      "sub_invocations": [
        {
          "label": "ai-features",
          "scope_files": [...],
          "findings": [...]
        },
        {
          "label": "crypto",
          "scope_files": [...],
          "findings": [...]
        }
      ]
    },
    {
      "step": "6.C",
      "kind": "builtin",
      "scope": "v0.10.3..HEAD (full)",
      "findings": [...]
    }
  ]
}
```

This makes the audit-trail honest: invocations are clearly typed, the scoped runs are clearly labeled, and per-run JSON consumers (Step 7.10 auto-gen of `docs/security-review-vX.Y.Z.md`) can render the right sub-section per invocation.

## When the wrapper isn't needed

For **patch releases** where the diff is small + entirely within one subsystem, the builtin's diff-scoped Step 3 invocation IS the per-subsystem check. The skill detects this and skips Step 4 invocation #2 with explicit "patch release; Step 3 builtin already covered the only touched subsystem".

For **first-run** (per [first-run-bootstrap.md](first-run-bootstrap.md)), invocation #2 still runs — the wrapper's per-subsystem partition is exercised against the root-commit baseline so future runs have a comparison point.

## Implementation note (skill-creator pattern)

The wrapper is created via the [skill-creator skill](../../../anthropic-skills/skill-creator/SKILL.md). It's small (≈ 150 lines incl. the rubric prompt), lives under `~/.claude/skills/security-review-scoped/`, and is invokable directly OR composed via /pre-release-review's Step 4.

The wrapper's own prompt should be reviewed quarterly to stay in sync with the builtin `/security-review` rubric (which Anthropic updates). The maintenance burden is documented in [maintenance.md](maintenance.md).

## Migration from v4

v4 projects (Evidentia) had a `delta-unchanged-from-Step-3` convention. v5 migration:

1. First v5 run on a v4-shaped project surfaces the partition prompt
2. Operator confirms partition (defaults work for Evidentia per the default-partition table above)
3. Partition stored in `.local/pre-release-review/config.yaml`
4. Future runs invoke the wrapper per partition

No code changes required in the project; the migration is config-only.

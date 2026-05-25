# Project-shape detection (NEW in v5)

> **Purpose**: Make the skill portable across project types. v4 was Python/uv-shaped throughout — bug-bucketing examples cited CodeQL Python rules; verification gates assumed `packages/*/src/`; the pre-flight checked `pyproject.toml`. v5 detects the project's language + build system + branch-protection state at Step 1 and routes to the right tools per language.

Runs at **Step 1.0 entry** (before the first-run-bootstrap check). The detected shape is persisted to `.local/pre-release-review/project-shape.json` and re-used across runs unless the underlying signals change.

## Detection signals

### Language / build system (in detection order — first match wins)

| Signal | Project shape | Build system | Test runner |
|---|---|---|---|
| `pyproject.toml` exists | `python` | `uv` if `uv.lock`, else `poetry` if `[tool.poetry]`, else `setuptools`/`pdm`/`hatch` per `[build-system]` | `pytest` if any `tests/` exists; `unittest` otherwise |
| `package.json` exists | `node` | `pnpm` if `pnpm-lock.yaml`, `yarn` if `yarn.lock`, `npm` if `package-lock.json`, `bun` if `bun.lockb` | `vitest` / `jest` / `mocha` per `package.json` `scripts.test` |
| `Cargo.toml` exists | `rust` | `cargo` | `cargo test` |
| `go.mod` exists | `go` | `go` | `go test ./...` |
| `pom.xml` exists | `java-maven` | `mvn` | `mvn test` |
| `build.gradle` / `build.gradle.kts` | `java-gradle` / `kotlin-gradle` | `gradle` | `gradle test` |
| `Gemfile` exists | `ruby` | `bundler` | `rspec` / `minitest` per Gemfile |
| `mix.exs` exists | `elixir` | `mix` | `mix test` |
| `composer.json` exists | `php` | `composer` | `phpunit` / `pest` |
| `.csproj` / `.sln` exists | `dotnet` | `dotnet` | `dotnet test` |
| `Cargo.toml` + `pyproject.toml` | `python-rust-hybrid` (e.g., maturin) | per-component | per-component |
| Multiple of above | `polyglot` — record all detected; skill prompts user to pick primary | varies | varies |

### Publish-target detection (informs `publish-targets.yaml` autogen)

| Signal | Implied target |
|---|---|
| `pyproject.toml` `[project]` block + `.github/workflows/release.yml` containing `pypa/gh-action-pypi-publish` | `kind: pypi-trusted-publisher` |
| `package.json` `private: false` + `.github/workflows/*` with `npm publish` | `kind: npm` |
| `Dockerfile` + `.github/workflows/*` with `ghcr.io` | `kind: ghcr-container` |
| `Dockerfile` + `.github/workflows/*` with `docker.io` | `kind: docker-hub-container` |
| `vercel.json` OR `apps/*/vercel.json` | `kind: vercel` |
| `wrangler.toml` OR `.github/workflows/*` with `cloudflare/pages-action` | `kind: cloudflare-pages` |
| `Cargo.toml` + `.github/workflows/*` with `cargo publish` | `kind: cargo` |
| `Formula/*.rb` in a `*-tap` repo | `kind: homebrew-tap` |
| `.github/workflows/*` with `gh release create` | `kind: github-release` |

Detection is best-effort and conservative — when ambiguous, the skill asks the operator to confirm at first run. Stored in `publish-targets.yaml` for future runs.

### Branch-protection state (Q2 follow-on)

```bash
# Discover protected branches via gh (gracefully skips on no-auth)
if gh auth status >/dev/null 2>&1; then
  gh api "repos/<owner>/<repo>/branches" --paginate \
    -q '.[] | select(.protected==true) | .name' > .local/pre-release-review/protected-branches.txt
fi
```

If `protected-branches.txt` is empty AND the project has a recognizable default branch (`main` / `master` / `develop`), the skill surfaces the protected-branch auto-suggestion per [bypass-protocol.md §"Protected-branch auto-suggestion"](bypass-protocol.md#protected-branch-auto-suggestion-q2-follow-on).

## Per-shape tool routing

The detected shape drives:

- **Test gate command** (pre-push gate Row 6)
- **Lint/type gate command** (Row 7) — `ruff` + `mypy --strict` for Python, `eslint` + `tsc --noEmit` for Node, `cargo clippy` + `cargo check` for Rust, etc.
- **Build sanity command** (Row 8)
- **License/SCA command** (Row 15) — `pip-licenses` for Python, `license-checker` for Node, `cargo-license` for Rust
- **SBOM command** — `cyclonedx-py` for Python, `cyclonedx-npm` for Node, `cargo-cyclonedx` for Rust
- **Container CVE scan command** (Row 13) — **Grype default** (cross-shape; v5.0.1 switch post-Trivy-compromise CVE-2026-33634). Trivy retained as opt-in via `config.yaml container_cve_tool: trivy`
- **Reproducible-build verification** (Step 6.C.3) — `SOURCE_DATE_EPOCH` works cross-shape but the wheel/tarball/binary diff command varies
- **Fresh-venv install smoke** (Step 7.8) — `pip install` for Python, `npm install -g` for Node, `cargo install` for Rust, `gem install` for Ruby

### Routing table (excerpt — full table in `references/_shape-routes.json`)

```json
{
  "python": {
    "test": "uv run pytest -q || pytest -q",
    "lint": "uv run ruff check && uv run mypy --strict packages/",
    "build": "uv build --all-packages",
    "license": "pip-licenses --format=json",
    "sbom": "cyclonedx-py environment -o evidentia-sbom.cdx.json --of JSON --sv 1.6",
    "fresh_install_smoke": "python -m venv /tmp/fresh-VER && /tmp/fresh-VER/bin/pip install '<pkg>==VER'"
  },
  "node": {
    "test": "pnpm test || yarn test || npm test",
    "lint": "pnpm lint && pnpm exec tsc --noEmit",
    "build": "pnpm build",
    "license": "license-checker --json",
    "sbom": "cyclonedx-npm --output-file sbom.cdx.json --output-format JSON --spec-version 1.6",
    "fresh_install_smoke": "npm install -g <pkg>@VER && <bin> --version"
  },
  "rust": {
    "test": "cargo test",
    "lint": "cargo clippy --all-targets -- -D warnings && cargo fmt --check",
    "build": "cargo build --release",
    "license": "cargo license --json",
    "sbom": "cargo cyclonedx --format json",
    "fresh_install_smoke": "cargo install <crate> --version VER && <bin> --version"
  }
}
```

(Skill ships with `_shape-routes.json` covering all 11 detected shapes.)

## Per-shape paths

| Path-shape | Python | Node (pnpm-workspace) | Rust (cargo workspace) |
|---|---|---|---|
| Source root | `packages/*/src/` | `packages/*/src/` or `apps/*/src/` | `crates/*/src/` |
| Test root | `tests/` | `packages/*/tests/` or `__tests__/` | inline `mod tests` or `tests/` |
| CHANGELOG | `CHANGELOG.md` (any shape) | same | same |
| Lockfile (single source of truth) | `uv.lock` / `poetry.lock` | `pnpm-lock.yaml` / `yarn.lock` / `package-lock.json` | `Cargo.lock` |

## Persisted state — `.local/pre-release-review/project-shape.json`

```json
{
  "schema_version": 1,
  "detected_at": "2026-05-23T20:00:00Z",
  "primary_shape": "python",
  "build_system": "uv",
  "test_runner": "pytest",
  "source_paths": ["packages/*/src/"],
  "publish_targets_detected": [
    "pypi-trusted-publisher",
    "ghcr-container",
    "github-release"
  ],
  "protected_branches": ["main"],
  "polyglot_secondary": [],
  "user_confirmed": true,
  "user_confirmation_date": "2026-05-23T20:05:00Z"
}
```

Skill re-runs detection on each invocation but only re-prompts the user if a signal changed (e.g., a new lockfile appeared). Otherwise re-uses persisted state silently.

## When detection fails

If NO signal matches (greenfield repo with no lockfiles yet), the skill enters **first-run bootstrap** ([first-run-bootstrap.md](first-run-bootstrap.md)) and asks the user the shape explicitly. The answer is persisted as `user_supplied: true` in `project-shape.json`.

## Test cases for the detection itself

The skill ships a `tests/test_project_shape_detection.py` (or shape-equivalent) that exercises detection against fixture projects representing each shape. Run via `python -m pytest tests/test_project_shape_detection.py` from the skill dir.

# tidyout — Design Spec
**Date:** 2026-05-12  
**Status:** Approved

---

## What It Does

`tidyout` is a Python CLI wrapper that sits between an AI agent (Claude Code, Cursor, etc.) and the terminal. When a command is prefixed with `tidy`, tidyout:

1. Executes the real command and captures stdout + stderr
2. Looks up a strip/keep rule for the command
3. Applies the rule to compress the output
4. Prints the compressed output followed by a token savings summary

Goal: reduce token consumption in AI agent sessions by stripping human-pretty noise and returning machine-readable output.

---

## CLI Usage

```bash
tidy pytest tests/
tidy git status
tidy ls -la
tidy docker logs mycontainer
tidy init
```

Every run ends with:
```
✂️  tidyout: {original} lines → {compressed} lines | saved ~{tokens} tokens ({percent}% reduction)
```

Token estimate: `1 token ≈ 4 characters`. Savings calculated from character count difference.

---

## Architecture

```
tidy <cmd> [args]
        │
        ▼
   cli.py:main()
        │
        ├── cmd == "init" → init_agent.py
        │
        └── everything else → runner.py
                │
                ▼
         subprocess (stdout+stderr merged)
                │
                ▼
         stripper.py
                │
                ├── loads rules/<cmd>.yaml  (or no rule → pass-through)
                ├── applies strip/keep logic line-by-line
                └── computes token savings
                │
                ▼
         print output + ✂️ summary line
```

**Command detection:**
- Single-word commands: `tidy pytest tests/` → rule key `pytest`
- Two-word subcommands: `tidy git status` → rule key `git_status`, `tidy docker logs` → `docker_logs`
- No matching rule → pass-through: run command, return output as-is, still print summary line (0% reduction)

---

## YAML Rule Schema

Each file in `tidyout/rules/` follows this schema:

```yaml
strip:
  - pattern: "regex or string"
    type: regex | prefix | exact | contains

keep:
  - pattern: "..."
    type: regex | prefix | exact | contains
```

**Evaluation order per line:**
1. Matches any `keep` pattern → kept (keep always wins)
2. Matches any `strip` pattern → dropped
3. Otherwise → kept

**Special transforms** (reformatting, not just filtering) for `ls`, `git_log`, `docker_ps`, `git_status` are implemented as post-processing hooks in `stripper.py`, keyed by command name.

---

## Components

| File | Responsibility |
|---|---|
| `cli.py` | Parse `sys.argv`, detect `init`, dispatch to runner or init_agent |
| `runner.py` | `subprocess.run` with merged stdout+stderr, returns raw output string |
| `stripper.py` | Load rule YAML, apply strip/keep, run transform hooks, calculate savings |
| `init_agent.py` | Detect/create CLAUDE.md / .cursorrules, append tidyout usage block |
| `rules/*.yaml` | One file per command, declarative strip/keep patterns |

---

## Rules Inventory

| Rule file | Command | Typical savings |
|---|---|---|
| `pytest.yaml` | `pytest` | ~80% |
| `git_status.yaml` | `git status` | ~60% |
| `git_log.yaml` | `git log` | ~50% |
| `ls.yaml` | `ls` | ~70% |
| `find.yaml` | `find` | ~40% |
| `tree.yaml` | `tree` | ~50% |
| `pip_install.yaml` | `pip install` | ~90% |
| `npm_install.yaml` | `npm install` | ~85% |
| `docker_logs.yaml` | `docker logs` | ~70% |
| `docker_ps.yaml` | `docker ps` | ~60% |
| `jest.yaml` | `jest` | ~80% |
| `make.yaml` | `make` | ~40% |
| `cargo_build.yaml` | `cargo build` | ~75% |

---

## `tidy init` Behavior

- Detects `CLAUDE.md` in CWD → appends tidyout usage block
- Detects `.cursorrules` in CWD → appends tidyout usage block
- Neither exists → creates `CLAUDE.md` with the block
- Prints exactly what action was taken

**Injected block:**
```markdown
## Token Optimization with tidyout
Always prefix the following commands with `tidy` when running in terminal:
pytest, npm test, jest, rspec, git status, git log, ls, find, tree,
pip install, npm install, docker logs, docker ps, make, cargo build
This reduces token usage by 60-97% on command outputs.
```

---

## Token Savings Calculation

```python
original_chars = len(original_output)
compressed_chars = len(compressed_output)
saved_tokens = (original_chars - compressed_chars) // 4
percent = int((1 - compressed_chars / original_chars) * 100) if original_chars else 0
```

`1 token ≈ 4 characters` is the standard cross-industry rule of thumb (from OpenAI tokenizer research, also used by Anthropic). Accurate enough for an estimate.

---

## Testing

- `tests/test_stripper.py` — unit tests per rule: feed known raw output string, assert compressed output matches expected
- `tests/test_cli.py` — integration tests for `tidy init`: verify file creation/appending with correct content

---

## Packaging & Publishing

- `pyproject.toml`: package `tidyout`, version `0.1.0`, entry point `tidy = tidyout.cli:main`, Python `>=3.9`
- GitHub Actions workflow at `.github/workflows/publish.yml`: triggers on `v*.*.*` tags, runs tests, builds, publishes to PyPI via `PYPI_API_TOKEN` secret
- GitHub repo: `sathish-2000/tidyout`

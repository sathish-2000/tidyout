# tidyout

A CLI wrapper that sits between you (or your AI agent) and the terminal. Prefix any command with `tidy` and tidyout executes it, strips the noise, and returns a compressed version with a token savings summary.

```
✂️  tidyout: 312 lines → 18 lines | saved ~2376 tokens (94% reduction)
```

Built for AI coding sessions (Claude Code, Cursor, Copilot) where terminal output burns tokens fast.

## Install

```bash
pip install tidyout-cli
```

## Usage

```bash
tidy pytest tests/
tidy git status
tidy git log
tidy ls -la
tidy find . -name "*.py"
tidy docker logs mycontainer
tidy npm install
tidy cargo build
```

Every run ends with a summary line:

```
✂️  tidyout: {original} lines → {compressed} lines | saved ~{tokens} tokens ({percent}% reduction)
```

Commands without a matching rule pass through unchanged and still show the summary (0% reduction).

## Supported commands

| Command | What gets stripped | Typical savings |
|---|---|---|
| `pytest` | PASSED lines, platform info, separators | ~80% |
| `git status` | hints, up-to-date messages, blank lines | ~60% |
| `git log` | Author email, full hashes, blank lines | ~50% |
| `ls` | permissions, owner, group, timestamp — reformatted to `DIR:name` / `F:name:size` | ~70% |
| `find` | `.git/`, `node_modules/`, `__pycache__/`, `./` prefix | ~40% |
| `tree` | entries beyond depth 3, `node_modules`, `.git`, `__pycache__` | ~50% |
| `pip install` | progress bars, Collecting/Downloading, already-satisfied | ~90% |
| `npm install` | warn/notice lines, blank lines | ~85% |
| `docker logs` | health check noise, keeps last 50 lines | ~70% |
| `docker ps` | header, full IDs, padding — reformatted to `name:status:ports` | ~60% |
| `jest` | passing test names, keeps failures and summary | ~80% |
| `make` | Entering/Leaving directory noise | ~40% |
| `cargo build` | dependency Compiling lines, Downloading | ~75% |

## `tidy init` — inject rules into your AI agent config

Running `tidy init` in your project directory automatically tells your AI agent to always use `tidy`:

```bash
tidy init
```

It writes to **all** major AI agent config files at once — creating missing ones and appending to existing ones:

| File | AI tool |
|---|---|
| `CLAUDE.md` | Claude Code |
| `.cursorrules` | Cursor |
| `.windsurfrules` | Windsurf |
| `.github/copilot-instructions.md` | GitHub Copilot |

Injected block:

```markdown
## Token Optimization with tidyout
Always prefix the following commands with `tidy` when running in terminal:
pytest, npm test, jest, rspec, git status, git log, ls, find, tree,
pip install, npm install, docker logs, docker ps, make, cargo build
This reduces token usage by 60-97% on command outputs.
```

## Contributing a new rule

See [CONTRIBUTING.md](CONTRIBUTING.md) — it's just one YAML file.

from pathlib import Path

TIDYOUT_BLOCK = """
## Token Optimization with tidyout
Always prefix the following commands with `tidy` when running in terminal:
pytest, npm test, jest, rspec, git status, git log, ls, find, tree,
pip install, npm install, docker logs, docker ps, make, cargo build
This reduces token usage by 60-97% on command outputs.
"""

# All major AI IDE / agent config files
AI_CONFIG_FILES = [
    "CLAUDE.md",                          # Claude Code
    ".cursorrules",                        # Cursor
    ".windsurfrules",                      # Windsurf
    ".github/copilot-instructions.md",    # GitHub Copilot
]


def run_init():
    cwd = Path.cwd()

    for rel_path in AI_CONFIG_FILES:
        target = cwd / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            with open(target, "a") as f:
                f.write(TIDYOUT_BLOCK)
            print(f"  appended → {rel_path}")
        else:
            with open(target, "w") as f:
                f.write(TIDYOUT_BLOCK.lstrip())
            print(f"  created  → {rel_path}")

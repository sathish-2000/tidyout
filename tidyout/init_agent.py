from pathlib import Path

TIDYOUT_BLOCK = """
## Token Optimization with tidyout
Always prefix the following commands with `tidy` when running in terminal:
pytest, npm test, jest, rspec, git status, git log, ls, find, tree,
pip install, npm install, docker logs, docker ps, make, cargo build
This reduces token usage by 60-97% on command outputs.
"""


def run_init():
    cwd = Path.cwd()
    claude_md = cwd / "CLAUDE.md"
    cursorrules = cwd / ".cursorrules"

    if claude_md.exists():
        with open(claude_md, "a") as f:
            f.write(TIDYOUT_BLOCK)
        print(f"Appended tidyout rules to {claude_md}")
    elif cursorrules.exists():
        with open(cursorrules, "a") as f:
            f.write(TIDYOUT_BLOCK)
        print(f"Appended tidyout rules to {cursorrules}")
    else:
        with open(claude_md, "w") as f:
            f.write(TIDYOUT_BLOCK.lstrip())
        print(f"Created {claude_md} with tidyout rules")

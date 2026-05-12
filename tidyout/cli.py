import sys

from tidyout.runner import run_command
from tidyout.stripper import strip_output
from tidyout.init_agent import run_init


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: tidy <command> [args...]")
        print("       tidy init")
        sys.exit(1)

    if args[0] == "init":
        run_init()
        return

    raw_output, return_code = run_command(args)
    compressed, original_lines, compressed_lines, saved_tokens, percent = strip_output(args, raw_output)

    if compressed:
        print(compressed, end="" if compressed.endswith("\n") else "\n")

    print(
        f"\u2702\ufe0f  tidyout: {original_lines} lines \u2192 {compressed_lines} lines"
        f" | saved ~{saved_tokens} tokens ({percent}% reduction)"
    )

    sys.exit(return_code)

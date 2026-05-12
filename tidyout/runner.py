import subprocess


def run_command(args):
    """Execute a command, merging stdout and stderr. Returns (output, return_code)."""
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.stdout, result.returncode
    except FileNotFoundError:
        return f"tidy: command not found: {args[0]}\n", 127

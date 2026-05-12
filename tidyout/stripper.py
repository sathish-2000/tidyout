import re
from pathlib import Path

import yaml

RULES_DIR = Path(__file__).parent / "rules"


# ---------------------------------------------------------------------------
# Rule loading & matching
# ---------------------------------------------------------------------------

def get_rule_key(args):
    """Return the rule key for a command. Tries two-word key first."""
    if len(args) >= 2:
        two_word = f"{args[0]}_{args[1]}"
        if (RULES_DIR / f"{two_word}.yaml").exists():
            return two_word
    return args[0]


def load_rule(rule_key):
    """Load a YAML rule file. Returns None if no rule exists for this key."""
    rule_path = RULES_DIR / f"{rule_key}.yaml"
    if not rule_path.exists():
        return None
    with open(rule_path) as f:
        return yaml.safe_load(f)


def _matches(line, entry):
    pattern = entry["pattern"]
    ptype = entry.get("type", "contains")
    if ptype == "regex":
        return bool(re.search(pattern, line))
    if ptype == "prefix":
        return line.startswith(pattern)
    if ptype == "exact":
        return line == pattern
    # default: contains
    return pattern in line


def apply_rule(lines, rule):
    """Filter lines using strip/keep rules. keep always wins over strip."""
    strip_patterns = rule.get("strip") or []
    keep_patterns = rule.get("keep") or []

    result = []
    for line in lines:
        if any(_matches(line, p) for p in keep_patterns):
            result.append(line)
            continue
        if any(_matches(line, p) for p in strip_patterns):
            continue
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# Transform hooks (reformatting beyond simple line filtering)
# ---------------------------------------------------------------------------

def _month_num(month):
    return {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }.get(month, "??")


def transform_ls(lines):
    dirs, files = [], []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        # Long format: permissions links owner group size ... name
        if len(parts) >= 9 and line[0] in ("-", "d", "l"):
            permissions = parts[0]
            size = parts[4]
            name = " ".join(parts[8:])
            if name in (".", ".."):
                continue
            if permissions.startswith("d"):
                dirs.append(f"DIR:{name}")
            elif permissions.startswith("l"):
                link_name = name.split(" -> ")[0]
                files.append(f"L:{link_name}")
            else:
                files.append(f"F:{name}:{size}")
        else:
            files.append(line)
    return dirs + files


def transform_git_status(lines):
    result = []
    for line in lines:
        stripped = line.strip()
        if line.startswith("On branch "):
            result.append(f"branch: {line[len('On branch '):]}")
            continue
        for prefix in ("modified:", "deleted:", "new file:", "renamed:", "both modified:"):
            if stripped.startswith(prefix):
                result.append(f"{prefix} {stripped[len(prefix):].strip()}")
                break
        else:
            result.append(line)
    return result


def transform_git_log(lines):
    result = []
    cur_hash = cur_date = cur_msg = None

    for line in lines:
        if line.startswith("commit "):
            if cur_hash and cur_msg:
                result.append(f"{cur_hash} {cur_date} {cur_msg}")
            cur_hash = line.split()[1][:7]
            cur_date = cur_msg = None
        elif line.startswith("Date:"):
            date_str = line[5:].strip()
            parts = date_str.split()
            if len(parts) >= 5:
                cur_date = f"{parts[4]}-{_month_num(parts[1])}-{parts[2].zfill(2)}"
            else:
                cur_date = date_str
        elif line.startswith("    ") and cur_hash and cur_msg is None:
            cur_msg = line.strip()

    if cur_hash and cur_msg:
        result.append(f"{cur_hash} {cur_date} {cur_msg}")
    return result


def transform_docker_ps(lines):
    result = []
    col_starts = {}
    col_order = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "PORTS", "NAMES"]

    for line in lines:
        if not line.strip():
            continue
        if "CONTAINER ID" in line:
            for col in col_order:
                idx = line.find(col)
                if idx >= 0:
                    col_starts[col] = idx
            continue

        if not col_starts:
            result.append(line)
            continue

        def get_field(col):
            start = col_starts.get(col)
            if start is None:
                return ""
            col_idx = col_order.index(col)
            for next_col in col_order[col_idx + 1:]:
                if next_col in col_starts:
                    return line[start:col_starts[next_col]].strip()
            return line[start:].strip()

        name = get_field("NAMES")
        status = get_field("STATUS")
        ports = get_field("PORTS")
        if not name:
            continue
        entry = f"{name}:{status}:{ports}" if ports else f"{name}:{status}"
        result.append(entry)

    return result


def transform_find(lines):
    result = []
    for line in lines:
        line = line.strip()
        if line.startswith("./"):
            line = line[2:]
        if line and line != ".":
            result.append(line)
    return result


def _tree_depth(line):
    i = depth = 0
    while i < len(line):
        chunk = line[i:i+4]
        if chunk in ("│   ", "    "):
            depth += 1
            i += 4
        elif chunk in ("├── ", "└── "):
            depth += 1
            break
        else:
            break
    return depth


def transform_tree(lines):
    result = []
    for line in lines:
        if not line.rstrip():
            result.append(line)
            continue
        if _tree_depth(line) <= 3:
            result.append(line)
    return result


def transform_docker_logs(lines):
    # Keep last 50 lines after filtering
    if len(lines) > 50:
        return lines[-50:]
    return lines


def transform_cargo_build(lines):
    # Keep only the last "Compiling" line (the project crate itself)
    compiling = [l for l in lines if l.startswith("   Compiling ")]
    others = [l for l in lines if not l.startswith("   Compiling ")]
    if compiling:
        # Insert the last compiling line back in its original position
        last = compiling[-1]
        original_idx = lines.index(last)
        result = []
        inserted = False
        pos = 0
        for line in others:
            orig_pos = lines.index(line) if line in lines else 9999
            if not inserted and original_idx < orig_pos:
                result.append(last)
                inserted = True
            result.append(line)
        if not inserted:
            result.append(last)
        return result
    return others


TRANSFORMS = {
    "ls": transform_ls,
    "git_status": transform_git_status,
    "git_log": transform_git_log,
    "docker_ps": transform_docker_ps,
    "find": transform_find,
    "tree": transform_tree,
    "docker_logs": transform_docker_logs,
    "cargo_build": transform_cargo_build,
}


# ---------------------------------------------------------------------------
# Savings calculation
# ---------------------------------------------------------------------------

def calculate_savings(original, compressed):
    orig_chars = len(original)
    comp_chars = len(compressed)
    saved_tokens = max(0, (orig_chars - comp_chars) // 4)
    percent = max(0, int((1 - comp_chars / orig_chars) * 100)) if orig_chars else 0
    return saved_tokens, percent


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def strip_output(args, raw_output):
    """
    Apply rules and transforms to raw command output.

    Returns:
        (compressed_text, original_line_count, compressed_line_count, saved_tokens, percent)
    """
    rule_key = get_rule_key(args)
    rule = load_rule(rule_key)

    lines = raw_output.splitlines()
    original_line_count = len(lines)

    filtered = apply_rule(lines, rule) if rule is not None else list(lines)

    if rule_key in TRANSFORMS:
        filtered = TRANSFORMS[rule_key](filtered)

    compressed = "\n".join(filtered)
    if raw_output.endswith("\n"):
        compressed += "\n"

    saved_tokens, percent = calculate_savings(raw_output, compressed)

    return compressed, original_line_count, len(filtered), saved_tokens, percent

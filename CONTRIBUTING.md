# Contributing a New Rule

Adding support for a new command is just one file.

## Steps

1. Create `tidyout/rules/<command>.yaml`
2. Follow the schema below
3. Add a test in `tests/test_stripper.py`
4. Open a PR

## YAML Schema

```yaml
strip:
  - pattern: "string or regex"
    type: prefix | contains | exact | regex

keep:
  - pattern: "string or regex"
    type: prefix | contains | exact | regex
```

**`type` options:**

| Type | Behaviour |
|---|---|
| `prefix` | `line.startswith(pattern)` |
| `contains` | `pattern in line` |
| `exact` | `line == pattern` |
| `regex` | `re.search(pattern, line)` |

**Evaluation order:** `keep` always wins over `strip`. If a line matches a keep pattern it is always kept, even if it also matches a strip pattern.

## Two-word commands

For commands like `git status` or `docker logs`, name the file using an underscore:
`git_status.yaml`, `docker_logs.yaml`, `npm_install.yaml`

tidyout automatically tries the two-word key first, then falls back to the single-word key.

## Transform hooks (optional)

If the rule needs to reformat lines rather than just filter them (e.g., shorten a hash, reorder output), add a Python function in `tidyout/stripper.py` and register it in the `TRANSFORMS` dict:

```python
def transform_mycommand(lines):
    # lines: filtered output after YAML rules applied
    # return: final list of lines
    return [line.upper() for line in lines]

TRANSFORMS = {
    ...
    "mycommand": transform_mycommand,
}
```

## Example rule

`tidyout/rules/rspec.yaml` — strip passing examples, keep failures and summary:

```yaml
strip:
  - pattern: "^  \\."
    type: regex
  - pattern: "^$"
    type: exact

keep:
  - pattern: "example"
    type: contains
  - pattern: "failure"
    type: contains
  - pattern: "Failure/Error"
    type: contains
  - pattern: "rspec"
    type: contains
```

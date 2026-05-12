import pytest
from tidyout.stripper import strip_output, calculate_savings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compressed(args, raw):
    text, *_ = strip_output(args, raw)
    return text


# ---------------------------------------------------------------------------
# Token savings
# ---------------------------------------------------------------------------

def test_calculate_savings_basic():
    saved, pct = calculate_savings("a" * 400, "a" * 200)
    assert saved == 50
    assert pct == 50


def test_calculate_savings_no_change():
    saved, pct = calculate_savings("abc", "abc")
    assert saved == 0
    assert pct == 0


def test_calculate_savings_empty_original():
    saved, pct = calculate_savings("", "")
    assert saved == 0
    assert pct == 0


# ---------------------------------------------------------------------------
# Pass-through (no rule)
# ---------------------------------------------------------------------------

UNKNOWN_OUTPUT = "hello world\nfoo bar\nbaz\n"


def test_passthrough_returns_output_unchanged():
    text, orig, comp, tokens, pct = strip_output(["unknowncmd123"], UNKNOWN_OUTPUT)
    assert text == UNKNOWN_OUTPUT


def test_passthrough_zero_savings():
    _, orig, comp, tokens, pct = strip_output(["unknowncmd123"], UNKNOWN_OUTPUT)
    assert orig == comp
    assert tokens == 0
    assert pct == 0


# ---------------------------------------------------------------------------
# pytest rule
# ---------------------------------------------------------------------------

PYTEST_OUTPUT = """\
============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.0.0
rootdir: /home/user/project
plugins: cov-4.0.0
collecting ... collected 5 items

tests/test_foo.py::test_add PASSED
tests/test_foo.py::test_sub PASSED
tests/test_foo.py::test_mul FAILED
tests/test_foo.py::test_div FAILED
tests/test_foo.py::test_mod PASSED

=================================== FAILURES ===================================
_________________________________ test_mul _________________________________

    def test_mul():
>       assert mul(2, 3) == 7
E       AssertionError: assert 6 == 7

tests/test_foo.py:12: AssertionError
=========================== short test summary info ============================
FAILED tests/test_foo.py::test_mul - AssertionError: assert 6 == 7
FAILED tests/test_foo.py::test_div - ZeroDivisionError
========================= 3 passed, 2 failed in 0.42s ==========================
"""


def test_pytest_strips_passed_lines():
    out = compressed(["pytest"], PYTEST_OUTPUT)
    assert "PASSED" not in out


def test_pytest_strips_platform_info():
    out = compressed(["pytest"], PYTEST_OUTPUT)
    assert "platform linux" not in out
    assert "rootdir:" not in out
    assert "plugins:" not in out


def test_pytest_keeps_failed_lines():
    out = compressed(["pytest"], PYTEST_OUTPUT)
    assert "test_mul" in out
    assert "FAILED" in out


def test_pytest_keeps_error_details():
    out = compressed(["pytest"], PYTEST_OUTPUT)
    assert "AssertionError" in out


def test_pytest_keeps_summary_line():
    out = compressed(["pytest"], PYTEST_OUTPUT)
    assert "3 passed, 2 failed" in out


# ---------------------------------------------------------------------------
# git status rule + transform
# ---------------------------------------------------------------------------

GIT_STATUS_OUTPUT = """\
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
\tmodified:   src/foo.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
\tbar.py

no changes added to commit (use "git add" and/or "git commit -a")
"""


def test_git_status_reformats_branch():
    out = compressed(["git", "status"], GIT_STATUS_OUTPUT)
    assert "branch: main" in out
    assert "On branch" not in out


def test_git_status_strips_hints():
    out = compressed(["git", "status"], GIT_STATUS_OUTPUT)
    assert "Your branch is up to date" not in out
    assert "no changes added" not in out
    assert '(use "git' not in out


def test_git_status_keeps_modified_files():
    out = compressed(["git", "status"], GIT_STATUS_OUTPUT)
    assert "src/foo.py" in out


def test_git_status_strips_blank_lines():
    out = compressed(["git", "status"], GIT_STATUS_OUTPUT)
    assert "\n\n" not in out


# ---------------------------------------------------------------------------
# git log rule + transform
# ---------------------------------------------------------------------------

GIT_LOG_OUTPUT = """\
commit a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t
Author: Jane Doe <jane@example.com>
Date:   Mon May 12 10:00:00 2026 +0000

    Add feature X

commit b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u
Author: John Smith <john@example.com>
Date:   Sun May 11 09:00:00 2026 +0000

    Fix bug Y

"""


def test_git_log_strips_author():
    out = compressed(["git", "log"], GIT_LOG_OUTPUT)
    assert "Author:" not in out
    assert "jane@example.com" not in out


def test_git_log_shortens_hash():
    out = compressed(["git", "log"], GIT_LOG_OUTPUT)
    assert "a1b2c3d" in out
    assert "a1b2c3d4e5f6g7h8i9j0" not in out


def test_git_log_keeps_message():
    out = compressed(["git", "log"], GIT_LOG_OUTPUT)
    assert "Add feature X" in out
    assert "Fix bug Y" in out


def test_git_log_compact_format():
    out = compressed(["git", "log"], GIT_LOG_OUTPUT)
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 2


# ---------------------------------------------------------------------------
# ls rule + transform
# ---------------------------------------------------------------------------

LS_OUTPUT = """\
total 40
drwxr-xr-x  8 user group  256 May 12 10:00 .
drwxr-xr-x 15 user group  480 May 12 09:00 ..
-rw-r--r--  1 user group 1234 May 12 10:00 file.txt
drwxr-xr-x  2 user group   64 May 12 09:30 mydir
lrwxrwxrwx  1 user group   10 May 12 10:00 link -> target
"""


def test_ls_reformats_file():
    out = compressed(["ls"], LS_OUTPUT)
    assert "F:file.txt:1234" in out


def test_ls_reformats_directory():
    out = compressed(["ls"], LS_OUTPUT)
    assert "DIR:mydir" in out


def test_ls_strips_dot_entries():
    out = compressed(["ls"], LS_OUTPUT)
    assert "DIR:." not in out
    assert "DIR:.." not in out


def test_ls_strips_permissions():
    out = compressed(["ls"], LS_OUTPUT)
    assert "drwxr-xr-x" not in out


def test_ls_directories_before_files():
    out = compressed(["ls"], LS_OUTPUT)
    lines = [l for l in out.strip().splitlines() if l]
    dir_indices = [i for i, l in enumerate(lines) if l.startswith("DIR:")]
    file_indices = [i for i, l in enumerate(lines) if l.startswith("F:")]
    if dir_indices and file_indices:
        assert max(dir_indices) < min(file_indices)


# ---------------------------------------------------------------------------
# find rule + transform
# ---------------------------------------------------------------------------

FIND_OUTPUT = """\
.
./src
./src/main.py
./.git
./.git/config
./node_modules
./node_modules/lodash
./__pycache__
./__pycache__/main.cpython-311.pyc
./tests
./tests/test_main.py
"""


def test_find_strips_git_contents():
    out = compressed(["find"], FIND_OUTPUT)
    assert ".git/config" not in out
    assert ".git" not in out


def test_find_strips_node_modules():
    out = compressed(["find"], FIND_OUTPUT)
    assert "node_modules" not in out


def test_find_strips_pycache():
    out = compressed(["find"], FIND_OUTPUT)
    assert "__pycache__" not in out


def test_find_strips_dot_slash_prefix():
    out = compressed(["find"], FIND_OUTPUT)
    assert "./src" not in out
    assert "src" in out
    assert "tests/test_main.py" in out


# ---------------------------------------------------------------------------
# pip install rule
# ---------------------------------------------------------------------------

PIP_OUTPUT = """\
Collecting requests
  Downloading requests-2.31.0-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.6/62.6 kB 1.2 MB/s eta 0:00:00
Collecting charset-normalizer<4,>=2
  Downloading charset_normalizer-3.3.2-cp311-cp311-linux_x86_64.whl (194 kB)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/lib/python3/dist-packages
Installing collected packages: charset-normalizer, requests
Successfully installed charset-normalizer-3.3.2 requests-2.31.0
"""


def test_pip_strips_collecting_lines():
    out = compressed(["pip", "install"], PIP_OUTPUT)
    assert "Collecting requests" not in out
    assert "Downloading" not in out


def test_pip_strips_requirement_already_satisfied():
    out = compressed(["pip", "install"], PIP_OUTPUT)
    assert "Requirement already satisfied" not in out


def test_pip_strips_progress_bar():
    out = compressed(["pip", "install"], PIP_OUTPUT)
    assert "━" not in out


def test_pip_keeps_successfully_installed():
    out = compressed(["pip", "install"], PIP_OUTPUT)
    assert "Successfully installed" in out


# ---------------------------------------------------------------------------
# docker ps rule + transform
# ---------------------------------------------------------------------------

DOCKER_PS_OUTPUT = """\
CONTAINER ID   IMAGE         COMMAND                  CREATED        STATUS          PORTS                    NAMES
a1b2c3d4e5f6   nginx:latest  "/docker-entrypoint.…"   2 hours ago    Up 2 hours      0.0.0.0:80->80/tcp       webserver
b2c3d4e5f6a7   redis:7       "docker-entrypoint.s…"   1 day ago      Up 1 day        6379/tcp                 cache
"""


def test_docker_ps_strips_header():
    out = compressed(["docker", "ps"], DOCKER_PS_OUTPUT)
    assert "CONTAINER ID" not in out


def test_docker_ps_includes_name():
    out = compressed(["docker", "ps"], DOCKER_PS_OUTPUT)
    assert "webserver" in out
    assert "cache" in out


def test_docker_ps_includes_status():
    out = compressed(["docker", "ps"], DOCKER_PS_OUTPUT)
    assert "Up 2 hours" in out


# ---------------------------------------------------------------------------
# make rule
# ---------------------------------------------------------------------------

MAKE_OUTPUT = """\
make[1]: Entering directory '/home/user/project/src'
gcc -o main main.c
make[1]: Leaving directory '/home/user/project/src'
make[2]: Entering directory '/home/user/project'
gcc -o tests tests.c
make[2]: Leaving directory '/home/user/project'
"""


def test_make_strips_entering_leaving():
    out = compressed(["make"], MAKE_OUTPUT)
    assert "Entering directory" not in out
    assert "Leaving directory" not in out


def test_make_keeps_build_commands():
    out = compressed(["make"], MAKE_OUTPUT)
    assert "gcc -o main main.c" in out
    assert "gcc -o tests tests.c" in out

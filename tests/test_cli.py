import os
import pytest
from pathlib import Path

from tidyout.init_agent import run_init, TIDYOUT_BLOCK, AI_CONFIG_FILES


def _chdir(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    return orig


# ---------------------------------------------------------------------------
# All files created when none exist
# ---------------------------------------------------------------------------

def test_init_creates_all_config_files_when_none_exist(tmp_path):
    orig = _chdir(tmp_path)
    try:
        run_init()
        for rel in AI_CONFIG_FILES:
            path = tmp_path / rel
            assert path.exists(), f"{rel} was not created"
            assert "tidyout" in path.read_text()
    finally:
        os.chdir(orig)


def test_init_all_files_contain_key_commands(tmp_path):
    orig = _chdir(tmp_path)
    try:
        run_init()
        for rel in AI_CONFIG_FILES:
            content = (tmp_path / rel).read_text()
            for cmd in ["pytest", "git status", "git log", "docker logs", "npm install"]:
                assert cmd in content, f"{cmd} missing from {rel}"
    finally:
        os.chdir(orig)


# ---------------------------------------------------------------------------
# Append to existing files, create missing ones
# ---------------------------------------------------------------------------

def test_init_appends_to_existing_claude_md(tmp_path):
    orig = _chdir(tmp_path)
    try:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Existing content\n")
        run_init()
        content = claude_md.read_text()
        assert "# Existing content" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_appends_to_existing_cursorrules(tmp_path):
    orig = _chdir(tmp_path)
    try:
        cursorrules = tmp_path / ".cursorrules"
        cursorrules.write_text("# Existing cursor rules\n")
        run_init()
        content = cursorrules.read_text()
        assert "# Existing cursor rules" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_appends_to_existing_windsurfrules(tmp_path):
    orig = _chdir(tmp_path)
    try:
        windsurfrules = tmp_path / ".windsurfrules"
        windsurfrules.write_text("# Windsurf config\n")
        run_init()
        content = windsurfrules.read_text()
        assert "# Windsurf config" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_appends_to_existing_copilot_instructions(tmp_path):
    orig = _chdir(tmp_path)
    try:
        copilot = tmp_path / ".github" / "copilot-instructions.md"
        copilot.parent.mkdir()
        copilot.write_text("# Copilot instructions\n")
        run_init()
        content = copilot.read_text()
        assert "# Copilot instructions" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_creates_github_dir_for_copilot(tmp_path):
    orig = _chdir(tmp_path)
    try:
        run_init()
        copilot = tmp_path / ".github" / "copilot-instructions.md"
        assert copilot.exists()
    finally:
        os.chdir(orig)


# ---------------------------------------------------------------------------
# Mixed: some files exist, some don't
# ---------------------------------------------------------------------------

def test_init_writes_to_all_files_regardless_of_which_exist(tmp_path):
    orig = _chdir(tmp_path)
    try:
        # Pre-create only CLAUDE.md
        (tmp_path / "CLAUDE.md").write_text("# Claude\n")
        run_init()
        for rel in AI_CONFIG_FILES:
            path = tmp_path / rel
            assert path.exists(), f"{rel} should exist after init"
            assert "tidyout" in path.read_text()
    finally:
        os.chdir(orig)


# ---------------------------------------------------------------------------
# Output messages
# ---------------------------------------------------------------------------

def test_init_prints_created_for_new_files(tmp_path, capsys):
    orig = _chdir(tmp_path)
    try:
        run_init()
        out = capsys.readouterr().out
        assert "created" in out
    finally:
        os.chdir(orig)


def test_init_prints_appended_for_existing_files(tmp_path, capsys):
    orig = _chdir(tmp_path)
    try:
        (tmp_path / "CLAUDE.md").write_text("# Existing\n")
        run_init()
        out = capsys.readouterr().out
        assert "appended" in out
    finally:
        os.chdir(orig)

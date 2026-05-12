import os
import pytest
from pathlib import Path

from tidyout.init_agent import run_init, TIDYOUT_BLOCK


def test_init_creates_claude_md_when_neither_exists(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        run_init()
        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text()
        assert "tidyout" in content
        assert "tidy" in content
    finally:
        os.chdir(orig)


def test_init_appends_to_existing_claude_md(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Existing content\n")
        run_init()
        content = claude_md.read_text()
        assert "# Existing content" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_does_not_create_new_claude_md_when_cursorrules_exists(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        cursorrules = tmp_path / ".cursorrules"
        cursorrules.write_text("# Cursor rules\n")
        run_init()
        assert not (tmp_path / "CLAUDE.md").exists()
        assert "tidyout" in cursorrules.read_text()
    finally:
        os.chdir(orig)


def test_init_appends_to_cursorrules(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        cursorrules = tmp_path / ".cursorrules"
        cursorrules.write_text("# Cursor rules\n")
        run_init()
        content = cursorrules.read_text()
        assert "# Cursor rules" in content
        assert "tidyout" in content
    finally:
        os.chdir(orig)


def test_init_prefers_claude_md_over_cursorrules(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        claude_md = tmp_path / "CLAUDE.md"
        cursorrules = tmp_path / ".cursorrules"
        claude_md.write_text("# Claude\n")
        cursorrules.write_text("# Cursor\n")
        run_init()
        assert "tidyout" in claude_md.read_text()
        assert "tidyout" not in cursorrules.read_text()
    finally:
        os.chdir(orig)


def test_init_block_contains_key_commands(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        run_init()
        content = (tmp_path / "CLAUDE.md").read_text()
        for cmd in ["pytest", "git status", "git log", "docker logs", "npm install"]:
            assert cmd in content
    finally:
        os.chdir(orig)


def test_init_prints_action(tmp_path, capsys):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        run_init()
        out = capsys.readouterr().out
        assert "CLAUDE.md" in out
    finally:
        os.chdir(orig)

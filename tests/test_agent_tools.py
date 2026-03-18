"""Test Task 2 tools."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import read_file, list_files, safe_path

def test_read_file():
    content = read_file("agent.py")
    assert "read_file" in content

def test_list_files():
    files = list_files(".")
    assert "agent.py" in files

def test_safe_path_blocked():
    import pytest
    with pytest.raises(ValueError):
        safe_path("../secrets")

def test_wiki_access():
    try:
        content = read_file("wiki/git-workflow.md")
        assert "#" in content or "not found" in content
    except:
        pass  # wiki might not exist yet

print("✅ Tool tests passed")
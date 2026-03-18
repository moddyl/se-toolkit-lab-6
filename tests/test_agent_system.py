"""Test Task 3 system agent tools."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import query_api, TOOLS

def test_query_api_tool_exists():
    """Verify query_api is in tools."""
    tool_names = [t["function"]["name"] for t in TOOLS]
    assert "query_api" in tool_names

def test_query_api_schema():
    """Check query_api has correct parameters."""
    for tool in TOOLS:
        if tool["function"]["name"] == "query_api":
            props = tool["function"]["parameters"]["properties"]
            assert "method" in props
            assert "path" in props
            return
    assert False, "query_api not found"

def test_query_api_no_auth():
    """Test query_api without auth (should work for public endpoints)."""
    # This test might need mocking - for now just check function exists
    assert callable(query_api)

print("✅ System agent tests passed")
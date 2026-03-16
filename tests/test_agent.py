import subprocess
import json
import sys

def test_agent_returns_valid_json():
    result = subprocess.run(
        ["python", "agent.py", "What does REST stand for?"],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "answer" in output
    assert "tool_calls" in output

def test_agent_tool_calls_is_list():
    result = subprocess.run(
        ["python", "agent.py", "What does REST stand for?"],
        capture_output=True, text=True, timeout=60
    )
    output = json.loads(result.stdout)
    assert isinstance(output["tool_calls"], list)

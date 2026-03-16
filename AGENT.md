cat > AGENT.md << 'EOF'
# Agent Documentation

## Overview
CLI agent that answers questions using an LLM via OpenAI-compatible API.

## Usage
uv run agent.py "Your question here"

## Output
{"answer": "...", "tool_calls": []}

## LLM Provider
Qwen Code API (qwen3-coder-plus). Configured via environment variables.

## Environment Variables
- LLM_API_KEY — LLM provider API key
- LLM_API_BASE — LLM API endpoint URL
- LLM_MODEL — model name
- LMS_API_KEY — backend API key for query_api tool
- AGENT_API_BASE_URL — backend base URL (default: http://localhost:42002)

## Tools
- read_file — reads project files (wiki, source code, configs)
- list_files — lists files in a directory
- query_api — calls the live backend API with LMS_API_KEY auth

## Agentic Loop
1. Send question + tool definitions to LLM
2. If LLM returns tool_calls — execute tools, feed results back
3. Repeat up to 10 iterations
4. When LLM returns text with no tool calls — output final JSON
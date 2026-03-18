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
- AGENT_API_BASE_URL — backend base URL (default: <http://localhost:42002>)

## Tools

- read_file — reads project files (wiki, source code, configs)
- list_files — lists files in a directory
- query_api — calls the live backend API with LMS_API_KEY auth

## Agentic Loop

1. Send question + tool definitions to LLM
2. If LLM returns tool_calls — execute tools, feed results back
3. Repeat up to 10 iterations
4. When LLM returns text with no tool calls — output final JSON

## System Prompt Strategy

The agent uses a detailed system prompt that guides the LLM to:

- Use `list_files` first to discover available wiki files
- Use `read_file` to examine relevant files (wiki docs, source code, configs)
- Use `query_api` to get live data from the backend
- Chain tools when needed (e.g., API error → read source code to find bug)
- Include source references in format: `wiki/file.md#section`
- For `query_api`, test with `auth=false` to check unauthenticated responses

## Tool Details

### read_file

- **Purpose**: Read any file within project root
- **Parameters**: `path` (string) — relative path from project root
- **Security**: Validates path to prevent directory traversal (`safe_path()`)
- **Returns**: File contents or error message

### list_files

- **Purpose**: Discover files in a directory
- **Parameters**: `path` (string) — relative directory path
- **Security**: Only lists directories within project root
- **Returns**: Newline-separated list of entries

### query_api

- **Purpose**: Interact with the live backend API
- **Parameters**:
  - `method` (string) — HTTP method (GET, POST, etc.)
  - `path` (string) — API endpoint (e.g., `/items/`)
  - `body` (optional) — JSON request body
  - `auth` (boolean) — whether to include LMS_API_KEY (default: true)
- **Returns**: JSON with `status_code` and `body`

## Security Measures

- All file paths are resolved against `PROJECT_ROOT` and checked for traversal attacks
- Paths containing `..` or absolute paths outside project are rejected
- API requests include authentication only when `auth=true`

## Example Workflows

### Wiki Question

```bash
uv run agent.py "How do you resolve a merge conflict?"

### Data Question
```bash
uv run agent.py "How many items are in the database?"

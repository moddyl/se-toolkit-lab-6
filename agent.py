import sys
import json
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env.agent.secret")
load_dotenv(".env.docker.secret")

AGENT_API_BASE_URL = os.environ.get("AGENT_API_BASE_URL", "http://localhost:42002")
LMS_API_KEY = os.environ.get("LMS_API_KEY", "")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a local file. Use this to read wiki documentation "
                "(in the wiki/ directory), backend source code (e.g. main.py, routers/, models.py), "
                "docker-compose.yml, Dockerfile, or any other project file. "
                "Use this for questions about how the project works, what framework it uses, "
                "ETL pipeline logic, request lifecycle, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file, e.g. 'wiki/git-workflow.md' or 'backend/main.py'",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files in a directory. Use this to discover what files exist before reading them. "
                "Useful for finding all router modules, wiki pages, or source files in a directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the directory, e.g. 'backend/routers' or 'wiki'",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": (
                "Send an HTTP request to the deployed backend API. Use this for questions that require "
                "live data from the running system: item counts, scores, completion rates, HTTP status codes "
                "returned by specific endpoints, or any question about the current state of the database. "
                "Always use this (not read_file) when the question asks to 'query the API', 'query the running API', "
                "or asks about current data. Authenticate automatically with LMS_API_KEY."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method: GET, POST, PUT, DELETE, etc.",
                    },
                    "path": {
                        "type": "string",
                        "description": "API path, e.g. '/items/' or '/analytics/completion-rate?lab=lab-99'",
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON body for POST/PUT requests.",
                    },
                },
                "required": ["method", "path"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a helpful assistant for a software engineering project.
You have access to three tools:

1. read_file — read local project files (wiki docs, source code, config files).
   Use for: wiki questions, framework/library questions, code logic, ETL pipeline, Dockerfile, docker-compose.yml.

2. list_files — list files in a directory.
   Use for: discovering what router modules exist, what wiki pages are available.

3. query_api — send HTTP requests to the running backend API.
   Use for: current data (item counts, scores), HTTP status codes returned by endpoints,
   endpoint behavior, live error responses.

Decision rules:
- Question about documentation or wiki → read_file on the wiki/ directory.
- Question about source code or architecture → read_file on backend/ files.
- Question about what the API returns, how many items exist, live data → query_api.
- Question about what files/modules exist → list_files.
- When diagnosing a bug: first query_api to see the error, then read_file to find the buggy line.

Always use the appropriate tool — do not answer from memory alone when a tool can give the real answer.
When counting items from an API response that returns a list, count the actual items in the list.
"""


def run_read_file(path: str) -> str:
    try:
        content = Path(path).read_text(encoding="utf-8")
        # Limit to avoid context overflow
        if len(content) > 12000:
            content = content[:12000] + "\n... [truncated]"
        return content
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def run_list_files(path: str) -> str:
    try:
        entries = sorted(Path(path).iterdir())
        lines = [str(e) for e in entries]
        return "\n".join(lines) if lines else "(empty directory)"
    except FileNotFoundError:
        return f"Error: directory not found: {path}"
    except Exception as e:
        return f"Error listing directory: {e}"


def run_query_api(method: str, path: str, body: str = None) -> str:
    url = AGENT_API_BASE_URL.rstrip("/") + path
    headers = {"X-API-Key": LMS_API_KEY, "Content-Type": "application/json"}
    try:
        resp = httpx.request(
            method=method.upper(),
            url=url,
            headers=headers,
            content=body.encode() if body else None,
            timeout=15,
        )
        return json.dumps({"status_code": resp.status_code, "body": resp.text})
    except Exception as e:
        return json.dumps({"status_code": 0, "body": f"Request error: {e}"})


def dispatch_tool(name: str, args: dict) -> str:
    if name == "read_file":
        return run_read_file(args["path"])
    elif name == "list_files":
        return run_list_files(args["path"])
    elif name == "query_api":
        return run_query_api(args["method"], args["path"], args.get("body"))
    else:
        return f"Unknown tool: {name}"


def main():
    if len(sys.argv) < 2:
        print("Usage: agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    client = OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_API_BASE"],
    )
    model = os.environ["LLM_MODEL"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_calls_log = []
    max_iterations = 10

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            timeout=60,
        )

        msg = response.choices[0].message

        # If no tool calls, we have the final answer
        if not msg.tool_calls:
            answer = (msg.content or "").strip()
            result = {"answer": answer, "tool_calls": tool_calls_log}
            print(json.dumps(result))
            return

        # Add assistant message to history
        messages.append(msg.model_dump(exclude_unset=False))

        # Process each tool call
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            print(f"[tool] {name}({args})", file=sys.stderr)
            tool_result = dispatch_tool(name, args)

            tool_calls_log.append({
                "tool": name,
                "args": args,
                "result": tool_result[:500],  # truncate for log
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result,
            })

    # Fallback if max iterations reached
    result = {"answer": "Max iterations reached without a final answer.", "tool_calls": tool_calls_log}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
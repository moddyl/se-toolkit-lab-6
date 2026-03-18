# Task 3: System Agent Plan

## query_api Tool Schema

- **Name**: query_api
- **Description**: Call the deployed backend API with authentication
- **Parameters**:
  - `method` (string): GET, POST, etc.
  - `path` (string): API endpoint (e.g., "/items/")
  - `body` (optional string): JSON request body
  - `auth` (boolean): Whether to include LMS_API_KEY (default: true)
- **Returns**: JSON with `status_code` and `body`

## Authentication

- Uses `LMS_API_KEY` from environment (`.env.docker.secret`)
- Base URL from `AGENT_API_BASE_URL` (default: <http://localhost:42002>)

## System Prompt Updates

Add decision rules for when to use:

- `read_file` → for source code, configs, wiki
- `list_files` → to discover files
- `query_api` → for live data, status codes, error diagnosis

## Benchmark Strategy

1. Run `uv run run_eval.py` to get initial score
2. Fix failures one by one:
   - Wrong tool → improve tool descriptions
   - Wrong answer → adjust system prompt
   - API errors → fix query_api implementation
3. Aim for 10/10 on local eval

## Initial Score: 0/10 (to be updated)

## Iterations: TBD

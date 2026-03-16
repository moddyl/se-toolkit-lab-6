# Task 1 Plan: Call an LLM from Code

## LLM Provider
Qwen Code API via OpenAI-compatible endpoint.

## Model
qwen3-coder-plus

## Structure
- agent.py reads question from sys.argv[1]
- Loads LLM_API_KEY, LLM_API_BASE, LLM_MODEL from environment variables
- Calls OpenAI-compatible chat completions API
- Prints JSON with answer and tool_calls to stdout
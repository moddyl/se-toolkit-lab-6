# Task 2: Documentation Agent Plan

## Tool Schemas Implemented

- `read_file`: Reads files safely with path traversal protection
- `list_files`: Lists directory contents within project root

## Agentic Loop

1. Send question + tool definitions to LLM
2. If tool_calls → execute tools, append results, repeat
3. If text response → extract SOURCE: tag for source field
4. Max 10 iterations

## Security

- `safe_path()` validates all paths against PROJECT_ROOT
- Blocks any path containing ".." or absolute paths outside project

## System Prompt Strategy

Instructs LLM to:

- Use list_files first to discover wiki files
- Then read_file to find answers
- Include SOURCE: wiki/file.md#section in response

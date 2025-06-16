# mcp-talk
Code and material for the talk "MCP: Principles and Practice"

## Getting Started
Ensure you have `uv` installed. You can install it by following the instructions at [installing uv](https://docs.astral.sh/uv/getting-started/installation/.

Then, run:
```bash
uv sync
```

This will install all the dependencies required for the project.

## Running the MCP Server
To run the MCP server, use the following command:
```bash
mcp install src/mcp_server.py
mcp dev src/mcp_server.py
```

"""MCP server for Agent Context Pruner and Token Budget Compressor."""
import sys
import json
from client import ContextPruner


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "truncate_tool_output",
                    "description": "Collapses long terminal or tool outputs into compact head/tail summaries to conserve context",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "output_text": {"type": "string", "description": "Raw verbose tool output text"},
                            "max_lines": {"type": "integer", "default": 40},
                            "max_chars": {"type": "integer", "default": 4000},
                        },
                        "required": ["output_text"],
                    },
                },
                {
                    "name": "prune_trajectory",
                    "description": "Prunes historical conversation messages to fit within an explicit token budget while preserving system prompts",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "messages": {"type": "array", "description": "Array of message objects (role, content)"},
                            "token_budget": {"type": "integer", "default": 4000},
                        },
                        "required": ["messages"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "truncate_tool_output":
            res = ContextPruner.truncate_tool_output(
                args.get("output_text", ""),
                max_lines=args.get("max_lines", 40),
                max_chars=args.get("max_chars", 4000),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "prune_trajectory":
            res = ContextPruner.prune_trajectory(
                args.get("messages", []),
                token_budget=args.get("token_budget", 4000),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()

# genpark-agent-context-pruner-and-token-budget-compressor-skill

Prunes historical agent context, truncates verbose tool outputs, and compresses conversational trajectories within strict token budget limits.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities
- **Intelligent Tool Output Truncation**: Collapses thousand-line command outputs and file dumps into structured head-and-tail summaries with truncation notices.
- **Priority-Preserving Trajectory Pruning**: Pins essential system prompts and current user instructions while sliding-window pruning intermediate turns.
- **Token Budget Compliance**: Calculates heuristic token counts (~4 characters per token) to prevent context overflow exceptions across autonomous loops.
- **Zero Dependencies**: Pure standard library execution with zero latency overhead.

## Architecture

```
[Voluminous Trajectory & Tool Dumps]
                  │
                  ▼
┌──────────────────────────────────────────────┐
│  ContextPruner                               │
│  ├─ Head/Tail Window Truncator               │
│  ├─ Pin Manager (System & Current User)      │
│  └─ Token Budget Constraint Solver           │
└──────────────────────────────────────────────┘
                  │
                  ▼
[Clean Budget-Compliant Context for Next Step]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `truncate_tool_output`: Truncates large tool results into clean head/tail summaries.
- `prune_trajectory`: Prunes an array of messages to fit within an explicit token budget while preserving pinned instructions.

## Quickstart

```python
from client import ContextPruner

# 1. Truncate long log
raw_log = "\n".join([f"Line {i}" for i in range(200)])
res = ContextPruner.truncate_tool_output(raw_log, max_lines=20)
print(res["text"])

# 2. Prune message trajectory
messages = [
    {"role": "system", "content": "System prompt."},
    {"role": "user", "content": "Old request."},
    {"role": "assistant", "content": "Intermediate output " * 100},
    {"role": "user", "content": "Latest task."},
]
pruned = ContextPruner.prune_trajectory(messages, token_budget=50)
print("Remaining messages:", len(pruned["messages"]))
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)

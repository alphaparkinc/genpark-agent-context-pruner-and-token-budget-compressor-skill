"""Example usage for Agent Context Pruner & Token Budget Compressor."""
from client import ContextPruner

if __name__ == "__main__":
    # 1. Truncate long tool output
    long_log = "\n".join([f"Processing batch #{i}..." for i in range(100)])
    trunc_res = ContextPruner.truncate_tool_output(long_log, max_lines=20)
    print("Truncated:", trunc_res["truncated"])
    print("Pruned Lines:", trunc_res["pruned_lines"])
    print("Output Snippet:\n", trunc_res["text"])

    # 2. Prune conversation trajectory
    chat_history = [
        {"role": "system", "content": "You are a helpful GenPark autonomous coding agent."},
        {"role": "user", "content": "Initial request to build feature X."},
        {"role": "assistant", "content": "Step 1 details " * 200},
        {"role": "user", "content": "Intermediate feedback " * 200},
        {"role": "assistant", "content": "Step 2 details " * 200},
        {"role": "user", "content": "Final latest instruction: please verify the build."},
    ]

    pruned = ContextPruner.prune_trajectory(chat_history, token_budget=300)
    print("\nOriginal Messages:", len(chat_history))
    print("Retained Messages:", len(pruned["messages"]))
    print("Pruned Count:", pruned["pruned_count"])

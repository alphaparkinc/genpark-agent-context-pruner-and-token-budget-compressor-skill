"""Agent Context Pruner and Token Budget Compressor.
100% Python Standard Library.
"""

from typing import List, Dict, Any, Tuple, Optional


class ContextPruner:
    """Manages LLM conversational trajectories to ensure strict adherence to token budgets,
    truncates verbose tool outputs, and preserves high-priority instructions."""

    CHARS_PER_TOKEN = 4

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Estimates token count using character heuristic (~4 chars/token)."""
        return max(1, len(text) // cls.CHARS_PER_TOKEN)

    @classmethod
    def truncate_tool_output(
        cls,
        output_text: str,
        max_lines: int = 40,
        max_chars: int = 4000,
        head_lines: int = 15,
        tail_lines: int = 15,
    ) -> Dict[str, Any]:
        """Collapses voluminous output into a compact head-and-tail summary."""
        lines = output_text.splitlines()
        original_line_count = len(lines)
        original_char_count = len(output_text)

        if original_line_count <= max_lines and original_char_count <= max_chars:
            return {
                "truncated": False,
                "text": output_text,
                "original_lines": original_line_count,
                "pruned_lines": 0,
            }

        head = lines[:head_lines]
        tail = lines[-tail_lines:] if tail_lines > 0 else []
        pruned_count = original_line_count - (len(head) + len(tail))

        summary_marker = f"\n... [Truncated {pruned_count} lines of verbose output by ContextPruner] ...\n"
        truncated_body = "\n".join(head) + summary_marker + "\n".join(tail)

        # Double check character cap
        if len(truncated_body) > max_chars:
            truncated_body = truncated_body[:max_chars] + "\n... [Character budget reached] ..."

        return {
            "truncated": True,
            "text": truncated_body,
            "original_lines": original_line_count,
            "pruned_lines": pruned_count,
        }

    @classmethod
    def prune_trajectory(
        cls,
        messages: List[Dict[str, Any]],
        token_budget: int = 4000,
        preserve_system: bool = True,
        preserve_last_user: bool = True,
    ) -> Dict[str, Any]:
        """Prunes historical conversational messages from the middle while
        preserving initial system prompts and the latest user request."""
        if not messages:
            return {"messages": [], "estimated_tokens": 0, "pruned_count": 0}

        # Calculate initial token usage
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        est_tokens = total_chars // cls.CHARS_PER_TOKEN

        if est_tokens <= token_budget:
            return {
                "messages": messages,
                "estimated_tokens": est_tokens,
                "pruned_count": 0,
                "budget_exceeded": False,
            }

        pinned_indices = set()
        if preserve_system and messages and messages[0].get("role") == "system":
            pinned_indices.add(0)

        if preserve_last_user:
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    pinned_indices.add(i)
                    break

        # Always keep the most recent message
        pinned_indices.add(len(messages) - 1)

        # Build prioritized list starting from recent messages backwards
        retained = []
        current_tokens = 0

        # First add pinned messages
        for idx in sorted(pinned_indices):
            msg = messages[idx]
            tok = cls.estimate_tokens(str(msg.get("content", "")))
            retained.append((idx, msg, tok))
            current_tokens += tok

        # Fill remaining budget from newest to oldest
        for idx in range(len(messages) - 1, -1, -1):
            if idx in pinned_indices:
                continue
            msg = messages[idx]
            tok = cls.estimate_tokens(str(msg.get("content", "")))
            if current_tokens + tok <= token_budget:
                retained.append((idx, msg, tok))
                current_tokens += tok

        retained.sort(key=lambda x: x[0])
        final_messages = [x[1] for x in retained]
        pruned_count = len(messages) - len(final_messages)

        return {
            "messages": final_messages,
            "estimated_tokens": current_tokens,
            "pruned_count": pruned_count,
            "budget_exceeded": False,
        }

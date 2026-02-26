from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PromptContext:
    tokens_used: int
    safety_anchors: List[str]
    working_memory: str

class ContextGovernor:
    """
    Executes Context Governor rules:
    - Enforces token budgets
    - Preserves prioritized safety constraints
    - Prevents context saturation and manipulation
    """
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self._global_anchors = [
            "CRITICAL: Do not alter configuration files.",
            "CRITICAL: Only read from the designated sandboxed directory."
        ]

    def _estimate_tokens(self, text: str) -> int:
        """Mock token estimation for MVP."""
        return len(text.split())

    def validate_budget(self, proposed_context_len: int) -> bool:
        """Check if context exceeds limits."""
        return proposed_context_len <= self.max_tokens

    def prepare_context(self, dynamic_query: str, system_prompt: str) -> Optional[PromptContext]:
        """
        Assembles a context block while strictly preserving safety guidelines 
        and enforcing budget limits.
        """
        # Ensure safety anchors are never pruned
        anchors_block = "\n".join(self._global_anchors)
        
        # Assemble string to estimate
        full_string = f"{anchors_block}\n\n{system_prompt}\n\n{dynamic_query}"
        estimated_tokens = self._estimate_tokens(full_string)
        
        if not self.validate_budget(estimated_tokens):
            print(f"CONTEXT GOVERNOR Block: Context saturation. Used {estimated_tokens}/{self.max_tokens} tokens.")
            # A real implementation would invoke priority-weighted pruning here.
            # We mock a hard block for safety.
            return None
            
        print(f"CONTEXT GOVERNOR Pass: Context budget OK ({estimated_tokens}/{self.max_tokens}). Constraints re-anchored.")
        
        return PromptContext(
            tokens_used=estimated_tokens,
            safety_anchors=self._global_anchors,
            working_memory=dynamic_query
        )

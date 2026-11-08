from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.observability.tracer import ExecutionTrace

class AgentStep(BaseModel):
    step_number: int
    thought: str
    action_type: str  # "CALL_TOOL", "SELF_CORRECT", "FINISH"
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    reflection: Optional[str] = None

class AgentState(BaseModel):
    query: str
    steps: List[AgentStep] = Field(default_factory=list)
    current_step_index: int = 0
    max_steps: int = 6
    retries_left: int = 2
    is_complete: bool = False
    final_answer: Optional[str] = None
    trace: ExecutionTrace

    class Config:
        arbitrary_types_allowed = True

    def has_failures(self) -> bool:
        """Checks if any recorded step encountered a failure or triggered reflection."""
        return any(s.action_type == "SELF_CORRECT" or (s.tool_output and not s.tool_output.get("success", True)) for s in self.steps)

    def get_tool_names(self) -> List[str]:
        """Returns distinct tool names executed across all steps."""
        return [s.tool_name for s in self.steps if s.tool_name is not None]

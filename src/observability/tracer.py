import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SpanRecord(BaseModel):
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None
    name: str
    span_type: str  # "AGENT_STEP", "LLM_CALL", "TOOL_CALL", "SELF_CORRECTION", "SYNTHESIS"
    start_time: float
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    status: str = "RUNNING"  # "RUNNING", "SUCCESS", "ERROR"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def finish(self, status: str = "SUCCESS", output: Any = None, error: Optional[str] = None):
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        self.output_data = output
        self.error_message = error

        # Pricing estimation (Standard Gemini/GPT-4o mini tier: $0.15/1M input, $0.60/1M output)
        input_cost = (self.prompt_tokens / 1_000_000) * 0.15
        output_cost = (self.completion_tokens / 1_000_000) * 0.60
        self.estimated_cost_usd = round(input_cost + output_cost, 6)

class ExecutionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration_ms: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    spans: List[SpanRecord] = Field(default_factory=list)

    def start_span(
        self,
        name: str,
        span_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> SpanRecord:
        span = SpanRecord(
            name=name,
            span_type=span_type,
            start_time=time.time(),
            input_data=input_data or {},
            parent_id=parent_id,
        )
        self.spans.append(span)
        return span

    def close(self):
        self.end_time = time.time()
        self.total_duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.total_prompt_tokens = sum(s.prompt_tokens for s in self.spans)
        self.total_completion_tokens = sum(s.completion_tokens for s in self.spans)
        self.total_tokens = sum(s.total_tokens for s in self.spans)
        self.total_cost_usd = round(sum(s.estimated_cost_usd for s in self.spans), 6)

    def summary(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "duration_ms": self.total_duration_ms,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "span_count": len(self.spans),
            "tool_calls": len([s for s in self.spans if s.span_type == "TOOL_CALL"]),
            "retries": len([s for s in self.spans if s.span_type == "SELF_CORRECTION"]),
        }

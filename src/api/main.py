from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent.graph import AgentGraph
from src.agent.tools.registry import default_registry
from src.agent.tools.sql_analytics import analytics_engine

app = FastAPI(
    title="Agent-Trace-Ops API",
    description="Autonomous Agentic Workflow Engine with OpenTelemetry Spans & DuckDB Analytics",
    version="0.1.0",
)

# CORS middleware for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., example="What are the top 3 AI funding rounds in the database and calculate their average?")

class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

@app.get("/health")
def health_check():
    """Health check endpoint displaying system readiness and tool count."""
    return {
        "status": "healthy",
        "system": "agent-trace-ops",
        "registered_tools": list(default_registry.tools.keys()),
        "in_memory_db": "DuckDB active",
    }

@app.get("/tools")
def list_tools():
    """Returns available tools and their JSON parameter schemas."""
    return {"tools": default_registry.definitions}

@app.post("/agent/run")
def run_agent(request: QueryRequest):
    """Executes the autonomous agent graph and returns findings + trace telemetry."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    graph = AgentGraph(registry=default_registry)
    state = graph.run(request.query)

    return {
        "query": state.query,
        "is_complete": state.is_complete,
        "steps_count": len(state.steps),
        "steps": [s.model_dump() for s in state.steps],
        "final_answer": state.final_answer,
        "trace": {
            "trace_id": state.trace.trace_id,
            "duration_ms": state.trace.total_duration_ms,
            "total_tokens": state.trace.total_tokens,
            "total_cost_usd": state.trace.total_cost_usd,
            "spans": [span.model_dump() for span in state.trace.spans],
        },
    }

@app.post("/tools/execute")
def execute_tool_directly(req: ToolExecutionRequest):
    """Directly invokes a single tool for testing or isolated execution."""
    result = default_registry.execute(req.tool_name, req.arguments)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

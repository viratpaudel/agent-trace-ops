import pytest
from src.agent.graph import AgentGraph
from src.agent.tools.registry import default_registry

def test_agent_graph_executes_query():
    graph = AgentGraph(registry=default_registry)
    state = graph.run("What are the top AI funding rounds?")

    assert state.is_complete is True
    assert len(state.steps) >= 1
    assert state.final_answer is not None
    assert len(state.trace.spans) > 0
    assert state.trace.total_duration_ms > 0

def test_agent_graph_schema_inspection():
    graph = AgentGraph(registry=default_registry)
    state = graph.run("Show me the database schema and table details")

    assert state.is_complete is True
    assert any(s.tool_name == "get_database_schema" for s in state.steps)

def test_agent_self_correction_trigger():
    # Test self-correction logic directly
    graph = AgentGraph(registry=default_registry)
    correction = graph._self_correct("query_duckdb", {"sql_query": "SELECT fake_column FROM missing_table"}, "Table not found")
    assert correction["retry"] is True
    assert "tech_investments" in correction["retry_input"]["sql_query"]

import pytest
from src.agent.tools.calculator import safe_calculate
from src.agent.tools.sql_analytics import analytics_engine
from src.agent.tools.registry import default_registry

def test_safe_calculator_basic_arithmetic():
    res = safe_calculate("100 + 50 * 2")
    assert res["success"] is True
    assert res["result"] == 200

def test_safe_calculator_division_by_zero():
    res = safe_calculate("100 / 0")
    assert res["success"] is False
    assert "Division by zero" in res["error"]

def test_safe_calculator_blocks_arbitrary_code_injection():
    # Attempt Python code execution injection
    res = safe_calculate("__import__('os').system('ls')")
    assert res["success"] is False
    assert "Invalid expression" in res["error"] or "syntax" in res["error"].lower()

def test_duckdb_analytics_select_query():
    res = analytics_engine.execute_query("SELECT company, funding_usd_millions FROM tech_investments LIMIT 3")
    assert res["success"] is True
    assert len(res["data"]) == 3
    assert "company" in res["columns"]

def test_duckdb_analytics_blocks_mutations():
    res = analytics_engine.execute_query("DROP TABLE tech_investments")
    assert res["success"] is False
    assert "Security violation" in res["error"]

def test_tool_registry_execution():
    res = default_registry.execute("safe_calculate", {"expression": "25 * 4"})
    assert res["success"] is True
    assert res["result"] == 100

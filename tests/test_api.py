import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "safe_calculate" in data["registered_tools"]

def test_api_tools_list():
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert len(tools) >= 3

def test_api_agent_run():
    response = client.post("/agent/run", json={"query": "Find the highest funded tech companies"})
    assert response.status_code == 200
    res = response.json()
    assert res["is_complete"] is True
    assert "trace" in res
    assert len(res["trace"]["spans"]) >= 1

def test_api_direct_tool_execution():
    response = client.post("/tools/execute", json={
        "tool_name": "safe_calculate",
        "arguments": {"expression": "500 / 2"}
    })
    assert response.status_code == 200
    assert response.json()["result"] == 250

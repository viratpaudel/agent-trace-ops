from typing import Any, Callable, Dict, List
from .calculator import safe_calculate
from .sql_analytics import analytics_engine
from .web_search import search_web

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.definitions: List[Dict[str, Any]] = []
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self.tools[name] = func
        self.definitions.append({
            "name": name,
            "description": description,
            "parameters": parameters,
        })

    def _register_default_tools(self):
        # 1. Calculator
        self.register(
            name="safe_calculate",
            description="Safely executes arithmetic calculations (e.g. '120 * 1.15', 'round(4000 / 18000, 4)').",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression string to evaluate without arbitrary code execution."
                    }
                },
                "required": ["expression"]
            },
            func=lambda expression: safe_calculate(expression)
        )

        # 2. DuckDB SQL Analytics
        self.register(
            name="query_duckdb",
            description="Runs SQL SELECT analytical queries on the in-memory database table 'tech_investments' (columns: company, sector, funding_usd_millions, valuation_usd_millions, year, stage, lead_investor, country).",
            parameters={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL SELECT query string to execute against 'tech_investments'."
                    }
                },
                "required": ["sql_query"]
            },
            func=lambda sql_query: analytics_engine.execute_query(sql_query)
        )

        # 3. DuckDB Schema Inspector
        self.register(
            name="get_database_schema",
            description="Retrieves the exact schema, table names, and column types for analytical queries.",
            parameters={"type": "object", "properties": {}},
            func=lambda: analytics_engine.get_table_schema()
        )

        # 4. Web Search
        self.register(
            name="search_web",
            description="Searches technical documentation, articles, and industry insights.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Target search query string."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to retrieve (default 3)."
                    }
                },
                "required": ["query"]
            },
            func=lambda query, max_results=3: search_web(query, max_results)
        )

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered tool defensively with structured error encapsulation."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}",
            }
        try:
            return self.tools[tool_name](**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error in tool '{tool_name}': {str(e)}",
            }

default_registry = ToolRegistry()

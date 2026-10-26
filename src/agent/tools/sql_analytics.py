import os
from pathlib import Path
from typing import Any, Dict
import duckdb

DATA_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sample_tech_investments.csv"

class DuckDBAnalytics:
    def __init__(self, data_file: Path = DATA_PATH):
        self.conn = duckdb.connect(database=":memory:")
        self.data_file = data_file
        self._init_tables()

    def _init_tables(self):
        if self.data_file.exists():
            # Load CSV into in-memory table
            self.conn.execute(f"""
                CREATE TABLE tech_investments AS 
                SELECT * FROM read_csv_auto('{self.data_file.as_posix()}', header=True)
            """)
        else:
            # Fallback mock schema if file is missing
            self.conn.execute("""
                CREATE TABLE tech_investments (
                    company VARCHAR,
                    sector VARCHAR,
                    funding_usd_millions DOUBLE,
                    valuation_usd_millions DOUBLE,
                    year INTEGER,
                    stage VARCHAR,
                    lead_investor VARCHAR,
                    country VARCHAR
                );
                INSERT INTO tech_investments VALUES 
                ('Anthropic', 'GenAI', 4000, 18000, 2023, 'Series C', 'Amazon', 'USA'),
                ('Mistral AI', 'GenAI', 640, 6000, 2024, 'Series B', 'General Catalyst', 'France');
            """)

    def get_table_schema(self) -> Dict[str, Any]:
        """Returns the schema and column info for available tables."""
        columns_info = self.conn.execute("DESCRIBE tech_investments").fetchall()
        schema_summary = [f"{col[0]} ({col[1]})" for col in columns_info]
        return {
            "table_name": "tech_investments",
            "columns": schema_summary,
            "description": "Tech and AI funding rounds with company, sector, funding_usd_millions, valuation_usd_millions, year, stage, lead_investor, country",
        }

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Executes a read-only analytical SQL query on DuckDB."""
        cleaned_query = sql_query.strip().rstrip(";")

        # Security check: Read-only guardrail
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "ATTACH", "COPY", "CALL"]
        upper_tokens = cleaned_query.upper().split()
        for f in forbidden:
            if f in upper_tokens:
                return {
                    "success": False,
                    "error": f"Security violation: Query contains disallowed mutation keyword '{f}'. Only SELECT/WITH analytical queries are permitted.",
                }

        try:
            rel = self.conn.execute(cleaned_query)
            df = rel.df()
            rows_count = len(df)
            # Limit returned rows to top 50 to avoid prompt context explosion
            if rows_count > 50:
                df = df.head(50)
            return {
                "success": True,
                "rows_returned": rows_count,
                "columns": list(df.columns),
                "data": df.to_dict(orient="records"),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"DuckDB SQL Execution Error: {str(e)}",
                "attempted_query": cleaned_query,
            }

analytics_engine = DuckDBAnalytics()

import json
import httpx
from typing import List, Optional, Dict, Any
from app.domain.interfaces import ILLMService
from app.domain.models import SQLGeneration, SchemaInfo

class OpenAICompatibleService(ILLMService):
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def _chat_completion(self, messages: List[dict], response_json: bool = True) -> Optional[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model_name,
            "messages": messages
        }
        if response_json:
            body["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=body
            )
            if resp.status_code != 200:
                raise Exception(f"API error {resp.status_code}: {resp.text}")
            return resp.json()

    def generate_sql(self, query: str, context: List[SchemaInfo]) -> SQLGeneration:
        schema_text = ""
        for info in context:
            table_info = (
                f"\nTable: {info.table_name}\n"
                f"Columns: {', '.join(info.columns)}\n"
                f"Sample Rows: {info.sample_rows}\n"
            )
            schema_text += table_info

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert SQL Generator. Convert the user's natural language query "
                    "into a valid SQL query for SQLite.\n"
                    "Rules:\n"
                    "1. is_safe must be false if the query modifies data (INSERT/UPDATE/DELETE/DROP).\n"
                    "2. Use the provided schema names exactly.\n"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{schema_text}\n\nUser Query: \"{query}\""
            }
        ]

        try:
            data = self._chat_completion(messages)
            choice = data["choices"][0]["message"]["content"]
            parsed = json.loads(choice)
            return SQLGeneration(
                sql=parsed.get("sql", ""),
                explanation=parsed.get("explanation", ""),
                is_safe=parsed.get("is_safe", True)
            )
        except Exception as e:
            return SQLGeneration(sql="", error_message=str(e), is_safe=False)

    def guess_intent(self, query: str, available_tables: List[str]) -> List[str]:
        messages = [
            {
                "role": "system",
                "content": "Identify the top 3-5 most relevant tables needed to answer the query. Return JSON array of table names."
            },
            {
                "role": "user",
                "content": f'Query: "{query}"\nAvailable tables: {", ".join(available_tables)}'
            }
        ]
        try:
            data = self._chat_completion(messages)
            choice = data["choices"][0]["message"]["content"]
            return json.loads(choice)
        except:
            return []

    def suggest_chart(self, query: str, columns: List[str]) -> Optional[Dict[str, Any]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "Analyze the user query and the returned data columns to suggest the best visualization chart type.\n"
                    "Return JSON with:\n"
                    '- "chart_type": one of ["bar", "line", "pie", "doughnut", "scatter", "none"]\n'
                    '- "title": concise title\n'
                    '- "x_column": column for X-axis\n'
                    '- "y_columns": list of column names for Y-axis\n'
                    '- "labels": list of dataset labels\n'
                    'If chart_type is "none", other fields can be null.'
                )
            },
            {
                "role": "user",
                "content": f'User Query: "{query}"\nColumns: {columns}'
            }
        ]
        try:
            data = self._chat_completion(messages)
            choice = data["choices"][0]["message"]["content"]
            result = json.loads(choice)
            if result.get("chart_type") == "none":
                return None
            return result
        except:
            return None

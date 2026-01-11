from google import genai
from google.genai import types
import json
import os
from typing import List, Optional, Dict, Any
from app.domain.interfaces import ILLMService
from app.domain.models import SQLGeneration, SchemaInfo

class GeminiService(ILLMService):
    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _sanitize_text(self, text: str) -> str:
        """
        Removes surrogate characters that are not allowed in UTF-8 encoding.
        This prevents UnicodeEncodeError when sending data to Gemini.
        """
        if not isinstance(text, str):
            return str(text)
        return text.encode('utf-8', 'ignore').decode('utf-8')

    def generate_sql(self, query: str, context: List[SchemaInfo]) -> SQLGeneration:
        # Construct Context String
        schema_text = ""
        for info in context:
            # Sanitize potentially dirty data from database (sample_rows)
            table_info = f"\nTable: {info.table_name}\nColumns: {', '.join(info.columns)}\nMsg: Sample Rows: {info.sample_rows}\n"
            schema_text += self._sanitize_text(table_info)

        # Sanitize query just in case
        query = self._sanitize_text(query)

        prompt = f"""
        You are an expert SQL Generator. Convert the user's natural language query into a valid SQL query for SQLite.
        
        Context:
        {schema_text}
        
        User Query: "{query}"
        
        Rules:
        1. "is_safe" should be false if the query modifies data (INSERT/UPDATE/DELETE/DROP).
        2. Use the provided schema names exactly.
        """
        
        prompt = self._sanitize_text(prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string"},
                            "explanation": {"type": "string"},
                            "is_safe": {"type": "boolean"}
                        },
                        "required": ["sql", "explanation", "is_safe"]
                    }
                )
            )
            data = json.loads(response.text)
            return SQLGeneration(
                sql=data.get("sql", ""),
                explanation=data.get("explanation", ""),
                is_safe=data.get("is_safe", True)
            )
        except Exception as e:
            return SQLGeneration(sql="", error_message=str(e), is_safe=False)

    def guess_intent(self, query: str, available_tables: List[str]) -> List[str]:
        prompt = f"""
        Given the user query: "{query}"
        And the list of available tables: {', '.join(available_tables)}
        
        Identify the top 3-5 most relevant tables needed to answer this query.
        """
        
        prompt = self._sanitize_text(prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "array",
                        "items": {"type": "string"}
                    }
                )
            )
            return json.loads(response.text)
        except:
            return []

    def suggest_chart(self, query: str, columns: List[str]) -> Optional[Dict[str, Any]]:
        prompt = f"""
        Analyze the user query and the returned data columns to suggest the best visualization chart type.
        
        User Query: "{query}"
        Columns: {columns}
        
        Return a configuration JSON.
        - "chart_type": One of ["bar", "line", "pie", "doughnut", "scatter", "none"]. Use "none" if a table is better.
        - "title": A concise title for the chart.
        - "x_column": The column name to use for the X-axis (labels).
        - "y_columns": A LIST of column names to use for the Y-axis (values). E.g. ["sales", "profit"].
        - "labels": A LIST of labels for each dataset (e.g., ["Total Revenue", "Net Profit"]).
        
        If "chart_type" is "none", other fields can be null.
        """
        
        prompt = self._sanitize_text(prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "chart_type": {"type": "string"},
                            "title": {"type": "string"},
                            "x_column": {"type": "string"},
                            "y_columns": {"type": "array", "items": {"type": "string"}},
                            "labels": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["chart_type", "title", "x_column", "y_columns", "labels"]
                    }
                )
            )
            
            data = json.loads(response.text)
            if data.get("chart_type") == "none":
                return None
            return data
        except:
            return None

import google.generativeai as genai
import json
import os
from typing import List
from app.domain.interfaces import ILLMService
from app.domain.models import SQLGeneration, SchemaInfo

class GeminiService(ILLMService):
    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

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
        
        # Define Schema for Structure Output
        generation_config = genai.GenerationConfig(
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

        prompt = self._sanitize_text(prompt)

        try:
            response = self.model.generate_content(prompt, generation_config=generation_config)
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
        
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "array",
                "items": {"type": "string"}
            }
        )

        prompt = self._sanitize_text(prompt)

        try:
            response = self.model.generate_content(prompt, generation_config=generation_config)
            return json.loads(response.text)
        except:
            return []

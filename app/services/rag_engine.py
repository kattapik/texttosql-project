from typing import List
from app.domain.interfaces import IRagEngine, IDatabase, ILLMService
from app.domain.models import SchemaInfo

class RagEngine(IRagEngine):
    def __init__(self, db: IDatabase, llm: ILLMService):
        self.db = db
        self.llm = llm

    def get_context(self, query: str) -> List[SchemaInfo]:
        """
        Retrieves context using a tiered approach:
        1. Short List (Keyword Match)
        2. LLM Guess (Fallback)
        """
        all_tables = self.db.get_all_table_names()
        
        # 1. Short List Strategy (Naive keyword matching)
        # Check if table names appear directly in the query
        short_list = [table for table in all_tables if table.lower() in query.lower()]
        
        # If we found robust matches (e.g. > 1 table or specific ones), we might verify them.
        # But for MVP, if short_list is empty, we fall back.
        
        if not short_list:
             # 2. LLM Guess Strategy (Fallback)
             print(f"DEBUG: Short list empty for '{query}'. Using LLM Guess.")
             guessed_tables = self.llm.guess_intent(query, all_tables)
             
             # Filter valid tables only
             short_list = [t for t in guessed_tables if t in all_tables]

        # Get Schema Info for selected tables
        if short_list:
            return self.db.get_schema_info(short_list)
        
        # If logic fails completely, return all (risky for large DBs, safe for MVP)
        print("DEBUG: Fallback to ALL tables.")
        return self.db.get_schema_info(all_tables[:5]) # Limit to 5 strictly for MVP safety

from typing import List
from app.domain.interfaces import IRagEngine, IDatabase, IVectorStore
from app.domain.models import SchemaInfo

class RagEngine(IRagEngine):
    def __init__(self, db: IDatabase, vector_store: IVectorStore):
        self.db = db
        self.vector_store = vector_store

    def get_context(self, query: str) -> List[SchemaInfo]:
        """
        Retrieves context using embedding-based semantic search.
        Falls back to first 3 tables if vector store is empty or no match found.
        """
        chunks = self.vector_store.search(query, k=5)

        if not chunks:
            print(f"DEBUG: No vector matches for '{query}'. Falling back to first 3 tables.")
            all_tables = self.db.get_all_table_names()
            return self.db.get_schema_info(all_tables[:3])

        table_names = [c.table_name for c in chunks if c.table_name]
        if table_names:
            return self.db.get_schema_info(table_names)

        all_tables = self.db.get_all_table_names()
        return self.db.get_schema_info(all_tables[:3])

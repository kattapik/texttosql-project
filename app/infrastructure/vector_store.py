from typing import List
import chromadb
from app.domain.interfaces import IVectorStore, IEmbeddingService
from app.domain.models import SchemaInfo, SchemaChunk

COLLECTION_NAME = "schema_chunks"

class SchemaVectorStore(IVectorStore):
    def __init__(self, embedding_service: IEmbeddingService, persist_dir: str = None):
        self._embedding_service = embedding_service
        if persist_dir:
            self._client = chromadb.PersistentClient(path=persist_dir)
        else:
            self._client = chromadb.EphemeralClient()
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def _chunk_schema(self, schema: SchemaInfo) -> SchemaChunk:
        cols_str = ", ".join(schema.columns)
        rows_str = str(schema.sample_rows[:3]) if schema.sample_rows else ""
        content = (
            f"Table: {schema.table_name}\n"
            f"Columns: {cols_str}\n"
            f"Sample Rows: {rows_str}"
        )
        return SchemaChunk(
            content=content,
            table_name=schema.table_name,
            columns=schema.columns
        )

    def index_schema(self, schema_list: List[SchemaInfo]) -> None:
        chunks = [self._chunk_schema(s) for s in schema_list]
        ids = [f"{c.table_name}" for c in chunks]
        contents = [c.content for c in chunks]

        count = self._collection.count()
        if count > 0:
            existing = self._collection.get(ids=ids)
            if existing and existing.get("ids"):
                self._collection.delete(ids=existing["ids"])

        embeddings = [self._embedding_service.embed(c) for c in contents]
        metadatas = [{"table_name": c.table_name} for c in chunks]

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

    def search(self, query: str, k: int = 5) -> List[SchemaChunk]:
        query_embedding = self._embedding_service.embed(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        chunks = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                chunks.append(SchemaChunk(
                    content=doc,
                    table_name=meta.get("table_name", "unknown"),
                    columns=[]
                ))
        return chunks

    def clear(self) -> None:
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

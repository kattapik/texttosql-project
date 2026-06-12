import os
import sys
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Any

# Ensure 'app' module is found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.sqlite_db import SqliteRepository
from app.infrastructure.gemini_llm import GeminiService
from app.infrastructure.embeddings import EmbeddingService
from app.infrastructure.vector_store import SchemaVectorStore
from app.infrastructure.provider_factory import LLMFactory, PROVIDER_PRESETS
from app.services.rag_engine import RagEngine
from app.services.validator import SqlValidator
from app.domain.interfaces import ILLMService

load_dotenv()

# --- Config & Dependencies ---
DB_PATH = os.getenv("DB_PATH", "data/sqlite.db")

server = FastAPI(title="Text-to-SQL API")

# Mount Static Files
server.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Services
db_repo = SqliteRepository(DB_PATH)
embedding_service = EmbeddingService()
vector_store = SchemaVectorStore(embedding_service)

# Index schema into vector store on startup
all_tables = db_repo.get_all_table_names()
if all_tables:
    schema_list = db_repo.get_schema_info(all_tables)
    vector_store.index_schema(schema_list)
    print(f"[*] Indexed {len(schema_list)} tables into vector store.")
else:
    print("[*] No tables found in database. Run init_db.py first.")

rag_engine = RagEngine(db=db_repo, vector_store=vector_store)
validator = SqlValidator()

def create_llm_from_request(req: "QueryRequest") -> ILLMService:
    api_key = req.api_key or os.getenv(f"{req.provider.upper()}_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail=f"API key required for provider '{req.provider}'")
    return LLMFactory.create(
        provider=req.provider,
        api_key=api_key,
        model_name=req.model_name,
        base_url=req.base_url
    )

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = "gemini"
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    base_url: Optional[str] = None

class QueryResponse(BaseModel):
    context: List[dict]
    sql: Optional[str] = None
    explanation: Optional[str] = None
    results: Optional[dict] = None
    chart_config: Optional[dict] = None
    error: Optional[str] = None

# --- Routes ---

@server.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@server.get("/favicon.ico")
async def favicon():
    from fastapi import Response
    return Response(status_code=204)

@server.get("/api/settings")
async def get_settings():
    return {
        "presets": {
            key: {
                "label": val["label"],
                "default_model": val["default_model"],
                "base_url": val["base_url"]
            }
            for key, val in PROVIDER_PRESETS.items()
        }
    }

@server.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    user_query = request.query

    if not user_query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        start_time = time.time()

        # A. RAG - Get Context
        t0 = time.time()
        context_infos = rag_engine.get_context(user_query)
        print(f"[Log] RAG Context: {time.time() - t0:.2f}s")

        context_data = [
            {"table": info.table_name, "columns": info.columns}
            for info in context_infos
        ]

        # B. LLM - Generate SQL (from selected provider)
        t1 = time.time()
        llm_service = create_llm_from_request(request)
        sql_result = llm_service.generate_sql(user_query, context_infos)
        print(f"[Log] SQL Gen ({request.provider}): {time.time() - t1:.2f}s")

        if not sql_result.sql:
            return QueryResponse(
                context=context_data,
                sql=None,
                error=f"Failed to generate SQL: {sql_result.error_message}"
            )

        # C. Validation
        validation = validator.validate(sql_result.sql)
        if not validation.is_valid:
             return QueryResponse(
                context=context_data,
                sql=sql_result.sql,
                error=f"Validation Failed: {validation.error}"
            )

        if not sql_result.is_safe:
             return QueryResponse(
                context=context_data,
                sql=sql_result.sql,
                error="Query identified as unsafe (Modification detected)."
            )

        # D. Execution
        t2 = time.time()
        exec_result = db_repo.execute_query(sql_result.sql)
        print(f"[Log] DB Exec: {time.time() - t2:.2f}s")

        if not exec_result.success:
            return QueryResponse(
                context=context_data,
                sql=sql_result.sql,
                explanation=sql_result.explanation,
                error=exec_result.error
            )

        # E. Chart Suggestion
        chart_config = None
        if exec_result.success and exec_result.columns and exec_result.rows:
            t3 = time.time()
            chart_config = llm_service.suggest_chart(user_query, exec_result.columns)
            print(f"[Log] Chart Gen: {time.time() - t3:.2f}s")

        total_time = time.time() - start_time
        print(f"[Log] Total Process: {total_time:.2f}s")

        return QueryResponse(
            context=context_data,
            sql=sql_result.sql,
            explanation=sql_result.explanation,
            results={
                "columns": exec_result.columns,
                "rows": exec_result.rows
            },
            chart_config=chart_config
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=8000)

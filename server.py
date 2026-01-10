import os
import sys
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
from app.services.rag_engine import RagEngine
from app.services.validator import SqlValidator

load_dotenv()

# --- Config & Dependencies ---
API_KEY = os.getenv("GOOGLE_API_KEY")
DB_PATH = os.getenv("DB_PATH", "data/sqlite.db")

if not API_KEY:
    print("ERROR: GOOGLE_API_KEY not set.")
    sys.exit(1)

server = FastAPI(title="Text-to-SQL API")

# Mount Static Files
server.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Services
db_repo = SqliteRepository(DB_PATH)
llm_service = GeminiService(api_key=API_KEY)
rag_engine = RagEngine(db=db_repo, llm=llm_service)
validator = SqlValidator()

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    context: List[dict]
    sql: Optional[str] = None
    explanation: Optional[str] = None
    results: Optional[dict] = None
    error: Optional[str] = None

# --- Routes ---

@server.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@server.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    user_query = request.query
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        # A. RAG - Get Context
        context_infos = rag_engine.get_context(user_query)
        context_data = [
            {"table": info.table_name, "columns": info.columns} 
            for info in context_infos
        ]

        # B. LLM - Generate SQL
        sql_result = llm_service.generate_sql(user_query, context_infos)
        
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
        exec_result = db_repo.execute_query(sql_result.sql)
        
        if not exec_result.success:
            return QueryResponse(
                context=context_data,
                sql=sql_result.sql,
                explanation=sql_result.explanation,
                error=exec_result.error
            )

        return QueryResponse(
            context=context_data,
            sql=sql_result.sql,
            explanation=sql_result.explanation,
            results={
                "columns": exec_result.columns,
                "rows": exec_result.rows
            }
        )

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="127.0.0.1", port=8000)

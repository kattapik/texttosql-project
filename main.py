import os
import sys
from dotenv import load_dotenv
from typing import List
from tabulate import tabulate

# Add current dir to path to find 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.sqlite_db import SqliteRepository
from app.infrastructure.gemini_llm import GeminiService
from app.services.rag_engine import RagEngine
from app.services.validator import SqlValidator
from app.domain.models import ExecutionResult

# Load environment variables
load_dotenv()

def main():
    print("==========================================")
    print("       Text-to-SQL MVP (Gemini)           ")
    print("==========================================")
    
    # 1. Configuration & Setup
    api_key = os.getenv("GOOGLE_API_KEY")
    db_path = os.getenv("DB_PATH", "sqlite.db")
    
    if not api_key or "your_gemini_api_key_here" in api_key:
        print("ERROR: GOOGLE_API_KEY not found or invalid in .env")
        print("Please set your API key in the .env file.")
        return

    if not os.path.exists(db_path):
        print(f"ERROR: Database '{db_path}' not found. Run init_db.py first.")
        return

    # 2. Dependency Injection
    print(f"[*] Connecting to database: {db_path}...")
    db_repo = SqliteRepository(db_path)
    
    print("[*] Initializing Gemini Service...")
    llm_service = GeminiService(api_key=api_key)
    
    print("[*] Initializing Services...")
    rag_engine = RagEngine(db=db_repo, llm=llm_service)
    validator = SqlValidator()
    
    print("\nSystem Ready. Type 'exit' to quit.\n")

    # 3. Main Loop
    while True:
        try:
            user_input = input("\nUser > ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # A. RAG / Context Retrieval
            print("  -> Retrieving Context...")
            context = rag_engine.get_context(user_input)
            print(f"     [Context] Found {len(context)} tables: {[t.table_name for t in context]}")

            # B. LLM Generation
            print("  -> Generative SQL...")
            sql_result = llm_service.generate_sql(user_input, context)
            
            if not sql_result.sql:
                print(f"  [!] Failed to generate SQL: {sql_result.error_message}")
                continue

            print(f"     [Generated] {sql_result.sql}")
            print(f"     [Reasoning] {sql_result.explanation}")

            # C. Validation
            print("  -> Validating...")
            validation = validator.validate(sql_result.sql)
            if not validation.is_valid:
                print(f"  [!] Validation Failed: {validation.error}")
                if not sql_result.is_safe:
                    print("      (Query identified as unsafe)")
                continue

            # D. Execution
            print("  -> Executing...")
            exec_result = db_repo.execute_query(sql_result.sql)
            
            if exec_result.success:
                print("\nResults:")
                if exec_result.rows:
                    print(tabulate(exec_result.rows, headers=exec_result.columns, tablefmt="grid"))
                else:
                    print("  (No rows returned)")
            else:
                print(f"  [!] Execution Error: {exec_result.error}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[!] Unexpected Error: {e}")

if __name__ == "__main__":
    main()

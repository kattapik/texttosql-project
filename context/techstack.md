# Technology Stack & Context

## Core Technologies
- **Language**: Python 3.10+
- **Database**: SQLite (Native `sqlite3` lib)
- **AI/LLM**: Google Gemini (via `google-generativeai`)
- **Environment Management**: `python-dotenv` for secrets

## Architecture Patterns
- **Clean Architecture / Layered Architecture**:
    - **Domain Layer**: Core logic and Interfaces (Ports).
    - **Infrastructure Layer**: Implementation of External services (Gemini, SQLite).
    - **Service/Application Layer**: Orchestration logic (RAG flow, Validator).
    - **Interface Layer**: Console UI (`main.py`).

## Key Libraries
- `google-generativeai`: For interacting with Gemini API.
- `python-dotenv`: Loading API keys from `.env`.
- `sqlparse` (Optional): For basic SQL validation/formatting if needed.

## Design Decisions
- **Dependency Injection**: Services will be injected into the main orchestrator to allow easy swapping of implementations (e.g., swapping RAG logic or LLM provider).
- **MVP Focus**: While "Clean", we will avoid over-engineering. Folders will be logical but not excessively nested.

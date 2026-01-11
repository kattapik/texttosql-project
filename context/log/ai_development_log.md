# AI Driven Development Log

This document tracks the development decision flow, AI reasoning, and major implementation steps.

## Phase 1: Inception & Setup
- **Objective**: Create a Text-to-SQL MVP with Google Gemini and SQLite.
- **Architecture**: Clean Architecture (Domain, Infrastructure, Services).
- **Schema**: Complex E-commerce schema (~19 tables) to test RAG capabilities.

### Decisions
1.  **Framework**: Pure Python + SQLite to keep dependencies minimal yet functional.
2.  **RAG Strategy**:
    - **Short List**: Quick check for keywords.
    - **Fallback**: LLM "Guess" -> RAG if Short List fails. This optimizes token usage and accuracy.
3.  **Safety**: Read-only enforcement via Validator service.

## Progress Log
- [x] Context & Plan created.
- [x] Context & Plan created.
- [x] Environment files (`requirements.txt`, `.env.example`) created.
- [x] Schema generation (19 tables).
- [x] Core Implementation (Domain, Infra, Services, Main) completed.

## Phase 1.5: AI Workflow Integration
- [x] Created `.agent/workflows/ai-driven-dev.md` to standardize context loading and logging.
- [x] Established rule to update this log after every development cycle.

## Phase 2: Implementation - Seeding
- [x] Integrated `Faker` for realistic data generation.
- [x] Created `DataSeeder` service in `app/infrastructure/seeder.py`.
- [x] Modified `init_db.py` to automatically seed data (Users, Products, Orders, Reviews) upon initialization.
- [x] Verified database population (size ~136KB).

## Phase 3: RAG Strategy Discussion
- [x] Discussed Vector DB vs. LLM.
- [x] Decision: Keep current "Simple RAG" (Keyword + LLM Guess) for MVP.

## Phase 4: Web Interface
- [x] Replaced Console UI with Flask Web App (`app.py`).
- [x] Implemented Modern Dark Mode UI with Glassmorphism.
- [x] Visualized RAG process (Context -> SQL -> Result).

## Phase 5: Refactoring & Polish
- [x] Migrated Backend from Flask to **FastAPI** (Async, Pydantic, Auto-docs).
- [x] Redesigned Frontend to "Clean SaaS" Aesthetic:
  - Removed "Gamer/Neon" style.
  - Implemented Professional Light Mode (Inter font, minimalist layout).
  - Improved Mobile Responsiveness.

## Phase 6: Data Visualization
- [x] Backend: Implemented `GeminiService.suggest_chart` using AI to determine chart type.
- [x] Frontend: Integrated `Chart.js` for dynamic chart rendering.
- [x] Strategy: Used "Column Mapping" (mapping SQL columns to X/Y axes) instead of regenerating data.

## Phase 7: SDK Migration
- [x] Migrated from deprecated `google.generativeai` to `google-genai` (v1.0+ Client).
- [x] Updated `requirements.txt`.
- [x] Refactored `GeminiService` to use `genai.Client` and `types`.

## Phase 8: Chart Enhancements (Multi-Column)
- [x] Backend: Updated `suggest_chart` to support returning multiple Y-columns (`y_columns` list) and `labels`.
- [x] Frontend: Updated `script.js` to dynamically generate multiple datasets with rotating colors.
- [x] Result: Visualization now supports complex comparisons (e.g., Sales vs Profit).

## Phase 9: Verifying
- Testing Chart Interactions.

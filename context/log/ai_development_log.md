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

## Phase 2: Verifying
- Testing with user queries.

# Text-to-SQL Flow Architecture

This document describes the flow for the Text-to-SQL MVP using Python, SQLite, and Google Gemini.

## Core Flow Architecture

The system follows a tiered approach to ensure accuracy and fallback mechanisms.

```mermaid
graph TD
    A[User Input] --> B{Short List Check}
    B -- Found --> C[RAG / Context Retrieval]
    B -- Not Found (Fail) --> D[Fallback: LLM Guess]
    D --> C
    C --> E[LLM Structure Output]
    E --> F{SQL Parse/Validate}
    F -- Valid --> G[Execute Query (SQLite)]
    F -- Invalid --> H[Error/Retry]
    G --> I[Return Result to User]
```

## Detailed Steps

1.  **User Input**: Console-based input from the user (natural language).
2.  **Short List**: A pre-defined list or lightweight check (e.g., keyword mappings or distinct column values) to quickly identify intent or filter relevant tables/columns.
3.  **Fallback (LLM Guess)**: If the Short List fails to find a direct match or context, use the LLM to "guess" the intent or relevant schema parts to narrow down the RAG scope.
4.  **RAG (Retrieval-Augmented Generation)**: Retrieve the specific table schemas, constraints, and relevant sample data based on the identified scope.
5.  **LLM (Structure Output)**: Send the gathered context + user query to Google Gemini. Request a structured response (e.g., JSON containing the SQL query and reasoning).
6.  **SQL Parse/Validate**:
    *   Syntactic check (using query validation tools).
    *   Safety check (ensure it is a READ operation, no DROP/DELETE).
7.  **Query**: Execute the validated SQL against the local SQLite database.

## Technology Stack

*   **Language**: Python
*   **Database**: SQLite
*   **AI Model**: Google Gemini (Standard API)
*   **Interface**: Console (CLI)

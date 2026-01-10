# Important Context & Constraints

## Project Goals
- **MVP Text-to-SQL**: A working console application that converts natural language to SQL.
- **Flow Reliability**: Must strictly follow: `User Input -> Short List -> RAG -> LLM -> Validator -> Query`.
- **Safety**:
    - **Read-Only**: The system should only execute `SELECT` queries.
    - **Validation**: SQL must be parsed and vetted before execution.

## Critical Constraints
- **Console Output**: Keep it clean. Show the generated SQL before executing for transparency.
- **LLM Guest Fallback**: If the "Short List" (exact match/lookup) fails, use the LLM to guess the context before hitting RAG again. This prevents blindly retrieving all schemas.

## User Preferences
- **Architecture**: Modular and Clean.
- **Structure**: Clear separation of concerns.
- **Language**: Python.

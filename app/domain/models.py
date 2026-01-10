from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class SchemaInfo:
    """Represents the schema information for RAG context."""
    table_name: str
    columns: List[str]
    sample_rows: List[Dict[str, Any]]

@dataclass
class UserQuery:
    """Represents the user's natural language query."""
    text: str
    context_history: Optional[List[str]] = None

@dataclass
class SQLGeneration:
    """Represents the output from the LLM."""
    sql: str
    explanation: Optional[str] = None
    is_safe: bool = False
    error_message: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of SQL validation."""
    is_valid: bool
    sql: Optional[str] = None
    error: Optional[str] = None

@dataclass
class ExecutionResult:
    """Result of SQL execution."""
    columns: List[str]
    rows: List[Any]
    success: bool
    error: Optional[str] = None

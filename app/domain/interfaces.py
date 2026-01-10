from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.domain.models import SchemaInfo, SQLGeneration, ExecutionResult, ValidationResult

class IDatabase(ABC):
    """Interface for Database Operations."""
    
    @abstractmethod
    def execute_query(self, sql: str) -> ExecutionResult:
        """Executes a SQL query and returns the results."""
        pass

    @abstractmethod
    def get_schema_info(self, table_names: List[str]) -> List[SchemaInfo]:
        """Retrieves schema information for specific tables."""
        pass

    @abstractmethod
    def get_all_table_names(self) -> List[str]:
        """Retrieves all table names in the database."""
        pass

class ILLMService(ABC):
    """Interface for LLM Operations."""

    @abstractmethod
    def generate_sql(self, query: str, context: List[SchemaInfo]) -> SQLGeneration:
        """Generates SQL based on the query and schema context."""
        pass

    @abstractmethod
    def guess_intent(self, query: str, available_tables: List[str]) -> List[str]:
        """Guesses relevant tables based on the query."""
        pass

class IRagEngine(ABC):
    """Interface for RAG Operations."""

    @abstractmethod
    def get_context(self, query: str) -> List[SchemaInfo]:
        """Retrieves the relevant schema context for a query."""
        pass

class IValidator(ABC):
    """Interface for SQL Validation."""
    
    @abstractmethod
    def validate(self, sql: str) -> ValidationResult:
        """Validates the SQL query for safety and syntax."""
        pass

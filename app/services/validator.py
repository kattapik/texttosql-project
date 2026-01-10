import sqlparse
from sqlparse import tokens as T
from app.domain.interfaces import IValidator
from app.domain.models import ValidationResult

class SqlValidator(IValidator):
    def validate(self, sql: str) -> ValidationResult:
        if not sql:
            return ValidationResult(is_valid=False, error="Empty SQL query")

        # Parsing
        parsed = sqlparse.parse(sql)
        if not parsed:
            return ValidationResult(is_valid=False, error="Could not parse SQL")
        
        stmt = parsed[0]
        
        # 1. Primary Check: Statement Type
        if stmt.get_type() != 'SELECT':
             return ValidationResult(is_valid=False, error="Safety Error: Query must be a SELECT statement")

        # 2. Token-based Check
        # Iterate through every token to ensure no hidden DDL/DML exists
        for token in stmt.flatten():
            if token.ttype is T.Keyword.DDL:
                return ValidationResult(is_valid=False, error=f"Safety Error: Forbidden DDL command found '{token.value}'")
            if token.ttype is T.Keyword.DML and token.value.upper() != 'SELECT':
                return ValidationResult(is_valid=False, error=f"Safety Error: Forbidden DML command found '{token.value}'")

        return ValidationResult(is_valid=True, sql=sql)

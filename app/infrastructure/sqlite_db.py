import sqlite3
from typing import List, Any
from app.domain.interfaces import IDatabase
from app.domain.models import ExecutionResult, SchemaInfo

class SqliteRepository(IDatabase):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, sql: str) -> ExecutionResult:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                
                # Fetch headers if available
                columns = []
                if cursor.description:
                    columns = [description[0] for description in cursor.description]
                
                rows = cursor.fetchall()
                return ExecutionResult(columns=columns, rows=rows, success=True)
        except Exception as e:
            return ExecutionResult(columns=[], rows=[], success=False, error=str(e))

    def get_all_table_names(self) -> List[str]:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        result = self.execute_query(query)
        if result.success:
            return [row[0] for row in result.rows if row[0] != "sqlite_sequence"]
        return []

    def get_schema_info(self, table_names: List[str]) -> List[SchemaInfo]:
        schema_infos = []
        for table in table_names:
            # Get Columns
            pragma_query = f"PRAGMA table_info({table});"
            result = self.execute_query(pragma_query)
            if not result.success:
                continue
            
            # row format: (cid, name, type, notnull, dflt_value, pk)
            columns = [f"{row[1]} ({row[2]})" for row in result.rows]

            # Get Sample Rows (Limit 3)
            sample_query = f"SELECT * FROM {table} LIMIT 3;"
            sample_result = self.execute_query(sample_query)
            sample_rows = []
            if sample_result.success:
                headers = sample_result.columns
                for row in sample_result.rows:
                    sample_rows.append(dict(zip(headers, row)))

            schema_infos.append(SchemaInfo(
                table_name=table,
                columns=columns,
                sample_rows=sample_rows
            ))
        return schema_infos

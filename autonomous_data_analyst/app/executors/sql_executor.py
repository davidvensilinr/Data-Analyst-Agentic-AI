import pandas as pd
import sqlite3
from typing import Dict, Any, List
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset
from config.settings import settings


class SQLExecutor(BaseExecutor):
    """Executor for SQL-based analysis steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SQL queries."""
        
        query_type = spec.get("query_type", "custom")
        
        if query_type == "custom":
            return await self._execute_custom_query(dataset, spec)
        elif query_type == "descriptive":
            return await self._execute_descriptive_query(dataset, spec)
        elif query_type == "aggregation":
            return await self._execute_aggregation_query(dataset, spec)
        elif query_type == "correlation":
            return await self._execute_correlation_query(dataset, spec)
        elif query_type == "time_series":
            return await self._execute_time_series_query(dataset, spec)
        else:
            raise ValueError(f"Unknown query type: {query_type}")
    
    async def _execute_custom_query(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom SQL query."""
        query = spec.get("query", "")
        
        if not query:
            raise ValueError("No SQL query provided")
        
        # Load dataset and create temporary SQLite database
        df = self._get_dataset_dataframe(dataset)
        df = self._sanitize_column_names(df)
        
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        try:
            # Validate query for safety
            if not self._is_safe_query(query):
                raise ValueError("Query contains potentially unsafe operations")
            
            # Execute query with row limit
            limited_query = f"SELECT * FROM ({query}) LIMIT {settings.MAX_QUERY_ROWS}"
            result_df = pd.read_sql_query(limited_query, conn)
            
            # Get query execution info
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM ({query})")
            total_rows = cursor.fetchone()[0]
            
            result = {
                "query": query,
                "data": result_df.fillna("").to_dict('records'),
                "columns": result_df.columns.tolist(),
                "row_count": len(result_df),
                "total_rows": total_rows,
                "truncated": total_rows > settings.MAX_QUERY_ROWS
            }
            
            return {
                "result": result,
                "rationale": f"Executed SQL query returning {len(result_df)} rows{' (truncated)' if result['truncated'] else ''}",
                "confidence": 0.9
            }
            
        finally:
            conn.close()
    
    async def _execute_descriptive_query(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute descriptive statistics queries."""
        df = self._get_dataset_dataframe(dataset)
        df = self._sanitize_column_names(df)
        
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        try:
            numeric_columns = self._get_numeric_columns(df)
            results = {}
            
            # Basic descriptive statistics for numeric columns
            for col in numeric_columns:
                query = f"""
                SELECT 
                    COUNT(*) as count,
                    AVG({col}) as mean,
                    MIN({col}) as min,
                    MAX({col}) as max,
                    ROUND(AVG({col}), 2) as mean_rounded
                FROM data
                WHERE {col} IS NOT NULL
                """
                
                result_df = pd.read_sql_query(query, conn)
                results[col] = result_df.to_dict('records')[0]
            
            # Row count
            count_query = "SELECT COUNT(*) as total_rows FROM data"
            total_rows = pd.read_sql_query(count_query, conn).iloc[0]['total_rows']
            
            result = {
                "total_rows": total_rows,
                "numeric_statistics": results,
                "column_count": len(df.columns),
                "numeric_columns": numeric_columns
            }
            
            return {
                "result": result,
                "rationale": f"Generated descriptive statistics for {len(numeric_columns)} numeric columns",
                "confidence": 0.95
            }
            
        finally:
            conn.close()
    
    async def _execute_aggregation_query(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute aggregation queries."""
        group_by = spec.get("group_by", [])
        aggregations = spec.get("aggregations", {})
        
        if not group_by and not aggregations:
            raise ValueError("Either group_by or aggregations must be specified")
        
        df = self._get_dataset_dataframe(dataset)
        df = self._sanitize_column_names(df)
        
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        try:
            # Build aggregation query
            select_clauses = []
            
            if group_by:
                select_clauses.extend(group_by)
            
            for col, agg_funcs in aggregations.items():
                for func in agg_funcs:
                    if func.upper() in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']:
                        select_clauses.append(f"{func.upper()}({col}) as {col}_{func}")
            
            query = f"SELECT {', '.join(select_clauses)} FROM data"
            
            if group_by:
                query += f" GROUP BY {', '.join(group_by)}"
            
            # Add limit
            query += f" LIMIT {settings.MAX_QUERY_ROWS}"
            
            result_df = pd.read_sql_query(query, conn)
            
            result = {
                "query": query,
                "data": result_df.fillna("").to_dict('records'),
                "columns": result_df.columns.tolist(),
                "row_count": len(result_df),
                "group_by": group_by,
                "aggregations": aggregations
            }
            
            return {
                "result": result,
                "rationale": f"Executed aggregation query grouped by {group_by} with {len(aggregations)} aggregations",
                "confidence": 0.9
            }
            
        finally:
            conn.close()
    
    async def _execute_correlation_query(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute correlation analysis."""
        columns = spec.get("columns", [])
        
        df = self._get_dataset_dataframe(dataset)
        df = self._sanitize_column_names(df)
        
        # Filter to numeric columns
        if columns:
            numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        else:
            numeric_cols = self._get_numeric_columns(df)
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation analysis")
        
        # Calculate correlation matrix
        correlation_matrix = df[numeric_cols].corr()
        
        # Convert to list format for JSON serialization
        correlation_data = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i <= j:  # Only include upper triangle to avoid duplicates
                    correlation_data.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": float(correlation_matrix.iloc[i, j]) if not pd.isna(correlation_matrix.iloc[i, j]) else None
                    })
        
        # Find strong correlations
        strong_correlations = [
            item for item in correlation_data
            if item["correlation"] is not None and abs(item["correlation"]) > 0.7 and item["column1"] != item["column2"]
        ]
        
        result = {
            "correlation_matrix": correlation_matrix.fillna("").to_dict(),
            "correlation_data": correlation_data,
            "strong_correlations": strong_correlations,
            "columns_analyzed": numeric_cols
        }
        
        return {
            "result": result,
            "rationale": f"Calculated correlations for {len(numeric_cols)} numeric columns. Found {len(strong_correlations)} strong correlations.",
            "confidence": 0.9
        }
    
    async def _execute_time_series_query(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute time series analysis queries."""
        date_column = spec.get("date_column")
        value_column = spec.get("value_column")
        aggregation = spec.get("aggregation", "SUM")
        frequency = spec.get("frequency", "daily")
        
        if not date_column or not value_column:
            raise ValueError("Both date_column and value_column must be specified")
        
        df = self._get_dataset_dataframe(dataset)
        df = self._sanitize_column_names(df)
        
        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        try:
            # Build time series query based on frequency
            if frequency == "daily":
                date_format = "%Y-%m-%d"
                group_clause = f"DATE({date_column})"
            elif frequency == "weekly":
                date_format = "%Y-%W"
                group_clause = f"strftime('%Y-%W', {date_column})"
            elif frequency == "monthly":
                date_format = "%Y-%m"
                group_clause = f"strftime('%Y-%m', {date_column})"
            elif frequency == "yearly":
                date_format = "%Y"
                group_clause = f"strftime('%Y', {date_column})"
            else:
                raise ValueError(f"Unsupported frequency: {frequency}")
            
            query = f"""
            SELECT 
                {group_clause} as period,
                {aggregation}({value_column}) as {value_column}_{aggregation.lower()},
                COUNT(*) as count
            FROM data
            WHERE {date_column} IS NOT NULL AND {value_column} IS NOT NULL
            GROUP BY {group_clause}
            ORDER BY period
            LIMIT {settings.MAX_QUERY_ROWS}
            """
            
            result_df = pd.read_sql_query(query, conn)
            
            result = {
                "query": query,
                "data": result_df.fillna("").to_dict('records'),
                "columns": result_df.columns.tolist(),
                "row_count": len(result_df),
                "date_column": date_column,
                "value_column": value_column,
                "aggregation": aggregation,
                "frequency": frequency
            }
            
            return {
                "result": result,
                "rationale": f"Executed time series aggregation: {aggregation} of {value_column} by {frequency}",
                "confidence": 0.9
            }
            
        finally:
            conn.close()
    
    def _is_safe_query(self, query: str) -> bool:
        """Check if SQL query is safe to execute."""
        query_upper = query.upper()
        
        # Block dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'ATTACH', 'DETACH'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        # Allow only SELECT operations
        if not query_upper.strip().startswith('SELECT'):
            return False
        
        # Check for multiple statements
        if ';' in query.rstrip(';'):
            return False
        
        return True

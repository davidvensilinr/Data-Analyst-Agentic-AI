import re
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from app.models.schemas import StepType
from config.settings import settings


class ValidationError(Exception):
    """Custom validation error."""
    pass


class InputValidator:
    """Validates user inputs and API requests."""
    
    @staticmethod
    def validate_dataset_upload(file_size: int, filename: str) -> None:
        """Validate dataset upload parameters."""
        if file_size > settings.MAX_FILE_SIZE:
            raise ValidationError(
                f"File size {file_size} exceeds maximum allowed size {settings.MAX_FILE_SIZE}"
            )
        
        if not filename:
            raise ValidationError("Filename is required")
        
        # Check file extension
        allowed_extensions = {'.csv', '.json', '.parquet', '.xlsx', '.xls', '.tsv'}
        file_extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"File type {file_extension} not allowed. Allowed types: {allowed_extensions}"
            )
    
    @staticmethod
    def validate_question(question: str) -> str:
        """Validate and sanitize user question."""
        if not question or not question.strip():
            raise ValidationError("Question cannot be empty")
        
        # Clean the question
        question = question.strip()
        
        # Check for prompt injection attempts
        dangerous_patterns = [
            r'(?i)(ignore|override|bypass).*previous.*instruction',
            r'(?i)(system|assistant|user):',
            r'(?i)(execute|run|eval).*code',
            r'(?i)(delete|drop|truncate).*table',
            r'(?i)(insert|update).*set',
            r'(?i)(grant|revoke).*privilege',
            r'(?i)(create|alter).*table',
            r'(?i)(exec|sp_executesql)',
            r'(?i)(union.*select)',
            r'(?i)(script|javascript|vbscript)',
            r'(?i)(<|>).*script',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, question):
                raise ValidationError(
                    f"Question contains potentially dangerous content: {pattern}"
                )
        
        # Length validation
        if len(question) > 2000:
            raise ValidationError("Question too long (max 2000 characters)")
        
        return question
    
    @staticmethod
    def validate_step_spec(step_type: StepType, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate step specification."""
        if not isinstance(spec, dict):
            raise ValidationError("Step specification must be a dictionary")
        
        # Type-specific validation
        if step_type == StepType.SQL:
            InputValidator._validate_sql_spec(spec)
        elif step_type == StepType.CLEAN:
            InputValidator._validate_clean_spec(spec)
        elif step_type == StepType.ANALYSIS:
            InputValidator._validate_analysis_spec(spec)
        elif step_type == StepType.VISUALIZATION:
            InputValidator._validate_visualization_spec(spec)
        elif step_type == StepType.ANOMALY:
            InputValidator._validate_anomaly_spec(spec)
        
        return spec
    
    @staticmethod
    def _validate_sql_spec(spec: Dict[str, Any]) -> None:
        """Validate SQL step specification."""
        if "query" in spec:
            query = spec["query"]
            
            # Check for dangerous SQL patterns
            dangerous_sql = [
                r'(?i)\b(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE)\b',
                r'(?i)\b(UNION.*SELECT|EXEC.*sp_|xp_cmdshell)\b',
                r'(?i)\b(GRANT|REVOKE)\b',
                r'(?i)\b(ATTACH|DETACH)\b',
                r';\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)',
            ]
            
            for pattern in dangerous_sql:
                if re.search(pattern, query):
                    raise ValidationError(f"SQL query contains dangerous pattern: {pattern}")
            
            # Ensure it's a SELECT query
            if not query.strip().upper().startswith('SELECT'):
                raise ValidationError("Only SELECT queries are allowed")
            
            # Check for multiple statements
            if ';' in query.rstrip(';'):
                raise ValidationError("Multiple SQL statements are not allowed")
        
        # Validate row limit
        if "limit" in spec and spec["limit"] > settings.MAX_QUERY_ROWS:
            raise ValidationError(
                f"Query limit {spec['limit']} exceeds maximum {settings.MAX_QUERY_ROWS}"
            )
    
    @staticmethod
    def _validate_clean_spec(spec: Dict[str, Any]) -> None:
        """Validate cleaning step specification."""
        operations = spec.get("operations", [])
        
        if not operations:
            raise ValidationError("Cleaning operations must be specified")
        
        valid_operations = [
            "handle_missing_values", "remove_duplicates", "fix_data_types",
            "handle_outliers", "standardize_formats", "validate_data"
        ]
        
        for op in operations:
            if op not in valid_operations:
                raise ValidationError(f"Invalid cleaning operation: {op}")
        
        # Validate missing value strategy
        if "missing_strategy" in spec:
            strategy = spec["missing_strategy"]
            valid_strategies = [
                "drop", "drop_columns", "impute_mean", "impute_median",
                "impute_mode", "impute_forward", "impute_backward"
            ]
            
            if strategy not in valid_strategies:
                raise ValidationError(f"Invalid missing value strategy: {strategy}")
    
    @staticmethod
    def _validate_analysis_spec(spec: Dict[str, Any]) -> None:
        """Validate analysis step specification."""
        operation = spec.get("operation")
        
        if not operation:
            raise ValidationError("Analysis operation must be specified")
        
        valid_operations = [
            "descriptive", "correlation", "distribution", "hypothesis",
            "clustering", "pca", "cohort"
        ]
        
        if operation not in valid_operations:
            raise ValidationError(f"Invalid analysis operation: {operation}")
        
        # Validate hypothesis testing parameters
        if operation == "hypothesis":
            test_type = spec.get("test_type")
            valid_tests = ["t_test", "chi_square", "anova"]
            
            if test_type not in valid_tests:
                raise ValidationError(f"Invalid hypothesis test: {test_type}")
    
    @staticmethod
    def _validate_visualization_spec(spec: Dict[str, Any]) -> None:
        """Validate visualization step specification."""
        chart_type = spec.get("chart_type", "auto")
        
        valid_chart_types = [
            "auto", "histogram", "scatter", "line", "bar", "box",
            "heatmap", "pie", "violin"
        ]
        
        if chart_type not in valid_chart_types:
            raise ValidationError(f"Invalid chart type: {chart_type}")
        
        # Validate bins for histograms
        if chart_type == "histogram" and "bins" in spec:
            bins = spec["bins"]
            if not isinstance(bins, int) or bins < 5 or bins > 100:
                raise ValidationError("Histogram bins must be an integer between 5 and 100")
    
    @staticmethod
    def _validate_anomaly_spec(spec: Dict[str, Any]) -> None:
        """Validate anomaly detection specification."""
        method = spec.get("method", "isolation_forest")
        
        valid_methods = [
            "isolation_forest", "statistical", "zscore", "iqr",
            "time_series", "auto"
        ]
        
        if method not in valid_methods:
            raise ValidationError(f"Invalid anomaly detection method: {method}")
        
        # Validate contamination parameter
        if method == "isolation_forest" and "contamination" in spec:
            contamination = spec["contamination"]
            if not isinstance(contamination, (int, float)) or contamination <= 0 or contamination >= 1:
                raise ValidationError("Contamination must be a float between 0 and 1")
    
    @staticmethod
    def sanitize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize column names for SQL compatibility."""
        # Remove special characters and convert to lowercase
        df.columns = [
            re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
            for col in df.columns
        ]
        
        # Ensure names don't start with numbers
        df.columns = [
            f'col_{col}' if col[0].isdigit() else col
            for col in df.columns
        ]
        
        # Remove duplicate column names
        seen = set()
        new_columns = []
        for col in df.columns:
            count = 1
            new_col = col
            while new_col in seen:
                new_col = f'{col}_{count}'
                count += 1
            seen.add(new_col)
            new_columns.append(new_col)
        
        df.columns = new_columns
        return df
    
    @staticmethod
    def validate_pagination(skip: int, limit: int) -> tuple[int, int]:
        """Validate pagination parameters."""
        if skip < 0:
            raise ValidationError("Skip parameter must be non-negative")
        
        if limit <= 0 or limit > 1000:
            raise ValidationError("Limit parameter must be between 1 and 1000")
        
        return skip, limit
    
    @staticmethod
    def sanitize_sensitive_data(data: Dict[str, Any], sensitive_columns: List[str] = None) -> Dict[str, Any]:
        """Sanitize sensitive data from responses."""
        if sensitive_columns is None:
            sensitive_columns = settings.SENSITIVE_COLUMNS
        
        def _sanitize_value(key: str, value: Any) -> Any:
            # Check if key contains sensitive information
            key_lower = key.lower()
            for sensitive in sensitive_columns:
                if sensitive in key_lower:
                    return "[REDACTED]"
            
            # Recursively sanitize nested structures
            if isinstance(value, dict):
                return {k: _sanitize_value(k, v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_sanitize_value(f"{key}[{i}]", item) for i, item in enumerate(value)]
            else:
                return value
        
        return {k: _sanitize_value(k, v) for k, v in data.items()}


class SecurityValidator:
    """Security-focused validation."""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format."""
        if not api_key:
            return False
        
        # Basic format validation (adjust based on your API key format)
        if len(api_key) < 16:
            return False
        
        # Check for common patterns
        if re.search(r'[^a-zA-Z0-9_\-]', api_key):
            return False
        
        return True
    
    @staticmethod
    def validate_user_input(input_string: str, max_length: int = 1000) -> str:
        """Validate and sanitize user input."""
        if not input_string:
            return ""
        
        input_string = input_string.strip()
        
        # Length validation
        if len(input_string) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)")
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\']
        for char in dangerous_chars:
            input_string = input_string.replace(char, '')
        
        return input_string
    
    @staticmethod
    def check_sql_injection(query: str) -> bool:
        """Check for SQL injection patterns."""
        injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b.*\b1\s*=\s*1\b)",
            r"(\bAND\b.*\b1\s*=\s*1\b)",
            r"(\bWHERE\b.*\bOR\b)",
            r"(\bWHERE\b.*\bAND\b.*\bOR\b)",
            r"(\bEXEC\b.*\bxp_cmdshell\b)",
            r"(\bEXEC\b.*\bsp_executesql\b)",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path to prevent directory traversal."""
        if not file_path:
            return False
        
        # Check for directory traversal
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in file_path:
                return False
        
        return True


class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, client_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if client is allowed to make request."""
        import time
        
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < limit:
            self.requests[client_id].append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def validate_pagination_params(skip: int = 0, limit: int = 50) -> tuple[int, int]:
    """FastAPI dependency for pagination validation."""
    return InputValidator.validate_pagination(skip, limit)


def check_rate_limit(client_id: str, limit: int = 100, window: int = 3600):
    """FastAPI dependency for rate limiting."""
    if not rate_limiter.is_allowed(client_id, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

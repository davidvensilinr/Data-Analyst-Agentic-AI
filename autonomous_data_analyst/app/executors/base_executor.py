from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.database import Dataset


class BaseExecutor(ABC):
    """Base class for all step executors."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    @abstractmethod
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the step.
        
        Args:
            dataset: The dataset to process
            spec: Step specification with parameters
            previous_results: Results from previous steps
            
        Returns:
            Dictionary containing:
            - result: The execution result
            - model_prompt: LLM prompt if used
            - model_output: LLM output if used
            - tool_call: Tool call details
            - tool_result: Tool execution result
            - rationale: Human-readable explanation
            - confidence: Confidence score 0-1
        """
        pass
    
    def _validate_spec(self, spec: Dict[str, Any], required_fields: list) -> None:
        """Validate step specification."""
        for field in required_fields:
            if field not in spec:
                raise ValueError(f"Missing required field '{field}' in step specification")
    
    def _get_dataset_dataframe(self, dataset: Dataset):
        """Load dataset as pandas DataFrame."""
        import pandas as pd
        import os
        
        if not os.path.exists(dataset.file_path):
            raise FileNotFoundError(f"Dataset file not found: {dataset.file_path}")
        
        try:
            if dataset.file_type == 'csv':
                return pd.read_csv(dataset.file_path)
            elif dataset.file_type == 'excel':
                return pd.read_excel(dataset.file_path)
            elif dataset.file_type == 'json':
                return pd.read_json(dataset.file_path)
            elif dataset.file_type == 'parquet':
                return pd.read_parquet(dataset.file_path)
            elif dataset.file_type == 'tsv':
                return pd.read_csv(dataset.file_path, sep='\\t')
            else:
                raise ValueError(f"Unsupported file type: {dataset.file_type}")
        except Exception as e:
            raise ValueError(f"Failed to load dataset: {str(e)}")
    
    def _save_dataframe(self, df, dataset: Dataset, suffix: str = "_processed") -> str:
        """Save DataFrame to file and return new file path."""
        import pandas as pd
        import os
        
        # Generate new filename
        base_name = os.path.splitext(dataset.file_path)[0]
        extension = os.path.splitext(dataset.file_path)[1]
        new_file_path = f"{base_name}{suffix}{extension}"
        
        try:
            if dataset.file_type == 'csv':
                df.to_csv(new_file_path, index=False)
            elif dataset.file_type == 'excel':
                df.to_excel(new_file_path, index=False)
            elif dataset.file_type == 'json':
                df.to_json(new_file_path, orient='records')
            elif dataset.file_type == 'parquet':
                df.to_parquet(new_file_path, index=False)
            elif dataset.file_type == 'tsv':
                df.to_csv(new_file_path, sep='\\t', index=False)
            else:
                raise ValueError(f"Unsupported file type: {dataset.file_type}")
            
            return new_file_path
        except Exception as e:
            raise ValueError(f"Failed to save dataset: {str(e)}")
    
    def _sanitize_column_names(self, df):
        """Sanitize column names for SQL compatibility."""
        import re
        df.columns = [
            re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
            for col in df.columns
        ]
        return df
    
    def _get_numeric_columns(self, df):
        """Get list of numeric columns."""
        return df.select_dtypes(include=['number']).columns.tolist()
    
    def _get_categorical_columns(self, df):
        """Get list of categorical columns."""
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def _get_datetime_columns(self, df):
        """Get list of datetime columns."""
        return df.select_dtypes(include=['datetime64']).columns.tolist()

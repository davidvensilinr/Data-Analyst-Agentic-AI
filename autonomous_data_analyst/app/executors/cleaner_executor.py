import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset


class CleanerExecutor(BaseExecutor):
    """Executor for data cleaning steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute data cleaning operations."""
        
        operations = spec.get("operations", [])
        
        if not operations:
            raise ValueError("No cleaning operations specified")
        
        df = self._get_dataset_dataframe(dataset)
        original_shape = df.shape
        changes_made = []
        
        for operation in operations:
            if operation == "handle_missing_values":
                df = await self._handle_missing_values(df, spec, changes_made)
            elif operation == "remove_duplicates":
                df = await self._remove_duplicates(df, spec, changes_made)
            elif operation == "fix_data_types":
                df = await self._fix_data_types(df, spec, changes_made)
            elif operation == "handle_outliers":
                df = await self._handle_outliers(df, spec, changes_made)
            elif operation == "standardize_formats":
                df = await self._standardize_formats(df, spec, changes_made)
            elif operation == "validate_data":
                df = await self._validate_data(df, spec, changes_made)
            else:
                raise ValueError(f"Unknown cleaning operation: {operation}")
        
        # Save cleaned dataset
        cleaned_file_path = self._save_dataframe(df, dataset, "_cleaned")
        
        # Generate summary
        final_shape = df.shape
        rows_removed = original_shape[0] - final_shape[0]
        cols_removed = original_shape[1] - final_shape[1]
        
        result = {
            "cleaned_dataset_path": cleaned_file_path,
            "original_shape": original_shape,
            "final_shape": final_shape,
            "rows_removed": rows_removed,
            "columns_removed": cols_removed,
            "changes_made": changes_made,
            "cleaning_summary": f"Removed {rows_removed} rows and {cols_removed} columns. Applied {len(changes_made)} cleaning operations."
        }
        
        return {
            "result": result,
            "rationale": f"Data cleaning completed. {result['cleaning_summary']}",
            "confidence": 0.85
        }
    
    async def _handle_missing_values(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        strategy = spec.get("missing_strategy", "drop")
        columns = spec.get("missing_columns", None)  # None means all columns
        
        if columns is None:
            columns = df.columns.tolist()
        
        original_missing = df[columns].isnull().sum().sum()
        
        if strategy == "drop":
            # Drop rows with missing values
            df = df.dropna(subset=columns)
            changes_made.append(f"Dropped rows with missing values in {len(columns)} columns")
        
        elif strategy == "drop_columns":
            # Drop columns with missing values
            cols_to_drop = [col for col in columns if df[col].isnull().any()]
            df = df.drop(columns=cols_to_drop)
            changes_made.append(f"Dropped {len(cols_to_drop)} columns with missing values")
        
        elif strategy == "impute_mean":
            # Impute numeric columns with mean
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    mean_val = df[col].mean()
                    df[col].fillna(mean_val, inplace=True)
            changes_made.append(f"Imputed {len(numeric_cols)} numeric columns with mean values")
        
        elif strategy == "impute_median":
            # Impute numeric columns with median
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    median_val = df[col].median()
                    df[col].fillna(median_val, inplace=True)
            changes_made.append(f"Imputed {len(numeric_cols)} numeric columns with median values")
        
        elif strategy == "impute_mode":
            # Impute all columns with mode
            for col in columns:
                if df[col].isnull().any():
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col].fillna(mode_val[0], inplace=True)
            changes_made.append(f"Imputed {len(columns)} columns with mode values")
        
        elif strategy == "impute_forward":
            # Forward fill
            df[columns] = df[columns].fillna(method='ffill')
            changes_made.append(f"Applied forward fill to {len(columns)} columns")
        
        elif strategy == "impute_backward":
            # Backward fill
            df[columns] = df[columns].fillna(method='bfill')
            changes_made.append(f"Applied backward fill to {len(columns)} columns")
        
        final_missing = df[columns].isnull().sum().sum()
        changes_made.append(f"Reduced missing values from {original_missing} to {final_missing}")
        
        return df
    
    async def _remove_duplicates(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Remove duplicate rows."""
        subset = spec.get("duplicate_subset", None)
        keep = spec.get("duplicate_keep", "first")
        
        original_count = len(df)
        df = df.drop_duplicates(subset=subset, keep=keep)
        duplicates_removed = original_count - len(df)
        
        if duplicates_removed > 0:
            subset_desc = f"based on {subset}" if subset else "based on all columns"
            changes_made.append(f"Removed {duplicates_removed} duplicate rows {subset_desc}")
        
        return df
    
    async def _fix_data_types(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Fix data types in the dataset."""
        type_conversions = spec.get("type_conversions", {})
        
        for col, target_type in type_conversions.items():
            if col not in df.columns:
                continue
            
            original_type = str(df[col].dtype)
            
            try:
                if target_type == "datetime":
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif target_type == "numeric":
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif target_type == "category":
                    df[col] = df[col].astype('category')
                elif target_type == "string":
                    df[col] = df[col].astype(str)
                else:
                    df[col] = df[col].astype(target_type)
                
                new_type = str(df[col].dtype)
                changes_made.append(f"Converted {col} from {original_type} to {new_type}")
                
            except Exception as e:
                changes_made.append(f"Failed to convert {col}: {str(e)}")
        
        return df
    
    async def _handle_outliers(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Handle outliers in numeric columns."""
        method = spec.get("outlier_method", "iqr")
        columns = spec.get("outlier_columns", None)
        action = spec.get("outlier_action", "remove")
        
        if columns is None:
            columns = self._get_numeric_columns(df)
        
        outliers_removed = 0
        
        for col in columns:
            if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            original_count = len(df)
            
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                if action == "remove":
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                elif action == "cap":
                    df[col] = df[col].clip(lower_bound, upper_bound)
                elif action == "transform":
                    # Log transformation for positive values
                    if (df[col] > 0).all():
                        df[col] = np.log1p(df[col])
            
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                threshold = spec.get("zscore_threshold", 3)
                
                if action == "remove":
                    df = df[z_scores <= threshold]
                elif action == "cap":
                    df.loc[z_scores > threshold, col] = df[col].median()
            
            outliers_removed += original_count - len(df)
        
        if outliers_removed > 0:
            changes_made.append(f"Handled {outliers_removed} outliers using {method} method")
        
        return df
    
    async def _standardize_formats(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Standardize text formats."""
        text_columns = spec.get("text_columns", [])
        date_columns = spec.get("date_columns", [])
        
        # Standardize text columns
        for col in text_columns:
            if col in df.columns:
                # Convert to string and strip whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Convert to lowercase if specified
                if spec.get("lowercase_text", False):
                    df[col] = df[col].str.lower()
                
                # Remove special characters if specified
                if spec.get("remove_special_chars", False):
                    df[col] = df[col].str.replace(r'[^a-zA-Z0-9\\s]', '', regex=True)
                
                changes_made.append(f"Standardized text format for column {col}")
        
        # Standardize date columns
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    changes_made.append(f"Standardized date format for column {col}")
                except Exception as e:
                    changes_made.append(f"Failed to standardize date format for {col}: {str(e)}")
        
        return df
    
    async def _validate_data(self, df: pd.DataFrame, spec: Dict[str, Any], changes_made: List[str]) -> pd.DataFrame:
        """Validate data against constraints."""
        validations = spec.get("validations", [])
        validation_errors = []
        
        for validation in validations:
            column = validation.get("column")
            rule = validation.get("rule")
            value = validation.get("value")
            
            if column not in df.columns:
                continue
            
            if rule == "not_null":
                null_count = df[column].isnull().sum()
                if null_count > 0:
                    validation_errors.append(f"Column {column} has {null_count} null values")
            
            elif rule == "unique":
                duplicate_count = df[column].duplicated().sum()
                if duplicate_count > 0:
                    validation_errors.append(f"Column {column} has {duplicate_count} duplicate values")
            
            elif rule == "range":
                min_val, max_val = value
                out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()
                if out_of_range > 0:
                    validation_errors.append(f"Column {column} has {out_of_range} values outside range [{min_val}, {max_val}]")
            
            elif rule == "length":
                max_length = value
                too_long = (df[column].astype(str).str.len() > max_length).sum()
                if too_long > 0:
                    validation_errors.append(f"Column {column} has {too_long} values longer than {max_length} characters")
        
        if validation_errors:
            changes_made.append(f"Data validation found {len(validation_errors)} issues")
        else:
            changes_made.append("Data validation passed successfully")
        
        return df

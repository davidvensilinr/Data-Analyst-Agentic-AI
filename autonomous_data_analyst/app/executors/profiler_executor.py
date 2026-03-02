import pandas as pd
import numpy as np
from typing import Dict, Any
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset


class ProfilerExecutor(BaseExecutor):
    """Executor for data profiling steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute data profiling."""
        
        operation = spec.get("operation", "basic_profile")
        
        if operation == "basic_profile":
            return await self._basic_profile(dataset)
        elif operation == "full_profile":
            return await self._full_profile(dataset)
        elif operation == "quality_check":
            return await self._quality_check(dataset)
        else:
            raise ValueError(f"Unknown profiling operation: {operation}")
    
    async def _basic_profile(self, dataset: Dataset) -> Dict[str, Any]:
        """Generate basic data profile."""
        df = self._get_dataset_dataframe(dataset)
        
        profile_info = {
            "schema": {
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "shape": df.shape,
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
            },
            "basic_stats": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "numeric_columns": self._get_numeric_columns(df),
                "categorical_columns": self._get_categorical_columns(df),
                "datetime_columns": self._get_datetime_columns(df)
            },
            "missing_values": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict()
        }
        
        return {
            "result": profile_info,
            "rationale": "Generated basic data profile including schema, statistics, and missing value analysis",
            "confidence": 0.95
        }
    
    async def _full_profile(self, dataset: Dataset) -> Dict[str, Any]:
        """Generate comprehensive data profile."""
        df = self._get_dataset_dataframe(dataset)
        
        # Basic info
        basic_info = await self._basic_profile(dataset)
        profile_info = basic_info["result"]
        
        # Detailed statistics for numeric columns
        numeric_cols = self._get_numeric_columns(df)
        if numeric_cols:
            numeric_stats = {}
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    numeric_stats[col] = {
                        "mean": float(series.mean()),
                        "median": float(series.median()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "q25": float(series.quantile(0.25)),
                        "q75": float(series.quantile(0.75)),
                        "skewness": float(series.skew()),
                        "kurtosis": float(series.kurtosis()),
                        "zeros": int((series == 0).sum()),
                        "unique_count": int(series.nunique())
                    }
            profile_info["numeric_statistics"] = numeric_stats
        
        # Detailed statistics for categorical columns
        categorical_cols = self._get_categorical_columns(df)
        if categorical_cols:
            categorical_stats = {}
            for col in categorical_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    value_counts = series.value_counts().head(10)
                    categorical_stats[col] = {
                        "unique_count": int(series.nunique()),
                        "most_frequent": str(series.mode().iloc[0]) if not series.mode().empty else None,
                        "least_frequent": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                        "top_values": value_counts.to_dict(),
                        "avg_length": float(series.astype(str).str.len().mean())
                    }
            profile_info["categorical_statistics"] = categorical_stats
        
        # Data quality metrics
        quality_metrics = {
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": float(df.duplicated().sum() / len(df) * 100),
            "complete_rows": int(df.dropna().shape[0]),
            "complete_percentage": float(df.dropna().shape[0] / len(df) * 100),
            "empty_columns": [col for col in df.columns if df[col].isnull().all()],
            "single_value_columns": [col for col in df.columns if df[col].nunique() == 1]
        }
        profile_info["quality_metrics"] = quality_metrics
        
        # Sample data
        sample_size = min(10, len(df))
        profile_info["sample_data"] = df.head(sample_size).fillna("").to_dict('records')
        
        return {
            "result": profile_info,
            "rationale": "Generated comprehensive data profile including detailed statistics, quality metrics, and sample data",
            "confidence": 0.95
        }
    
    async def _quality_check(self, dataset: Dataset) -> Dict[str, Any]:
        """Perform data quality assessment."""
        df = self._get_dataset_dataframe(dataset)
        
        quality_issues = []
        recommendations = []
        
        # Check missing values
        missing_pct = df.isnull().sum() / len(df) * 100
        high_missing_cols = missing_pct[missing_pct > 50].index.tolist()
        if high_missing_cols:
            quality_issues.append(f"Columns with >50% missing values: {high_missing_cols}")
            recommendations.append("Consider imputing or removing columns with high missing values")
        
        # Check duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            quality_issues.append(f"Found {duplicate_count} duplicate rows")
            recommendations.append("Remove duplicate rows to improve data quality")
        
        # Check for constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        if constant_cols:
            quality_issues.append(f"Constant columns (no variation): {constant_cols}")
            recommendations.append("Consider removing constant columns as they provide no analytical value")
        
        # Check numeric columns for outliers
        numeric_cols = self._get_numeric_columns(df)
        outlier_cols = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                outlier_cols.append(col)
        
        if outlier_cols:
            quality_issues.append(f"Potential outliers detected in: {outlier_cols}")
            recommendations.append("Investigate and handle outliers appropriately")
        
        # Check data types
        type_issues = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    pd.to_numeric(df[col])
                    type_issues.append(f"Column '{col}' appears numeric but stored as text")
                except:
                    pass
        
        if type_issues:
            quality_issues.extend(type_issues)
            recommendations.append("Convert columns to appropriate data types")
        
        # Overall quality score
        max_issues = 10  # Arbitrary maximum for normalization
        issue_count = len(quality_issues)
        quality_score = max(0, 100 - (issue_count / max_issues * 100))
        
        result = {
            "quality_score": quality_score,
            "issues": quality_issues,
            "recommendations": recommendations,
            "detailed_metrics": {
                "missing_value_summary": missing_pct.to_dict(),
                "duplicate_count": int(duplicate_count),
                "constant_columns": constant_cols,
                "outlier_columns": outlier_cols,
                "type_issues": type_issues
            }
        }
        
        return {
            "result": result,
            "rationale": f"Data quality assessment completed with score {quality_score:.1f}/100. Found {len(quality_issues)} issues to address.",
            "confidence": 0.9
        }

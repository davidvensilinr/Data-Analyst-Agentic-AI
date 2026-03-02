import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
from typing import Dict, Any, List
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset


class AnomalyExecutor(BaseExecutor):
    """Executor for anomaly detection steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute anomaly detection."""
        
        method = spec.get("method", "isolation_forest")
        
        if method == "isolation_forest":
            return await self._isolation_forest_detection(dataset, spec)
        elif method == "statistical":
            return await self._statistical_detection(dataset, spec)
        elif method == "zscore":
            return await self._zscore_detection(dataset, spec)
        elif method == "iqr":
            return await self._iqr_detection(dataset, spec)
        elif method == "time_series":
            return await self._time_series_anomaly_detection(dataset, spec)
        elif method == "auto":
            return await self._auto_anomaly_detection(dataset, spec)
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")
    
    async def _isolation_forest_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using Isolation Forest."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if not columns:
            columns = self._get_numeric_columns(df)
        
        if len(columns) < 2:
            raise ValueError("Need at least 2 numeric columns for Isolation Forest")
        
        # Prepare data
        anomaly_data = df[columns].dropna()
        if len(anomaly_data) < 100:
            raise ValueError("Need at least 100 data points for reliable anomaly detection")
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(anomaly_data)
        
        # Apply Isolation Forest
        contamination = spec.get("contamination", 0.1)  # Expected proportion of anomalies
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        anomaly_labels = iso_forest.fit_predict(scaled_data)
        anomaly_scores = iso_forest.decision_function(scaled_data)
        
        # Add results to original data
        result_data = anomaly_data.copy()
        result_data['anomaly_label'] = anomaly_labels
        result_data['anomaly_score'] = anomaly_scores
        result_data['is_anomaly'] = anomaly_labels == -1
        
        # Get anomaly summary
        anomalies = result_data[result_data['is_anomaly']]
        anomaly_count = len(anomalies)
        anomaly_percentage = (anomaly_count / len(result_data)) * 100
        
        # Analyze anomalies by column
        anomaly_analysis = {}
        for col in columns:
            normal_values = result_data[result_data['is_anomaly'] == False][col]
            anomaly_values = result_data[result_data['is_anomaly'] == True][col]
            
            if len(normal_values) > 0 and len(anomaly_values) > 0:
                anomaly_analysis[col] = {
                    "normal_mean": float(normal_values.mean()),
                    "normal_std": float(normal_values.std()),
                    "anomaly_mean": float(anomaly_values.mean()),
                    "anomaly_std": float(anomaly_values.std()),
                    "difference_ratio": float(abs(anomaly_values.mean() - normal_values.mean()) / normal_values.std()) if normal_values.std() > 0 else float('inf')
                }
        
        result = {
            "method": "Isolation Forest",
            "anomaly_count": anomaly_count,
            "anomaly_percentage": anomaly_percentage,
            "contamination": contamination,
            "columns_analyzed": columns,
            "anomaly_analysis": anomaly_analysis,
            "anomaly_data": anomalies.head(100).to_dict('records'),  # First 100 anomalies
            "summary": f"Detected {anomaly_count} anomalies ({anomaly_percentage:.2f}%) using Isolation Forest"
        }
        
        return {
            "result": result,
            "rationale": f"Applied Isolation Forest to detect anomalies in {len(columns)} features",
            "confidence": 0.85
        }
    
    async def _statistical_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using statistical methods."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if not columns:
            columns = self._get_numeric_columns(df)
        
        if not columns:
            raise ValueError("No numeric columns found for statistical anomaly detection")
        
        threshold = spec.get("threshold", 3.0)  # Standard deviations
        method = spec.get("statistical_method", "combined")
        
        anomaly_data = df[columns].copy()
        anomaly_data['is_anomaly'] = False
        anomaly_data['anomaly_reasons'] = ""
        
        anomaly_count = 0
        column_anomalies = {}
        
        for col in columns:
            series = df[col].dropna()
            if len(series) < 30:
                continue
            
            col_anomalies = []
            
            if method in ["zscore", "combined"]:
                # Z-score method
                z_scores = np.abs(stats.zscore(series))
                z_anomalies = z_scores > threshold
                col_anomalies.append(z_anomalies)
            
            if method in ["iqr", "combined"]:
                # IQR method
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                iqr_anomalies = (series < lower_bound) | (series > upper_bound)
                col_anomalies.append(iqr_anomalies)
            
            # Combine methods
            if method == "combined":
                combined_anomalies = np.any(col_anomalies, axis=0)
            else:
                combined_anomalies = col_anomalies[0]
            
            # Update anomaly data
            anomaly_indices = series.index[combined_anomalies]
            for idx in anomaly_indices:
                if not anomaly_data.loc[idx, 'is_anomaly']:
                    anomaly_count += 1
                    anomaly_data.loc[idx, 'is_anomaly'] = True
                    anomaly_data.loc[idx, 'anomaly_reasons'] = f"{col}"
                else:
                    anomaly_data.loc[idx, 'anomaly_reasons'] += f", {col}"
            
            column_anomalies[col] = {
                "anomaly_count": int(combined_anomalies.sum()),
                "anomaly_percentage": float(combined_anomalies.sum() / len(series) * 100),
                "threshold": threshold,
                "method": method
            }
        
        # Get anomaly records
        anomalies = anomaly_data[anomaly_data['is_anomaly']]
        
        result = {
            "method": f"Statistical ({method})",
            "anomaly_count": anomaly_count,
            "anomaly_percentage": float(anomaly_count / len(df) * 100),
            "threshold": threshold,
            "columns_analyzed": columns,
            "column_anomalies": column_anomalies,
            "anomaly_data": anomalies.head(100).to_dict('records'),
            "summary": f"Detected {anomaly_count} anomalies ({anomaly_count/len(df)*100:.2f}%) using statistical methods"
        }
        
        return {
            "result": result,
            "rationale": f"Applied statistical anomaly detection using {method} method on {len(columns)} columns",
            "confidence": 0.8
        }
    
    async def _zscore_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using Z-score method."""
        spec["statistical_method"] = "zscore"
        return await self._statistical_detection(dataset, spec)
    
    async def _iqr_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using IQR method."""
        spec["statistical_method"] = "iqr"
        return await self._statistical_detection(dataset, spec)
    
    async def _time_series_anomaly_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in time series data."""
        df = self._get_dataset_dataframe(dataset)
        
        date_column = spec.get("date_column")
        value_column = spec.get("value_column")
        method = spec.get("time_series_method", "seasonal_decompose")
        
        if not date_column or not value_column:
            raise ValueError("Both date_column and value_column are required for time series anomaly detection")
        
        # Prepare data
        ts_data = df[[date_column, value_column]].copy()
        ts_data[date_column] = pd.to_datetime(ts_data[date_column])
        ts_data = ts_data.sort_values(date_column).dropna()
        
        if len(ts_data) < 50:
            raise ValueError("Need at least 50 data points for time series anomaly detection")
        
        # Set date as index
        ts_data.set_index(date_column, inplace=True)
        
        anomalies = []
        
        if method == "seasonal_decompose":
            try:
                from statsmodels.tsa.seasonal import seasonal_decompose
                
                # Perform seasonal decomposition
                decomposition = seasonal_decompose(ts_data[value_column], model='additive', period=12)
                residuals = decomposition.resid.dropna()
                
                # Detect anomalies in residuals
                residual_threshold = residuals.std() * 3
                anomaly_indices = residuals[abs(residuals) > residual_threshold].index
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "timestamp": idx.isoformat(),
                        "value": float(ts_data.loc[idx, value_column]),
                        "residual": float(residuals.loc[idx]),
                        "reason": "Seasonal decomposition residual outlier"
                    })
                    
            except ImportError:
                # Fallback to simple moving average
                method = "moving_average"
        
        if method == "moving_average":
            # Moving average method
            window = spec.get("window", 12)
            threshold = spec.get("threshold", 2.0)
            
            rolling_mean = ts_data[value_column].rolling(window=window).mean()
            rolling_std = ts_data[value_column].rolling(window=window).std()
            
            # Detect anomalies
            deviation = abs(ts_data[value_column] - rolling_mean) / rolling_std
            anomaly_indices = deviation[deviation > threshold].index
            
            for idx in anomaly_indices:
                anomalies.append({
                    "timestamp": idx.isoformat(),
                    "value": float(ts_data.loc[idx, value_column]),
                    "deviation": float(deviation.loc[idx]),
                    "reason": f"Moving average deviation > {threshold} std"
                })
        
        result = {
            "method": f"Time Series ({method})",
            "anomaly_count": len(anomalies),
            "anomaly_percentage": float(len(anomalies) / len(ts_data) * 100),
            "date_column": date_column,
            "value_column": value_column,
            "time_series_method": method,
            "anomaly_data": anomalies,
            "summary": f"Detected {len(anomalies)} time series anomalies using {method} method"
        }
        
        return {
            "result": result,
            "rationale": f"Applied time series anomaly detection using {method} on {value_column}",
            "confidence": 0.8
        }
    
    async def _auto_anomaly_detection(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically choose best anomaly detection method."""
        df = self._get_dataset_dataframe(dataset)
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        results = []
        
        # Try Isolation Forest if enough numeric columns
        if len(numeric_cols) >= 2:
            try:
                iso_result = await self._isolation_forest_detection(dataset, {"columns": numeric_cols})
                results.append(iso_result["result"])
            except Exception as e:
                pass
        
        # Try statistical detection
        try:
            stat_result = await self._statistical_detection(dataset, {"columns": numeric_cols})
            results.append(stat_result["result"])
        except Exception as e:
            pass
        
        # Try time series if date column exists
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols and numeric_cols:
            try:
                ts_result = await self._time_series_anomaly_detection(
                    dataset, 
                    {"date_column": date_cols[0], "value_column": numeric_cols[0]}
                )
                results.append(ts_result["result"])
            except Exception as e:
                pass
        
        # Choose best result based on anomaly count and confidence
        if not results:
            raise ValueError("No anomaly detection methods could be applied")
        
        # Select result with reasonable anomaly count (not too high, not too low)
        best_result = min(results, key=lambda x: abs(x["anomaly_percentage"] - 5))  # Target ~5% anomalies
        
        best_result["method"] = f"Auto-selected ({best_result['method']})"
        best_result["methods_tried"] = [r["method"] for r in results]
        
        return {
            "result": best_result,
            "rationale": f"Auto-selected best anomaly detection method from {len(results)} methods tried",
            "confidence": 0.75
        }

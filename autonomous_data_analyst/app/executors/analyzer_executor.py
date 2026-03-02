import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from typing import Dict, Any, List
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset


class AnalyzerExecutor(BaseExecutor):
    """Executor for statistical analysis steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute statistical analysis."""
        
        analysis_type = spec.get("operation", "descriptive")
        
        if analysis_type == "descriptive":
            return await self._descriptive_analysis(dataset, spec)
        elif analysis_type == "correlation":
            return await self._correlation_analysis(dataset, spec)
        elif analysis_type == "distribution":
            return await self._distribution_analysis(dataset, spec)
        elif analysis_type == "hypothesis":
            return await self._hypothesis_testing(dataset, spec)
        elif analysis_type == "clustering":
            return await self._clustering_analysis(dataset, spec)
        elif analysis_type == "pca":
            return await self._pca_analysis(dataset, spec)
        elif analysis_type == "cohort":
            return await self._cohort_analysis(dataset, spec)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    async def _descriptive_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform descriptive statistical analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if columns:
            df = df[columns]
        
        results = {}
        
        # Numeric columns analysis
        numeric_cols = self._get_numeric_columns(df)
        if numeric_cols:
            numeric_stats = {}
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    numeric_stats[col] = {
                        "count": len(series),
                        "mean": float(series.mean()),
                        "median": float(series.median()),
                        "std": float(series.std()),
                        "var": float(series.var()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "q25": float(series.quantile(0.25)),
                        "q75": float(series.quantile(0.75)),
                        "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
                        "skewness": float(series.skew()),
                        "kurtosis": float(series.kurtosis()),
                        "cv": float(series.std() / series.mean()) if series.mean() != 0 else float('inf')
                    }
            results["numeric_statistics"] = numeric_stats
        
        # Categorical columns analysis
        categorical_cols = self._get_categorical_columns(df)
        if categorical_cols:
            categorical_stats = {}
            for col in categorical_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    value_counts = series.value_counts()
                    categorical_stats[col] = {
                        "count": len(series),
                        "unique_count": len(value_counts),
                        "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                        "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                        "least_frequent": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                        "least_frequent_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                        "entropy": float(stats.entropy(value_counts.values))
                    }
            results["categorical_statistics"] = categorical_stats
        
        # Overall dataset statistics
        results["overall_statistics"] = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_values": df.isnull().sum().sum(),
            "missing_percentage": float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        }
        
        # Generate insights
        insights = []
        if numeric_cols:
            high_cv_cols = [col for col, stats in numeric_stats.items() if stats["cv"] > 1.0]
            if high_cv_cols:
                insights.append(f"High variability detected in columns: {high_cv_cols}")
            
            skewed_cols = [col for col, stats in numeric_stats.items() if abs(stats["skewness"]) > 2]
            if skewed_cols:
                insights.append(f"Highly skewed columns: {skewed_cols}")
        
        if categorical_cols:
            high_cardinality_cols = [col for col, stats in categorical_stats.items() if stats["unique_count"] > 50]
            if high_cardinality_cols:
                insights.append(f"High cardinality categorical columns: {high_cardinality_cols}")
        
        results["insights"] = insights
        
        return {
            "result": results,
            "rationale": f"Completed descriptive analysis on {len(df)} rows and {len(df.columns)} columns",
            "confidence": 0.95
        }
    
    async def _correlation_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform correlation analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if columns:
            df = df[columns]
        
        numeric_cols = self._get_numeric_columns(df)
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation analysis")
        
        # Calculate correlation matrices
        pearson_corr = df[numeric_cols].corr(method='pearson')
        spearman_corr = df[numeric_cols].corr(method='spearman')
        
        # Find significant correlations
        significant_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates
                    pearson_r = pearson_corr.iloc[i, j]
                    spearman_r = spearman_corr.iloc[i, j]
                    
                    if not pd.isna(pearson_r):
                        # Calculate p-value for Pearson correlation
                        n = len(df[numeric_cols].dropna(subset=[col1, col2]))
                        if n > 2:
                            t_stat = pearson_r * np.sqrt((n - 2) / (1 - pearson_r**2))
                            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
                            
                            if abs(pearson_r) > 0.3 and p_value < 0.05:
                                significant_correlations.append({
                                    "column1": col1,
                                    "column2": col2,
                                    "pearson_correlation": float(pearson_r),
                                    "spearman_correlation": float(spearman_r),
                                    "p_value": float(p_value),
                                    "strength": self._interpret_correlation(abs(pearson_r))
                                })
        
        results = {
            "pearson_correlation_matrix": pearson_corr.fillna("").to_dict(),
            "spearman_correlation_matrix": spearman_corr.fillna("").to_dict(),
            "significant_correlations": significant_correlations,
            "columns_analyzed": numeric_cols
        }
        
        insights = []
        if significant_correlations:
            insights.append(f"Found {len(significant_correlations)} significant correlations")
            strong_corr = [c for c in significant_correlations if c["strength"] in ["Strong", "Very Strong"]]
            if strong_corr:
                insights.append(f"Found {len(strong_corr)} strong correlations")
        else:
            insights.append("No significant correlations found")
        
        results["insights"] = insights
        
        return {
            "result": results,
            "rationale": f"Performed correlation analysis on {len(numeric_cols)} numeric columns",
            "confidence": 0.9
        }
    
    async def _distribution_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform distribution analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if columns:
            df = df[columns]
        
        numeric_cols = self._get_numeric_columns(df)
        results = {}
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 30:  # Need sufficient sample size
                continue
            
            # Normality tests
            shapiro_stat, shapiro_p = stats.shapiro(series[:5000])  # Shapiro test has limit
            ks_stat, ks_p = stats.kstest(series, 'norm', args=(series.mean(), series.std()))
            
            # Distribution characteristics
            distribution_info = {
                "shapiro_wilk": {"statistic": float(shapiro_stat), "p_value": float(shapiro_p)},
                "kolmogorov_smirnov": {"statistic": float(ks_stat), "p_value": float(ks_p)},
                "is_normal": shapiro_p > 0.05 and ks_p > 0.05,
                "histogram_bins": self._create_histogram_data(series),
                "percentiles": {
                    f"p{p}": float(series.quantile(p/100))
                    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
                }
            }
            
            results[col] = distribution_info
        
        # Overall insights
        insights = []
        normal_cols = [col for col, info in results.items() if info["is_normal"]]
        non_normal_cols = [col for col, info in results.items() if not info["is_normal"]]
        
        if normal_cols:
            insights.append(f"Normally distributed columns: {normal_cols}")
        if non_normal_cols:
            insights.append(f"Non-normally distributed columns: {non_normal_cols}")
        
        results["insights"] = insights
        
        return {
            "result": results,
            "rationale": f"Analyzed distributions for {len(results)} numeric columns",
            "confidence": 0.85
        }
    
    async def _hypothesis_testing(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform hypothesis testing."""
        df = self._get_dataset_dataframe(dataset)
        
        test_type = spec.get("test_type")
        group_column = spec.get("group_column")
        value_column = spec.get("value_column")
        
        results = {}
        
        if test_type == "t_test":
            group1 = spec.get("group1")
            group2 = spec.get("group2")
            
            group1_data = df[df[group_column] == group1][value_column].dropna()
            group2_data = df[df[group_column] == group2][value_column].dropna()
            
            if len(group1_data) > 0 and len(group2_data) > 0:
                t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
                
                results = {
                    "test_type": "Independent t-test",
                    "group1": {"name": group1, "n": len(group1_data), "mean": float(group1_data.mean())},
                    "group2": {"name": group2, "n": len(group2_data), "mean": float(group2_data.mean())},
                    "statistic": float(t_stat),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05,
                    "effect_size": float(abs(group1_data.mean() - group2_data.mean()) / np.sqrt(((len(group1_data)-1)*group1_data.var() + (len(group2_data)-1)*group2_data.var()) / (len(group1_data)+len(group2_data)-2)))
                }
        
        elif test_type == "chi_square":
            categorical_col1 = spec.get("categorical_col1")
            categorical_col2 = spec.get("categorical_col2")
            
            contingency_table = pd.crosstab(df[categorical_col1], df[categorical_col2])
            chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            results = {
                "test_type": "Chi-square test of independence",
                "contingency_table": contingency_table.to_dict(),
                "statistic": float(chi2_stat),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "significant": p_value < 0.05
            }
        
        elif test_type == "anova":
            groups = spec.get("groups", [])
            group_data = [df[df[group_column] == group][value_column].dropna() for group in groups]
            group_data = [data for data in group_data if len(data) > 0]
            
            if len(group_data) >= 2:
                f_stat, p_value = stats.f_oneway(*group_data)
                
                results = {
                    "test_type": "One-way ANOVA",
                    "groups": [{"name": group, "n": len(data), "mean": float(data.mean())} 
                              for group, data in zip(groups, group_data)],
                    "statistic": float(f_stat),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05
                }
        
        return {
            "result": results,
            "rationale": f"Performed {results.get('test_type', 'hypothesis test')}",
            "confidence": 0.9
        }
    
    async def _clustering_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform clustering analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        n_clusters = spec.get("n_clusters", 3)
        
        if not columns:
            numeric_cols = self._get_numeric_columns(df)
        else:
            numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for clustering")
        
        # Prepare data
        cluster_data = df[numeric_cols].dropna()
        if len(cluster_data) < n_clusters * 2:
            raise ValueError("Insufficient data for clustering")
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Analyze clusters
        cluster_data['cluster'] = cluster_labels
        cluster_stats = {}
        
        for i in range(n_clusters):
            cluster_subset = cluster_data[cluster_data['cluster'] == i]
            cluster_stats[f"cluster_{i}"] = {
                "size": len(cluster_subset),
                "percentage": float(len(cluster_subset) / len(cluster_data) * 100),
                "centroid": kmeans.cluster_centers_[i].tolist(),
                "characteristics": {
                    col: float(cluster_subset[col].mean())
                    for col in numeric_cols
                }
            }
        
        # Calculate silhouette score
        from sklearn.metrics import silhouette_score
        silhouette_avg = silhouette_score(scaled_data, cluster_labels)
        
        results = {
            "clustering_method": "K-means",
            "n_clusters": n_clusters,
            "cluster_statistics": cluster_stats,
            "silhouette_score": float(silhouette_avg),
            "columns_used": numeric_cols,
            "total_samples": len(cluster_data)
        }
        
        return {
            "result": results,
            "rationale": f"Performed K-means clustering with {n_clusters} clusters on {len(numeric_cols)} features",
            "confidence": 0.8
        }
    
    async def _pca_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Principal Component Analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        n_components = spec.get("n_components", 2)
        
        if not columns:
            numeric_cols = self._get_numeric_columns(df)
        else:
            numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for PCA")
        
        # Prepare data
        pca_data = df[numeric_cols].dropna()
        if len(pca_data) < 10:
            raise ValueError("Insufficient data for PCA")
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pca_data)
        
        # Perform PCA
        pca = PCA(n_components=min(n_components, len(numeric_cols)))
        principal_components = pca.fit_transform(scaled_data)
        
        # Create results
        results = {
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "cumulative_variance_ratio": np.cumsum(pca.explained_variance_ratio_).tolist(),
            "components": pca.components_.tolist(),
            "feature_names": numeric_cols,
            "n_components": len(pca.components_),
            "total_samples": len(pca_data)
        }
        
        # Add principal component data
        pc_columns = [f"PC{i+1}" for i in range(len(pca.components_))]
        pc_df = pd.DataFrame(principal_components, columns=pc_columns)
        results["principal_components"] = pc_df.head(100).to_dict('records')  # First 100 samples
        
        return {
            "result": results,
            "rationale": f"Performed PCA on {len(numeric_cols)} features, reducing to {len(pca.components_)} components",
            "confidence": 0.85
        }
    
    async def _cohort_analysis(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cohort analysis."""
        df = self._get_dataset_dataframe(dataset)
        
        date_column = spec.get("date_column")
        cohort_column = spec.get("cohort_column")
        value_column = spec.get("value_column")
        
        if not all([date_column, cohort_column, value_column]):
            raise ValueError("date_column, cohort_column, and value_column are required")
        
        # Convert date column
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Create cohort periods
        df['cohort_period'] = df[date_column].dt.to_period(spec.get('period', 'M'))
        df['cohort_group'] = df[cohort_column]
        
        # Create cohort table
        cohort_data = df.groupby(['cohort_group', 'cohort_period'])[value_column].agg(['count', 'sum']).reset_index()
        
        # Calculate period number for each cohort
        cohort_data['period_number'] = cohort_data.apply(
            lambda row: (row['cohort_period'] - row['cohort_group']).n + 1, axis=1
        )
        
        # Create pivot table
        cohort_table = cohort_data.pivot_table(
            index='cohort_group',
            columns='period_number',
            values='count',
            aggfunc='sum'
        )
        
        # Calculate cohort sizes
        cohort_sizes = cohort_table.iloc[:, 0]
        
        # Calculate retention rates
        retention_table = cohort_table.divide(cohort_sizes, axis=0)
        
        results = {
            "cohort_table": cohort_table.fillna("").to_dict(),
            "retention_table": (retention_table * 100).round(2).fillna("").to_dict(),
            "cohort_sizes": cohort_sizes.to_dict(),
            "analysis_type": f"Cohort analysis by {cohort_column}"
        }
        
        return {
            "result": results,
            "rationale": f"Performed cohort analysis using {cohort_column} as cohort identifier",
            "confidence": 0.85
        }
    
    def _create_histogram_data(self, series, bins=30):
        """Create histogram data for visualization."""
        hist, bin_edges = np.histogram(series, bins=bins)
        return {
            "counts": hist.tolist(),
            "bin_edges": bin_edges.tolist(),
            "bin_centers": ((bin_edges[:-1] + bin_edges[1:]) / 2).tolist()
        }
    
    def _interpret_correlation(self, r):
        """Interpret correlation strength."""
        abs_r = abs(r)
        if abs_r < 0.1:
            return "Negligible"
        elif abs_r < 0.3:
            return "Weak"
        elif abs_r < 0.5:
            return "Moderate"
        elif abs_r < 0.7:
            return "Strong"
        else:
            return "Very Strong"

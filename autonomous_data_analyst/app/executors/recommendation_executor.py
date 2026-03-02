import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset
from app.llm.llm_planner import LLMPlanner
from config.settings import settings


class RecommendationExecutor(BaseExecutor):
    """Executor for generating insights and recommendations."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute insight generation and recommendations."""
        
        operation = spec.get("operation", "generate_insights")
        
        if operation == "generate_insights":
            return await self._generate_insights(dataset, spec, previous_results)
        elif operation == "data_quality_recommendations":
            return await self._data_quality_recommendations(dataset, spec, previous_results)
        elif operation == "analysis_recommendations":
            return await self._analysis_recommendations(dataset, spec, previous_results)
        elif operation == "business_insights":
            return await self._business_insights(dataset, spec, previous_results)
        elif operation == "safety_review":
            return await self._safety_review(dataset, spec, previous_results)
        else:
            raise ValueError(f"Unknown recommendation operation: {operation}")
    
    async def _generate_insights(self, dataset: Dataset, spec: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general insights from analysis results."""
        df = self._get_dataset_dataframe(dataset)
        
        insights = []
        recommendations = []
        confidence_scores = []
        
        # Analyze previous results to generate insights
        for step_id, step_result in previous_results.items():
            if not step_result.get("success", False):
                continue
            
            result_data = step_result.get("result", {})
            step_type = step_result.get("step_type", "")
            
            if step_type == "profile":
                insights.extend(self._extract_profile_insights(result_data))
            elif step_type == "analysis":
                insights.extend(self._extract_analysis_insights(result_data))
            elif step_type == "anomaly":
                insights.extend(self._extract_anomaly_insights(result_data))
            elif step_type == "clean":
                insights.extend(self._extract_cleaning_insights(result_data))
        
        # Generate data quality recommendations
        quality_recommendations = self._generate_quality_recommendations(df)
        recommendations.extend(quality_recommendations)
        
        # Generate analysis recommendations
        analysis_recommendations = self._generate_analysis_recommendations(df, previous_results)
        recommendations.extend(analysis_recommendations)
        
        # Use LLM to generate additional insights if available
        if not settings.MOCK_LLM_MODE:
            try:
                llm_insights = await self._generate_llm_insights(dataset, previous_results)
                insights.extend(llm_insights)
            except Exception as e:
                insights.append(f"LLM insight generation failed: {str(e)}")
        
        # Calculate overall confidence
        if confidence_scores:
            overall_confidence = np.mean(confidence_scores)
        else:
            overall_confidence = 0.7  # Default confidence
        
        result = {
            "insights": insights,
            "recommendations": recommendations,
            "confidence": overall_confidence,
            "insight_count": len(insights),
            "recommendation_count": len(recommendations),
            "summary": f"Generated {len(insights)} insights and {len(recommendations)} recommendations from the analysis"
        }
        
        return {
            "result": result,
            "rationale": f"Generated insights and recommendations based on {len(previous_results)} analysis steps",
            "confidence": overall_confidence
        }
    
    async def _data_quality_recommendations(self, dataset: Dataset, spec: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data quality specific recommendations."""
        df = self._get_dataset_dataframe(dataset)
        
        recommendations = []
        insights = []
        
        # Missing data recommendations
        missing_pct = df.isnull().sum() / len(df) * 100
        high_missing_cols = missing_pct[missing_pct > 20].index.tolist()
        
        if high_missing_cols:
            recommendations.append({
                "category": "Data Quality",
                "priority": "High",
                "recommendation": f"Address missing values in columns: {high_missing_cols}",
                "details": f"These columns have >20% missing values which may impact analysis quality",
                "action": "Consider imputation strategies or column removal"
            })
            insights.append(f"High missing data detected in {len(high_missing_cols)} columns")
        
        # Duplicate data recommendations
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            recommendations.append({
                "category": "Data Quality",
                "priority": "Medium",
                "recommendation": f"Remove {duplicate_count} duplicate rows",
                "details": "Duplicate rows can bias statistical analysis",
                "action": "Use deduplication before analysis"
            })
            insights.append(f"Found {duplicate_count} duplicate rows in dataset")
        
        # Data type recommendations
        type_issues = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if could be numeric
                try:
                    pd.to_numeric(df[col])
                    type_issues.append(col)
                except:
                    pass
        
        if type_issues:
            recommendations.append({
                "category": "Data Quality",
                "priority": "Medium",
                "recommendation": f"Convert columns to appropriate data types: {type_issues}",
                "details": "Some numeric columns may be stored as text",
                "action": "Review and convert data types for better analysis"
            })
            insights.append(f"Potential data type issues in {len(type_issues)} columns")
        
        result = {
            "insights": insights,
            "recommendations": recommendations,
            "category": "Data Quality",
            "summary": f"Generated {len(recommendations)} data quality recommendations"
        }
        
        return {
            "result": result,
            "rationale": "Analyzed data quality issues and generated specific recommendations",
            "confidence": 0.9
        }
    
    async def _analysis_recommendations(self, dataset: Dataset, spec: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis-specific recommendations."""
        df = self._get_dataset_dataframe(dataset)
        
        recommendations = []
        insights = []
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        # Statistical analysis recommendations
        if len(numeric_cols) >= 2:
            recommendations.append({
                "category": "Analysis",
                "priority": "Medium",
                "recommendation": "Perform correlation analysis",
                "details": f"Dataset has {len(numeric_cols)} numeric columns suitable for correlation analysis",
                "action": "Use correlation analysis to identify relationships between variables"
            })
            insights.append("Multiple numeric columns available for correlation analysis")
        
        # Visualization recommendations
        if len(numeric_cols) > 0:
            recommendations.append({
                "category": "Visualization",
                "priority": "Low",
                "recommendation": "Create distribution plots",
                "details": f"Visualize distributions of {len(numeric_cols)} numeric columns",
                "action": "Use histograms and box plots to understand data distributions"
            })
        
        if len(categorical_cols) > 0:
            low_cardinality_cols = [col for col in categorical_cols if df[col].nunique() <= 20]
            if low_cardinality_cols:
                recommendations.append({
                    "category": "Visualization",
                    "priority": "Low",
                    "recommendation": "Create categorical visualizations",
                    "details": f"Create bar charts for {len(low_cardinality_cols)} categorical columns",
                    "action": "Use bar charts to show categorical distributions"
                })
        
        # Machine learning recommendations
        if len(df) > 1000 and len(numeric_cols) >= 3:
            recommendations.append({
                "category": "Advanced Analysis",
                "priority": "Low",
                "recommendation": "Consider machine learning analysis",
                "details": f"Dataset size ({len(df)} rows) and features ({len(numeric_cols)} numeric) suitable for ML",
                "action": "Explore clustering, classification, or regression models"
            })
        
        result = {
            "insights": insights,
            "recommendations": recommendations,
            "category": "Analysis",
            "summary": f"Generated {len(recommendations)} analysis recommendations"
        }
        
        return {
            "result": result,
            "rationale": "Analyzed dataset characteristics and suggested appropriate analyses",
            "confidence": 0.8
        }
    
    async def _business_insights(self, dataset: Dataset, spec: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business-focused insights."""
        df = self._get_dataset_dataframe(dataset)
        
        insights = []
        recommendations = []
        
        # Data completeness insights
        completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        if completeness > 95:
            insights.append(f"Dataset has excellent data completeness ({completeness:.1f}%)")
        elif completeness > 80:
            insights.append(f"Dataset has good data completeness ({completeness:.1f}%)")
            recommendations.append({
                "category": "Business",
                "priority": "Medium",
                "recommendation": "Improve data completeness",
                "details": f"Current completeness is {completeness:.1f}%, aim for >95%",
                "action": "Implement data validation and collection processes"
            })
        else:
            insights.append(f"Dataset has poor data completeness ({completeness:.1f}%)")
            recommendations.append({
                "category": "Business",
                "priority": "High",
                "recommendation": "Address data quality issues urgently",
                "details": f"Low completeness ({completeness:.1f}%) may impact business decisions",
                "action": "Prioritize data quality improvement initiatives"
            })
        
        # Data size insights
        if len(df) > 100000:
            insights.append(f"Large dataset ({len(df):,} rows) suitable for comprehensive analysis")
            recommendations.append({
                "category": "Business",
                "priority": "Low",
                "recommendation": "Consider advanced analytics",
                "details": "Large dataset enables sophisticated analysis techniques",
                "action": "Explore machine learning and predictive modeling"
            })
        elif len(df) > 10000:
            insights.append(f"Medium-sized dataset ({len(df):,} rows) suitable for most analyses")
        else:
            insights.append(f"Small dataset ({len(df):,} rows) - consider statistical limitations")
            recommendations.append({
                "category": "Business",
                "priority": "Medium",
                "recommendation": "Collect more data if possible",
                "details": "Small dataset may limit statistical power",
                "action": "Expand data collection efforts"
            })
        
        result = {
            "insights": insights,
            "recommendations": recommendations,
            "category": "Business",
            "summary": f"Generated {len(insights)} business insights and {len(recommendations)} recommendations"
        }
        
        return {
            "result": result,
            "rationale": "Generated business-focused insights from dataset characteristics",
            "confidence": 0.75
        }
    
    async def _safety_review(self, dataset: Dataset, spec: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safety review of analysis plan."""
        issues = spec.get("issues", [])
        suggestions = spec.get("suggestions", [])
        
        insights = []
        recommendations = []
        
        if issues:
            insights.append(f"Safety review identified {len(issues)} potential issues")
            for issue in issues:
                recommendations.append({
                    "category": "Safety",
                    "priority": "High",
                    "recommendation": f"Address issue: {issue}",
                    "details": "Safety concern identified during plan review",
                    "action": "Review and modify analysis approach"
                })
        
        if suggestions:
            insights.append(f"Safety review provided {len(suggestions)} suggestions")
            for suggestion in suggestions:
                recommendations.append({
                    "category": "Safety",
                    "priority": "Medium",
                    "recommendation": f"Consider suggestion: {suggestion}",
                    "details": "Recommendation for improved analysis safety",
                    "action": "Implement suggested improvements"
                })
        
        if not issues and not suggestions:
            insights.append("Safety review completed with no concerns identified")
        
        result = {
            "insights": insights,
            "recommendations": recommendations,
            "category": "Safety",
            "summary": f"Safety review completed with {len(issues)} issues and {len(suggestions)} suggestions"
        }
        
        return {
            "result": result,
            "rationale": "Performed safety review of analysis plan and execution",
            "confidence": 0.9
        }
    
    def _extract_profile_insights(self, result_data: Dict[str, Any]) -> List[str]:
        """Extract insights from profiling results."""
        insights = []
        
        if "basic_stats" in result_data:
            stats = result_data["basic_stats"]
            insights.append(f"Dataset contains {stats.get('row_count', 0)} rows and {stats.get('column_count', 0)} columns")
            
            numeric_count = len(stats.get('numeric_columns', []))
            categorical_count = len(stats.get('categorical_columns', []))
            insights.append(f"Found {numeric_count} numeric and {categorical_count} categorical columns")
        
        if "quality_metrics" in result_data:
            quality = result_data["quality_metrics"]
            if quality.get("duplicate_rows", 0) > 0:
                insights.append(f"Found {quality['duplicate_rows']} duplicate rows")
            
            if quality.get("complete_percentage", 100) < 100:
                insights.append(f"Data completeness: {quality['complete_percentage']:.1f}%")
        
        return insights
    
    def _extract_analysis_insights(self, result_data: Dict[str, Any]) -> List[str]:
        """Extract insights from analysis results."""
        insights = []
        
        if "significant_correlations" in result_data:
            correlations = result_data["significant_correlations"]
            if correlations:
                insights.append(f"Found {len(correlations)} significant correlations")
        
        if "overall_statistics" in result_data:
            stats = result_data["overall_statistics"]
            if "missing_percentage" in stats:
                missing_pct = stats["missing_percentage"]
                if missing_pct > 10:
                    insights.append(f"High missing data: {missing_pct:.1f}%")
        
        return insights
    
    def _extract_anomaly_insights(self, result_data: Dict[str, Any]) -> List[str]:
        """Extract insights from anomaly detection results."""
        insights = []
        
        if "anomaly_count" in result_data:
            anomaly_count = result_data["anomaly_count"]
            anomaly_pct = result_data.get("anomaly_percentage", 0)
            insights.append(f"Detected {anomaly_count} anomalies ({anomaly_pct:.2f}% of data)")
        
        return insights
    
    def _extract_cleaning_insights(self, result_data: Dict[str, Any]) -> List[str]:
        """Extract insights from cleaning results."""
        insights = []
        
        if "rows_removed" in result_data:
            rows_removed = result_data["rows_removed"]
            if rows_removed > 0:
                insights.append(f"Removed {rows_removed} rows during cleaning")
        
        if "changes_made" in result_data:
            changes = result_data["changes_made"]
            insights.append(f"Applied {len(changes)} cleaning operations")
        
        return insights
    
    def _generate_quality_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate data quality recommendations."""
        recommendations = []
        
        # Missing data recommendations
        missing_pct = df.isnull().sum() / len(df) * 100
        for col, pct in missing_pct.items():
            if pct > 50:
                recommendations.append({
                    "category": "Data Quality",
                    "priority": "High",
                    "recommendation": f"Review column '{col}' with {pct:.1f}% missing values",
                    "action": "Consider imputation or removal"
                })
        
        return recommendations
    
    def _generate_analysis_recommendations(self, df: pd.DataFrame, previous_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate analysis recommendations."""
        recommendations = []
        
        numeric_cols = self._get_numeric_columns(df)
        
        if len(numeric_cols) >= 2:
            recommendations.append({
                "category": "Analysis",
                "priority": "Medium",
                "recommendation": "Perform correlation analysis",
                "action": "Explore relationships between numeric variables"
            })
        
        return recommendations
    
    async def _generate_llm_insights(self, dataset: Dataset, previous_results: Dict[str, Any]) -> List[str]:
        """Generate insights using LLM."""
        try:
            planner = LLMPlanner()
            
            # Create a summary of results for LLM
            results_summary = {}
            for step_id, step_result in previous_results.items():
                if step_result.get("success", False):
                    results_summary[step_id] = {
                        "type": step_result.get("step_type"),
                        "summary": str(step_result.get("result", {}))[:500]  # Truncate for context
                    }
            
            prompt = f"""
            Based on the following analysis results for dataset '{dataset.name}', generate 3-5 key insights:
            
            Results Summary:
            {json.dumps(results_summary, indent=2)}
            
            Provide concise, actionable insights that would be valuable for a data analyst.
            """
            
            llm_response = await planner.llm.generate_response(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse insights from response
            insights = []
            for line in llm_response.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    insights.append(line)
                elif line.startswith('-'):
                    insights.append(line[1:].strip())
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            return [f"LLM insight generation encountered an error: {str(e)}"]

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from app.executors.base_executor import BaseExecutor
from app.models.database import Dataset


class VisualizerExecutor(BaseExecutor):
    """Executor for data visualization steps."""
    
    async def execute(
        self,
        dataset: Dataset,
        spec: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute visualization generation."""
        
        chart_type = spec.get("chart_type", "auto")
        
        if chart_type == "auto":
            return await self._auto_visualize(dataset, spec)
        elif chart_type == "histogram":
            return await self._create_histogram(dataset, spec)
        elif chart_type == "scatter":
            return await self._create_scatter_plot(dataset, spec)
        elif chart_type == "line":
            return await self._create_line_plot(dataset, spec)
        elif chart_type == "bar":
            return await self._create_bar_chart(dataset, spec)
        elif chart_type == "box":
            return await self._create_box_plot(dataset, spec)
        elif chart_type == "heatmap":
            return await self._create_heatmap(dataset, spec)
        elif chart_type == "pie":
            return await self._create_pie_chart(dataset, spec)
        elif chart_type == "violin":
            return await self._create_violin_plot(dataset, spec)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    async def _auto_visualize(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically determine best visualizations."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns", [])
        if columns:
            df = df[columns]
        
        charts = []
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        # Generate histograms for numeric columns
        for col in numeric_cols[:5]:  # Limit to first 5 columns
            chart_spec = await self._create_histogram(dataset, {"column": col, "chart_type": "histogram"})
            charts.append(chart_spec["result"]["chart"])
        
        # Generate bar charts for categorical columns with reasonable cardinality
        for col in categorical_cols[:3]:  # Limit to first 3 columns
            if df[col].nunique() <= 20:  # Only if reasonable cardinality
                chart_spec = await self._create_bar_chart(dataset, {"column": col, "chart_type": "bar"})
                charts.append(chart_spec["result"]["chart"])
        
        # Generate scatter plots for numeric column pairs
        if len(numeric_cols) >= 2:
            chart_spec = await self._create_scatter_plot(
                dataset, 
                {"x_column": numeric_cols[0], "y_column": numeric_cols[1], "chart_type": "scatter"}
            )
            charts.append(chart_spec["result"]["chart"])
        
        # Generate correlation heatmap if enough numeric columns
        if len(numeric_cols) >= 3:
            chart_spec = await self._create_heatmap(dataset, {"columns": numeric_cols, "chart_type": "heatmap"})
            charts.append(chart_spec["result"]["chart"])
        
        result = {
            "charts": charts,
            "chart_count": len(charts),
            "visualization_summary": f"Generated {len(charts)} charts: {len([c for c in charts if c['type'] == 'histogram'])} histograms, {len([c for c in charts if c['type'] == 'bar'])} bar charts, {len([c for c in charts if c['type'] == 'scatter'])} scatter plots"
        }
        
        return {
            "result": result,
            "rationale": f"Auto-generated {len(charts)} appropriate visualizations based on data types",
            "confidence": 0.85
        }
    
    async def _create_histogram(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create histogram chart."""
        df = self._get_dataset_dataframe(dataset)
        
        column = spec.get("column")
        if not column:
            numeric_cols = self._get_numeric_columns(df)
            if not numeric_cols:
                raise ValueError("No numeric columns found for histogram")
            column = numeric_cols[0]
        
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in dataset")
        
        series = df[column].dropna()
        if len(series) == 0:
            raise ValueError(f"No data available for column {column}")
        
        # Calculate histogram data
        bins = spec.get("bins", 30)
        hist, bin_edges = np.histogram(series, bins=bins)
        
        # Create Vega-Lite specification
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {
                "values": [
                    {
                        "bin_start": float(bin_edges[i]),
                        "bin_end": float(bin_edges[i + 1]),
                        "count": int(hist[i]),
                        "density": float(hist[i] / len(series))
                    }
                    for i in range(len(hist))
                ]
            },
            "mark": "bar",
            "encoding": {
                "x": {
                    "field": "bin_start",
                    "type": "quantitative",
                    "title": column,
                    "bin": {"binned": True, "step": (bin_edges[1] - bin_edges[0])}
                },
                "x2": {"field": "bin_end"},
                "y": {
                    "field": "count",
                    "type": "quantitative",
                    "title": "Count"
                },
                "tooltip": [
                    {"field": "bin_start", "title": "Range Start"},
                    {"field": "bin_end", "title": "Range End"},
                    {"field": "count", "title": "Count"},
                    {"field": "density", "title": "Density", "format": ".3f"}
                ]
            },
            "title": f"Distribution of {column}",
            "width": 600,
            "height": 400
        }
        
        chart = {
            "type": "histogram",
            "title": f"Distribution of {column}",
            "spec": chart_spec,
            "description": f"Histogram showing the distribution of {column} with {bins} bins",
            "metadata": {
                "column": column,
                "bins": bins,
                "sample_size": len(series),
                "mean": float(series.mean()),
                "std": float(series.std())
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created histogram for {column} with {len(series)} data points",
            "confidence": 0.95
        }
    
    async def _create_scatter_plot(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create scatter plot."""
        df = self._get_dataset_dataframe(dataset)
        
        x_column = spec.get("x_column")
        y_column = spec.get("y_column")
        color_column = spec.get("color_column")
        
        if not x_column or not y_column:
            numeric_cols = self._get_numeric_columns(df)
            if len(numeric_cols) < 2:
                raise ValueError("Need at least 2 numeric columns for scatter plot")
            x_column = numeric_cols[0]
            y_column = numeric_cols[1]
        
        # Prepare data
        plot_data = df[[x_column, y_column]].dropna()
        if color_column and color_column in df.columns:
            plot_data[color_column] = df[color_column]
        
        # Create Vega-Lite specification
        encoding = {
            "x": {
                "field": x_column,
                "type": "quantitative",
                "title": x_column,
                "scale": {"zero": False}
            },
            "y": {
                "field": y_column,
                "type": "quantitative",
                "title": y_column,
                "scale": {"zero": False}
            },
            "tooltip": [
                {"field": x_column, "title": x_column, "format": ".2f"},
                {"field": y_column, "title": y_column, "format": ".2f"}
            ]
        }
        
        if color_column and color_column in plot_data.columns:
            encoding["color"] = {
                "field": color_column,
                "type": "nominal" if plot_data[color_column].dtype == 'object' else "quantitative"
            }
            encoding["tooltip"].append({"field": color_column, "title": color_column})
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.fillna("").to_dict('records')},
            "mark": {"type": "circle", "opacity": 0.6},
            "encoding": encoding,
            "title": f"{y_column} vs {x_column}",
            "width": 600,
            "height": 400
        }
        
        # Calculate correlation
        correlation = plot_data[x_column].corr(plot_data[y_column])
        
        chart = {
            "type": "scatter",
            "title": f"{y_column} vs {x_column}",
            "spec": chart_spec,
            "description": f"Scatter plot showing relationship between {x_column} and {y_column}",
            "metadata": {
                "x_column": x_column,
                "y_column": y_column,
                "color_column": color_column,
                "sample_size": len(plot_data),
                "correlation": float(correlation) if not pd.isna(correlation) else None
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created scatter plot with {len(plot_data)} points",
            "confidence": 0.9
        }
    
    async def _create_line_plot(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create line plot."""
        df = self._get_dataset_dataframe(dataset)
        
        x_column = spec.get("x_column")
        y_column = spec.get("y_column")
        group_column = spec.get("group_column")
        
        if not x_column or not y_column:
            raise ValueError("Both x_column and y_column are required for line plot")
        
        # Prepare data
        plot_data = df[[x_column, y_column]].dropna()
        if group_column and group_column in df.columns:
            plot_data[group_column] = df[group_column]
        
        # Sort by x column
        plot_data = plot_data.sort_values(x_column)
        
        # Create Vega-Lite specification
        encoding = {
            "x": {
                "field": x_column,
                "type": "temporal" if pd.api.types.is_datetime64_any_dtype(plot_data[x_column]) else "quantitative",
                "title": x_column
            },
            "y": {
                "field": y_column,
                "type": "quantitative",
                "title": y_column
            },
            "tooltip": [
                {"field": x_column, "title": x_column},
                {"field": y_column, "title": y_column, "format": ".2f"}
            ]
        }
        
        if group_column and group_column in plot_data.columns:
            encoding["color"] = {"field": group_column, "type": "nominal"}
            encoding["tooltip"].append({"field": group_column, "title": group_column})
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.fillna("").to_dict('records')},
            "mark": "line",
            "encoding": encoding,
            "title": f"{y_column} over {x_column}",
            "width": 600,
            "height": 400
        }
        
        chart = {
            "type": "line",
            "title": f"{y_column} over {x_column}",
            "spec": chart_spec,
            "description": f"Line plot showing {y_column} trends over {x_column}",
            "metadata": {
                "x_column": x_column,
                "y_column": y_column,
                "group_column": group_column,
                "sample_size": len(plot_data)
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created line plot with {len(plot_data)} data points",
            "confidence": 0.9
        }
    
    async def _create_bar_chart(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create bar chart."""
        df = self._get_dataset_dataframe(dataset)
        
        column = spec.get("column")
        value_column = spec.get("value_column")
        top_n = spec.get("top_n", 10)
        
        if not column:
            categorical_cols = self._get_categorical_columns(df)
            if not categorical_cols:
                raise ValueError("No categorical columns found for bar chart")
            column = categorical_cols[0]
        
        if value_column:
            # Aggregate by column
            plot_data = df.groupby(column)[value_column].sum().reset_index()
            plot_data = plot_data.sort_values(value_column, ascending=False).head(top_n)
            y_field = value_column
            y_type = "quantitative"
        else:
            # Count occurrences
            plot_data = df[column].value_counts().head(top_n).reset_index()
            plot_data.columns = [column, "count"]
            y_field = "count"
            y_type = "quantitative"
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.fillna("").to_dict('records')},
            "mark": "bar",
            "encoding": {
                "x": {
                    "field": column,
                    "type": "nominal",
                    "title": column,
                    "sort": "-y"
                },
                "y": {
                    "field": y_field,
                    "type": y_type,
                    "title": y_field
                },
                "tooltip": [
                    {"field": column, "title": column},
                    {"field": y_field, "title": y_field, "format": ".2f"}
                ]
            },
            "title": f"{y_field} by {column}",
            "width": 600,
            "height": 400
        }
        
        chart = {
            "type": "bar",
            "title": f"{y_field} by {column}",
            "spec": chart_spec,
            "description": f"Bar chart showing {y_field} for top {len(plot_data)} {column} values",
            "metadata": {
                "column": column,
                "value_column": value_column,
                "top_n": top_n,
                "sample_size": len(plot_data)
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created bar chart for {column} with {len(plot_data)} categories",
            "confidence": 0.9
        }
    
    async def _create_box_plot(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create box plot."""
        df = self._get_dataset_dataframe(dataset)
        
        value_column = spec.get("value_column")
        group_column = spec.get("group_column")
        
        if not value_column:
            numeric_cols = self._get_numeric_columns(df)
            if not numeric_cols:
                raise ValueError("No numeric columns found for box plot")
            value_column = numeric_cols[0]
        
        # Prepare data
        plot_data = df[[value_column]].dropna()
        if group_column and group_column in df.columns:
            plot_data[group_column] = df[group_column]
        
        # Create Vega-Lite specification
        encoding = {
            "y": {
                "field": value_column,
                "type": "quantitative",
                "title": value_column
            }
        }
        
        if group_column and group_column in plot_data.columns:
            encoding["x"] = {
                "field": group_column,
                "type": "nominal",
                "title": group_column
            }
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.fillna("").to_dict('records')},
            "mark": "boxplot",
            "encoding": encoding,
            "title": f"Box Plot of {value_column}" + (f" by {group_column}" if group_column else ""),
            "width": 600,
            "height": 400
        }
        
        chart = {
            "type": "box",
            "title": f"Box Plot of {value_column}" + (f" by {group_column}" if group_column else ""),
            "spec": chart_spec,
            "description": f"Box plot showing distribution of {value_column}" + (f" across {group_column}" if group_column else ""),
            "metadata": {
                "value_column": value_column,
                "group_column": group_column,
                "sample_size": len(plot_data)
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created box plot for {value_column} with {len(plot_data)} data points",
            "confidence": 0.9
        }
    
    async def _create_heatmap(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create correlation heatmap."""
        df = self._get_dataset_dataframe(dataset)
        
        columns = spec.get("columns")
        if not columns:
            columns = self._get_numeric_columns(df)
        
        if len(columns) < 2:
            raise ValueError("Need at least 2 numeric columns for heatmap")
        
        # Calculate correlation matrix
        corr_matrix = df[columns].corr()
        
        # Convert to long format for Vega-Lite
        corr_data = []
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                corr_data.append({
                    "column1": col1,
                    "column2": col2,
                    "correlation": float(corr_matrix.iloc[i, j]) if not pd.isna(corr_matrix.iloc[i, j]) else None
                })
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": corr_data},
            "mark": "rect",
            "encoding": {
                "x": {"field": "column1", "type": "nominal", "title": ""},
                "y": {"field": "column2", "type": "nominal", "title": ""},
                "color": {
                    "field": "correlation",
                    "type": "quantitative",
                    "title": "Correlation",
                    "scale": {"domain": [-1, 1], "scheme": "redblue"}
                },
                "tooltip": [
                    {"field": "column1", "title": "Variable 1"},
                    {"field": "column2", "title": "Variable 2"},
                    {"field": "correlation", "title": "Correlation", "format": ".3f"}
                ]
            },
            "title": "Correlation Heatmap",
            "width": 500,
            "height": 500,
            "config": {
                "view": {"stroke": None},
                "axis": {"labelAngle": 0}
            }
        }
        
        chart = {
            "type": "heatmap",
            "title": "Correlation Heatmap",
            "spec": chart_spec,
            "description": f"Correlation heatmap for {len(columns)} variables",
            "metadata": {
                "columns": columns,
                "correlation_matrix": corr_matrix.fillna("").to_dict()
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created correlation heatmap for {len(columns)} variables",
            "confidence": 0.9
        }
    
    async def _create_pie_chart(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create pie chart."""
        df = self._get_dataset_dataframe(dataset)
        
        column = spec.get("column")
        top_n = spec.get("top_n", 8)
        
        if not column:
            categorical_cols = self._get_categorical_columns(df)
            if not categorical_cols:
                raise ValueError("No categorical columns found for pie chart")
            column = categorical_cols[0]
        
        # Get value counts
        plot_data = df[column].value_counts().head(top_n).reset_index()
        plot_data.columns = [column, "count"]
        
        # Add "Others" category if needed
        if df[column].nunique() > top_n:
            others_count = df[column].value_counts().iloc[top_n:].sum()
            plot_data = pd.concat([
                plot_data,
                pd.DataFrame([{column: "Others", "count": others_count}])
            ], ignore_index=True)
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.to_dict('records')},
            "mark": {"type": "arc", "innerRadius": 50},
            "encoding": {
                "theta": {
                    "field": "count",
                    "type": "quantitative"
                },
                "color": {
                    "field": column,
                    "type": "nominal",
                    "title": column
                },
                "tooltip": [
                    {"field": column, "title": column},
                    {"field": "count", "title": "Count"}
                ]
            },
            "title": f"Distribution of {column}",
            "width": 400,
            "height": 400,
            "view": {"stroke": None}
        }
        
        chart = {
            "type": "pie",
            "title": f"Distribution of {column}",
            "spec": chart_spec,
            "description": f"Pie chart showing distribution of {column}",
            "metadata": {
                "column": column,
                "top_n": top_n,
                "total_categories": df[column].nunique()
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created pie chart for {column} with {len(plot_data)} categories",
            "confidence": 0.85
        }
    
    async def _create_violin_plot(self, dataset: Dataset, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create violin plot."""
        df = self._get_dataset_dataframe(dataset)
        
        value_column = spec.get("value_column")
        group_column = spec.get("group_column")
        
        if not value_column:
            numeric_cols = self._get_numeric_columns(df)
            if not numeric_cols:
                raise ValueError("No numeric columns found for violin plot")
            value_column = numeric_cols[0]
        
        # Prepare data
        plot_data = df[[value_column]].dropna()
        if group_column and group_column in df.columns:
            plot_data[group_column] = df[group_column]
        
        # Create Vega-Lite specification
        encoding = {
            "y": {
                "field": value_column,
                "type": "quantitative",
                "title": value_column
            }
        }
        
        if group_column and group_column in plot_data.columns:
            encoding["x"] = {
                "field": group_column,
                "type": "nominal",
                "title": group_column
            }
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": plot_data.fillna("").to_dict('records')},
            "mark": {"type": "area", "orient": "vertical", "opacity": 0.6},
            "encoding": encoding,
            "title": f"Violin Plot of {value_column}" + (f" by {group_column}" if group_column else ""),
            "width": 600,
            "height": 400,
            "transform": [
                {
                    "density": value_column,
                    "groupby": [group_column] if group_column else [],
                    "extent": {"signal": "domain('y')"},
                    "counts": True,
                    "as": ["density", "counts"]
                }
            ]
        }
        
        chart = {
            "type": "violin",
            "title": f"Violin Plot of {value_column}" + (f" by {group_column}" if group_column else ""),
            "spec": chart_spec,
            "description": f"Violin plot showing distribution of {value_column}" + (f" across {group_column}" if group_column else ""),
            "metadata": {
                "value_column": value_column,
                "group_column": group_column,
                "sample_size": len(plot_data)
            }
        }
        
        return {
            "result": {"chart": chart},
            "rationale": f"Created violin plot for {value_column} with {len(plot_data)} data points",
            "confidence": 0.9
        }

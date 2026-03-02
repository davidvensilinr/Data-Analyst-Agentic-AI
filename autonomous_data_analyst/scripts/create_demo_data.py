#!/usr/bin/env python3
"""
Script to create demo datasets for testing and demonstration.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import json


def create_employee_dataset():
    """Create a realistic employee dataset with various data quality issues."""
    np.random.seed(42)
    
    n_records = 1000
    
    # Generate realistic employee data
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    cities = ['New York', 'San Francisco', 'Chicago', 'Boston', 'Austin', 'Seattle']
    
    data = {
        'employee_id': range(1, n_records + 1),
        'first_name': np.random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa'], n_records),
        'last_name': np.random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'], n_records),
        'age': np.random.normal(35, 10, n_records),
        'department': np.random.choice(departments, n_records),
        'salary': np.random.normal(75000, 25000, n_records),
        'hire_date': [datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1500)) for _ in range(n_records)],
        'city': np.random.choice(cities, n_records),
        'performance_score': np.random.uniform(1, 5, n_records),
        'years_experience': np.random.exponential(5, n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce data quality issues
    # Missing values
    missing_indices = np.random.choice(df.index, size=int(0.05 * n_records), replace=False)
    df.loc[missing_indices, 'salary'] = np.nan
    
    missing_indices = np.random.choice(df.index, size=int(0.03 * n_records), replace=False)
    df.loc[missing_indices, 'performance_score'] = np.nan
    
    # Outliers
    outlier_indices = np.random.choice(df.index, size=int(0.02 * n_records), replace=False)
    df.loc[outlier_indices, 'age'] = df.loc[outlier_indices, 'age'] * 3
    
    outlier_indices = np.random.choice(df.index, size=int(0.01 * n_records), replace=False)
    df.loc[outlier_indices, 'salary'] = df.loc[outlier_indices, 'salary'] * 10
    
    # Inconsistent formatting
    df.loc[df.sample(frac=0.1).index, 'first_name'] = df.loc[df.sample(frac=0.1).index, 'first_name'].str.lower()
    df.loc[df.sample(frac=0.05).index, 'department'] = df.loc[df.sample(frac=0.05).index, 'department'].str.upper()
    
    # Duplicates
    duplicate_rows = df.sample(n=int(0.02 * n_records))
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # Data type issues
    df.loc[df.sample(frac=0.03).index, 'employee_id'] = df.loc[df.sample(frac=0.03).index, 'employee_id'].astype(str)
    
    # Ensure reasonable ranges
    df['age'] = df['age'].clip(18, 80)
    df['salary'] = df['salary'].clip(25000, 500000)
    df['performance_score'] = df['performance_score'].clip(1, 5)
    
    return df


def create_sales_dataset():
    """Create a sales dataset with time series data."""
    np.random.seed(123)
    
    # Generate 2 years of daily sales data
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    n_records = len(date_range)
    
    # Base sales with trend and seasonality
    trend = np.linspace(1000, 1500, n_records)
    seasonal = 200 * np.sin(2 * np.pi * np.arange(n_records) / 365.25)
    noise = np.random.normal(0, 100, n_records)
    
    base_sales = trend + seasonal + noise
    
    # Add some anomalies
    anomaly_dates = np.random.choice(date_range, size=10, replace=False)
    for date in anomaly_dates:
        idx = date_range.get_loc(date)
        base_sales[idx] *= np.random.choice([0.1, 5.0])  # Either very low or very high
    
    data = {
        'date': date_range,
        'sales_amount': np.maximum(0, base_sales),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Sports', 'Books'], n_records),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'customer_count': np.random.poisson(50, n_records),
        'promotion_active': np.random.choice([True, False], n_records, p=[0.3, 0.7])
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values
    missing_indices = np.random.choice(df.index, size=int(0.02 * n_records), replace=False)
    df.loc[missing_indices, 'customer_count'] = np.nan
    
    return df


def create_web_analytics_dataset():
    """Create a web analytics dataset."""
    np.random.seed(456)
    
    n_records = 5000
    
    # Generate realistic web analytics data
    pages = ['/home', '/products', '/about', '/contact', '/blog', '/checkout', '/login']
    referrers = ['google', 'facebook', 'twitter', 'direct', 'email', 'linkedin']
    devices = ['desktop', 'mobile', 'tablet']
    
    data = {
        'timestamp': [datetime(2023, 1, 1) + timedelta(minutes=np.random.randint(0, 525600)) for _ in range(n_records)],
        'page_url': np.random.choice(pages, n_records, p=[0.3, 0.25, 0.1, 0.05, 0.15, 0.1, 0.05]),
        'referrer': np.random.choice(referrers, n_records, p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05]),
        'device_type': np.random.choice(devices, n_records, p=[0.6, 0.35, 0.05]),
        'session_duration': np.random.exponential(180, n_records),  # In seconds
        'page_views': np.random.geometric(0.3, n_records),
        'bounce_rate': np.random.beta(2, 5, n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Add some anomalies (very long sessions)
    anomaly_indices = np.random.choice(df.index, size=int(0.01 * n_records), replace=False)
    df.loc[anomaly_indices, 'session_duration'] = df.loc[anomaly_indices, 'session_duration'] * 20
    
    # Ensure reasonable values
    df['session_duration'] = df['session_duration'].clip(1, 7200)  # Max 2 hours
    df['page_views'] = df['page_views'].clip(1, 50)
    df['bounce_rate'] = df['bounce_rate'].clip(0, 1)
    
    return df


def create_financial_dataset():
    """Create a financial dataset with transactions."""
    np.random.seed(789)
    
    n_records = 2000
    
    # Generate transaction data
    transaction_types = ['purchase', 'refund', 'transfer', 'payment', 'fee']
    categories = ['groceries', 'entertainment', 'utilities', 'transport', 'healthcare', 'other']
    
    data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(1, n_records + 1)],
        'date': [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(n_records)],
        'amount': np.random.lognormal(3, 1.5, n_records),
        'transaction_type': np.random.choice(transaction_types, n_records, p=[0.6, 0.1, 0.15, 0.1, 0.05]),
        'category': np.random.choice(categories, n_records),
        'account_id': np.random.choice([f'ACC{i:04d}' for i in range(1, 101)], n_records),
        'merchant': np.random.choice(['Amazon', 'Walmart', 'Target', 'Starbucks', 'Gas Station', 'Restaurant'], n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Adjust amounts based on transaction type
    df.loc[df['transaction_type'] == 'refund', 'amount'] *= -1
    df.loc[df['transaction_type'] == 'fee', 'amount'] *= -0.5
    
    # Add some missing data
    missing_indices = np.random.choice(df.index, size=int(0.03 * n_records), replace=False)
    df.loc[missing_indices, 'category'] = np.nan
    
    # Add some outliers (very large transactions)
    outlier_indices = np.random.choice(df.index, size=int(0.005 * n_records), replace=False)
    df.loc[outlier_indices, 'amount'] *= 100
    
    return df


def save_datasets():
    """Save all demo datasets."""
    # Create data directory if it doesn't exist
    data_dir = "data/raw"
    os.makedirs(data_dir, exist_ok=True)
    
    # Create datasets
    datasets = {
        'employees': create_employee_dataset(),
        'sales': create_sales_dataset(),
        'web_analytics': create_web_analytics_dataset(),
        'financial': create_financial_dataset()
    }
    
    # Save datasets
    for name, df in datasets.items():
        csv_path = os.path.join(data_dir, f'{name}.csv')
        json_path = os.path.join(data_dir, f'{name}.json')
        
        # Save as CSV
        df.to_csv(csv_path, index=False)
        print(f"Created {csv_path} with {len(df)} records")
        
        # Save as JSON
        df.to_json(json_path, orient='records', date_format='iso')
        print(f"Created {json_path}")
    
    # Create dataset metadata
    metadata = {
        'datasets': {
            'employees': {
                'name': 'Employee Dataset',
                'description': 'Employee information with various data quality issues including missing values, outliers, and inconsistencies.',
                'rows': len(datasets['employees']),
                'columns': len(datasets['employees'].columns),
                'file_types': ['csv', 'json'],
                'use_cases': ['data cleaning', 'profiling', 'anomaly detection', 'statistical analysis']
            },
            'sales': {
                'name': 'Sales Dataset',
                'description': 'Time series sales data with seasonal patterns, trends, and anomalies.',
                'rows': len(datasets['sales']),
                'columns': len(datasets['sales'].columns),
                'file_types': ['csv', 'json'],
                'use_cases': ['time series analysis', 'forecasting', 'anomaly detection', 'trend analysis']
            },
            'web_analytics': {
                'name': 'Web Analytics Dataset',
                'description': 'Website traffic and user behavior data with session information.',
                'rows': len(datasets['web_analytics']),
                'columns': len(datasets['web_analytics'].columns),
                'file_types': ['csv', 'json'],
                'use_cases': ['user behavior analysis', 'funnel analysis', 'performance metrics']
            },
            'financial': {
                'name': 'Financial Transactions Dataset',
                'description': 'Financial transaction data with various transaction types and categories.',
                'rows': len(datasets['financial']),
                'columns': len(datasets['financial'].columns),
                'file_types': ['csv', 'json'],
                'use_cases': ['fraud detection', 'spending analysis', 'categorization']
            }
        }
    }
    
    metadata_path = os.path.join(data_dir, 'datasets_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nCreated metadata file: {metadata_path}")
    print(f"\nSummary:")
    for name, info in metadata['datasets'].items():
        print(f"  {name}: {info['rows']:,} rows, {info['columns']} columns")


if __name__ == "__main__":
    print("Creating demo datasets...")
    save_datasets()
    print("\nDemo datasets created successfully!")
    print("\nYou can now use these datasets to test the autonomous data analyst backend.")

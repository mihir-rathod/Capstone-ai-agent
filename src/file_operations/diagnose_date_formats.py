#!/usr/bin/env python3
"""
Diagnostic script to analyze date formats in parquet files.
This helps identify inconsistent date formats causing parsing issues.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import re


def detect_date_format(date_string):
    """Detect the format of a date string."""
    if pd.isna(date_string) or date_string == '' or date_string is None:
        return 'NULL/EMPTY'
    
    date_str = str(date_string).strip()
    
    # Common date format patterns
    patterns = {
        r'^\d{4}-\d{2}-\d{2}$': 'YYYY-MM-DD',
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$': 'YYYY-MM-DD HH:MM:SS',
        r'^\d{2}/\d{2}/\d{4}$': 'MM/DD/YYYY',
        r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$': 'MM/DD/YYYY HH:MM',
        r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$': 'MM/DD/YYYY HH:MM:SS',
        r'^\d{1,2}/\d{1,2}/\d{4}$': 'M/D/YYYY',
        r'^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}$': 'M/D/YYYY H:MM',
        r'^\d{4}/\d{2}/\d{2}$': 'YYYY/MM/DD',
        r'^0000-00-00$': 'INVALID (0000-00-00)',
    }
    
    for pattern, format_name in patterns.items():
        if re.match(pattern, date_str):
            return format_name
    
    return f'UNKNOWN: {date_str[:30]}'


def analyze_date_column(df, column_name):
    """Analyze date formats in a specific column."""
    print(f"\n{'='*80}")
    print(f"Analyzing column: {column_name}")
    print(f"{'='*80}")
    
    if column_name not in df.columns:
        print(f"❌ Column '{column_name}' not found in dataframe")
        return
    
    # Get the column
    col = df[column_name]
    
    # Basic statistics
    total_rows = len(col)
    null_count = col.isna().sum()
    non_null_count = total_rows - null_count
    
    print(f"\n📊 Basic Statistics:")
    print(f"   Total rows:     {total_rows:,}")
    print(f"   NULL values:    {null_count:,} ({null_count/total_rows*100:.2f}%)")
    print(f"   Non-NULL values: {non_null_count:,} ({non_null_count/total_rows*100:.2f}%)")
    
    # Detect formats
    print(f"\n🔍 Detecting date formats...")
    formats = col.apply(detect_date_format)
    format_counts = Counter(formats)
    
    print(f"\n📋 Format Distribution:")
    for format_type, count in format_counts.most_common():
        percentage = (count / total_rows) * 100
        print(f"   {format_type:30s}: {count:8,} ({percentage:6.2f}%)")
    
    # Sample values for each format
    print(f"\n📝 Sample Values by Format:")
    for format_type in format_counts.keys():
        if format_type != 'NULL/EMPTY':
            samples = col[formats == format_type].head(3).tolist()
            print(f"   {format_type}:")
            for sample in samples:
                print(f"      - {sample}")
    
    # Data type information
    print(f"\n🔧 Data Type: {col.dtype}")
    
    return format_counts


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose_date_formats.py <parquet_file_path> [parquet_file_path2 ...]")
        print("\nExample:")
        print("  python diagnose_date_formats.py data/retail_data_file1.parquet")
        print("  python diagnose_date_formats.py data/*.parquet")
        sys.exit(1)
    
    parquet_files = sys.argv[1:]
    
    print("="*80)
    print("DATE FORMAT DIAGNOSTIC TOOL")
    print("="*80)
    print(f"\nAnalyzing {len(parquet_files)} file(s)...")
    
    for file_path in parquet_files:
        parquet_path = Path(file_path)
        
        if not parquet_path.exists():
            print(f"\n❌ File not found: {file_path}")
            continue
        
        print(f"\n\n{'#'*80}")
        print(f"# FILE: {parquet_path.name}")
        print(f"# PATH: {parquet_path}")
        print(f"# SIZE: {parquet_path.stat().st_size:,} bytes")
        print(f"{'#'*80}")
        
        try:
            # Read parquet file
            print(f"\n📂 Reading parquet file...")
            df = pd.read_parquet(parquet_path)
            print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
            
            # Show all columns
            print(f"\n📋 Available columns:")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i:2d}. {col}")
            
            # Analyze date columns
            date_columns = ['SALE_DATE_TIME', 'SALE_DATE']
            
            for col_name in date_columns:
                # Try case-insensitive match
                matching_cols = [c for c in df.columns if c.upper() == col_name.upper()]
                if matching_cols:
                    analyze_date_column(df, matching_cols[0])
                else:
                    print(f"\n⚠️  Column '{col_name}' not found (case-insensitive search)")
            
        except Exception as e:
            print(f"\n❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

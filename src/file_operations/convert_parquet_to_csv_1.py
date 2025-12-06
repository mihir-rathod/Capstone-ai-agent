import sys
import pandas as pd
import numpy as np
import traceback
from pathlib import Path

def validate_file_path(parquet_path):
    """Validate the parquet file exists and is readable."""
    print(f"Validating file path: {parquet_path}", flush=True)
    print(f"File exists: {parquet_path.exists()}", flush=True)
    if parquet_path.exists():
        print(f"File size: {parquet_path.stat().st_size} bytes", flush=True)
    
    if not parquet_path.exists():
        print(f"Error: File {parquet_path} not found.", flush=True)
        sys.exit(1)
    
    if parquet_path.stat().st_size == 0:
        print(f"Error: File {parquet_path} is empty.", flush=True)
        sys.exit(1)

def check_required_columns(df):
    """Check if all required columns are present."""
    required_columns = [
        'SALE_DATE_TIME', 'SALE_DATE', 'STORE_FORMAT', 'COMMAND_NAME',
        'SITE_ID', 'SITE_NAME', 'SLIP_NO', 'LINE', 'ITEM_ID', 'ITEM_DESC',
        'EXTENSION_AMOUNT', 'QTY', 'RETURN_IND', 'PRICE_STATUS'
    ]
    
    # Case-insensitive column matching
    df_columns_upper = [col.upper() for col in df.columns]
    missing_columns = [col for col in required_columns if col not in df_columns_upper]
    
    if missing_columns:
        print(f"Error: Missing required columns: {', '.join(missing_columns)}")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)
    
    return True

def check_null_values(df):
    """Check for null values in critical columns."""
    critical_columns = ['SALE_DATE', 'SALE_DATE_TIME']
    
    for col in df.columns:
        if col.upper() in [c.upper() for c in critical_columns]:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                percentage = (null_count / len(df)) * 100
                print(f"Warning: Column '{col}' has {null_count:,} null values ({percentage:.2f}%)", flush=True)

def clean_data(df):
    """Apply basic data cleaning."""
    original_rows = len(df)
    
    # Remove rows where critical dates are null
    for col in df.columns:
        if col.upper() in ['SALE_DATE', 'SALE_DATE_TIME']:
            df = df.dropna(subset=[col])
    
    # Convert column names to uppercase for consistency
    df.columns = [col.upper() for col in df.columns]
    
    # Trim whitespace from text columns
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        if col not in ['SALE_DATE_TIME', 'SALE_DATE']:
            df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
    
    # Handle ITEM_ID if it has decimal points (1947.0 -> 1947)
    if 'ITEM_ID' in df.columns and pd.api.types.is_float_dtype(df['ITEM_ID']):
        df['ITEM_ID'] = df['ITEM_ID'].astype('Int64')
    
    rows_removed = original_rows - len(df)
    if rows_removed > 0:
        print(f"Removed {rows_removed:,} rows during preprocessing", flush=True)
    
    return df

def normalize_date_formats(df):
    """Normalize date formats to standardized formats for MySQL loading."""
    print("\nNormalizing date formats...", flush=True)
    
    row_count = len(df)
    print(f"[DEBUG] Processing {row_count:,} rows for date normalization", flush=True)
    
    # Process SALE_DATE_TIME using vectorized operations (much faster)
    if 'SALE_DATE_TIME' in df.columns:
        print("  Processing SALE_DATE_TIME...", flush=True)
        original_nulls = df['SALE_DATE_TIME'].isna().sum()
        
        # Use pandas to_datetime with infer_datetime_format for speed
        print("  [DEBUG] Converting SALE_DATE_TIME with pd.to_datetime...", flush=True)
        df['SALE_DATE_TIME'] = pd.to_datetime(df['SALE_DATE_TIME'], errors='coerce', infer_datetime_format=True)
        
        # Convert to string format for CSV: YYYY-MM-DD HH:MM:SS
        print("  [DEBUG] Formatting SALE_DATE_TIME to string...", flush=True)
        df['SALE_DATE_TIME'] = df['SALE_DATE_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
        
        new_nulls = (df['SALE_DATE_TIME'] == '').sum()
        print(f"    Original NULLs: {original_nulls:,}, After parsing: {new_nulls:,}", flush=True)
        if new_nulls > original_nulls:
            print(f"    ⚠️  Warning: {new_nulls - original_nulls:,} values could not be parsed", flush=True)
    
    # Process SALE_DATE using vectorized operations
    if 'SALE_DATE' in df.columns:
        print("  Processing SALE_DATE...", flush=True)
        original_nulls = df['SALE_DATE'].isna().sum()
        
        # Use pandas to_datetime with infer_datetime_format for speed
        print("  [DEBUG] Converting SALE_DATE with pd.to_datetime...", flush=True)
        df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'], errors='coerce', infer_datetime_format=True)
        
        # Convert to string format for CSV: YYYY-MM-DD
        print("  [DEBUG] Formatting SALE_DATE to string...", flush=True)
        df['SALE_DATE'] = df['SALE_DATE'].dt.strftime('%Y-%m-%d').fillna('')
        
        new_nulls = (df['SALE_DATE'] == '').sum()
        print(f"    Original NULLs: {original_nulls:,}, After parsing: {new_nulls:,}", flush=True)
        if new_nulls > original_nulls:
            print(f"    ⚠️  Warning: {new_nulls - original_nulls:,} values could not be parsed", flush=True)
    
    print("  ✅ Date normalization complete", flush=True)
    return df

def main():
    print("[DEBUG] convert_parquet_to_csv_1.py started", flush=True)
    if len(sys.argv) != 2:
        print("Usage: python convert_parquet_to_csv.py <path_to_parquet_file>", flush=True)
        sys.exit(1)

    parquet_path = Path(sys.argv[1])
    
    # Validate file
    validate_file_path(parquet_path)
    
    # Read parquet file
    print(f"[DEBUG] Starting to read parquet file: {parquet_path.name}", flush=True)
    try:
        df = pd.read_parquet(parquet_path)
        print(f"[DEBUG] Loaded {len(df):,} rows, {len(df.columns)} columns", flush=True)
    except Exception as e:
        print(f"Error reading parquet file: {e}", flush=True)
        print("Full traceback:", flush=True)
        traceback.print_exc()
        sys.exit(1)
    
    # Run validation checks
    print("[DEBUG] Running validation checks...", flush=True)
    check_required_columns(df)
    check_null_values(df)
    
    # Clean data
    print("[DEBUG] Cleaning data...", flush=True)
    df = clean_data(df)
    
    # Normalize date formats
    print("[DEBUG] Starting date normalization...", flush=True)
    df = normalize_date_formats(df)
    
    # Convert to CSV
    csv_path = parquet_path.with_suffix(".csv")
    print(f"[DEBUG] Writing CSV file: {csv_path}", flush=True)
    
    try:
        df.to_csv(csv_path, index=False)
        print(f"[DEBUG] Conversion complete: {len(df):,} rows written", flush=True)
    except Exception as e:
        print(f"Error writing CSV: {e}", flush=True)
        print("Full traceback:", flush=True)
        traceback.print_exc()
        sys.exit(1)
    
    # Output the path (for the bash script to capture)
    print(csv_path, flush=True)

if __name__ == "__main__":
    main()

import sys
import pandas as pd
import numpy as np
import traceback
from pathlib import Path

def validate_file_path(parquet_path):
    """Validate the parquet file exists and is readable."""
    print(f"Validating file path: {parquet_path}")
    print(f"File exists: {parquet_path.exists()}")
    if parquet_path.exists():
        print(f"File size: {parquet_path.stat().st_size} bytes")
    
    if not parquet_path.exists():
        print(f"Error: File {parquet_path} not found.")
        sys.exit(1)
    
    if parquet_path.stat().st_size == 0:
        print(f"Error: File {parquet_path} is empty.")
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
                print(f"Warning: Column '{col}' has {null_count:,} null values ({percentage:.2f}%)")

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
        print(f"Removed {rows_removed:,} rows during preprocessing")
    
    return df

def normalize_date_formats(df):
    """Normalize date formats to standardized formats for MySQL loading."""
    print("\nNormalizing date formats...")
    
    def parse_flexible_datetime(value):
        """Parse datetime from multiple possible formats."""
        if pd.isna(value) or value == '' or value is None:
            return pd.NaT
        
        value_str = str(value).strip()
        
        # Try different datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',  # 2024-04-30 11:06:00
            '%m/%d/%Y %H:%M:%S',  # 04/30/2024 11:06:00
            '%m/%d/%Y %H:%M',     # 04/30/2024 11:06
            '%Y-%m-%d %H:%M',     # 2024-04-30 11:06
            '%Y/%m/%d %H:%M:%S',  # 2024/04/30 11:06:00
            '%Y/%m/%d %H:%M',     # 2024/04/30 11:06
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(value_str, format=fmt)
            except (ValueError, TypeError):
                continue
        
        # Try pandas auto-detection as fallback
        try:
            return pd.to_datetime(value_str)
        except:
            return pd.NaT
    
    def parse_flexible_date(value):
        """Parse date from multiple possible formats."""
        if pd.isna(value) or value == '' or value is None:
            return pd.NaT
        
        value_str = str(value).strip()
        
        # Skip invalid dates
        if value_str == '0000-00-00':
            return pd.NaT
        
        # Try different date formats
        formats = [
            '%Y-%m-%d',     # 2024-04-30
            '%m/%d/%Y',     # 04/30/2024
            '%Y/%m/%d',     # 2024/04/30
            '%d/%m/%Y',     # 30/04/2024
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(value_str, format=fmt).date()
            except (ValueError, TypeError):
                continue
        
        # Try pandas auto-detection as fallback
        try:
            return pd.to_datetime(value_str).date()
        except:
            return pd.NaT
    
    # Process SALE_DATE_TIME
    if 'SALE_DATE_TIME' in df.columns:
        print("  Processing SALE_DATE_TIME...")
        original_nulls = df['SALE_DATE_TIME'].isna().sum()
        
        df['SALE_DATE_TIME'] = df['SALE_DATE_TIME'].apply(parse_flexible_datetime)
        
        # Convert to string format for CSV: YYYY-MM-DD HH:MM:SS
        df['SALE_DATE_TIME'] = df['SALE_DATE_TIME'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else ''
        )
        
        new_nulls = (df['SALE_DATE_TIME'] == '').sum()
        print(f"    Original NULLs: {original_nulls:,}, After parsing: {new_nulls:,}")
        if new_nulls > original_nulls:
            print(f"    ⚠️  Warning: {new_nulls - original_nulls:,} values could not be parsed")
    
    # Process SALE_DATE
    if 'SALE_DATE' in df.columns:
        print("  Processing SALE_DATE...")
        original_nulls = df['SALE_DATE'].isna().sum()
        
        df['SALE_DATE'] = df['SALE_DATE'].apply(parse_flexible_date)
        
        # Convert to string format for CSV: YYYY-MM-DD
        df['SALE_DATE'] = df['SALE_DATE'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
        )
        
        new_nulls = (df['SALE_DATE'] == '').sum()
        print(f"    Original NULLs: {original_nulls:,}, After parsing: {new_nulls:,}")
        if new_nulls > original_nulls:
            print(f"    ⚠️  Warning: {new_nulls - original_nulls:,} values could not be parsed")
    
    print("  ✅ Date normalization complete")
    return df

def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_parquet_to_csv.py <path_to_parquet_file>")
        sys.exit(1)

    parquet_path = Path(sys.argv[1])
    
    # Validate file
    validate_file_path(parquet_path)
    
    # Read parquet file
    print(f"Reading parquet file: {parquet_path.name}")
    try:
        df = pd.read_parquet(parquet_path)
        print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"Error reading parquet file: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)
    
    # Run validation checks
    check_required_columns(df)
    check_null_values(df)
    
    # Clean data
    df = clean_data(df)
    
    # Normalize date formats
    df = normalize_date_formats(df)
    
    # Convert to CSV
    csv_path = parquet_path.with_suffix(".csv")
    print(f"Writing CSV file: {csv_path.name}")
    
    try:
        df.to_csv(csv_path, index=False)
        print(f"Conversion complete: {len(df):,} rows written")
    except Exception as e:
        print(f"Error writing CSV: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)
    
    # Output the path (for the bash script to capture)
    print(csv_path)

if __name__ == "__main__":
    main()

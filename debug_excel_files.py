import pandas as pd
import os

# File paths from the codebase
files = {
    'deliveries': '/Users/prasanthbalaji/desktop/MCCS-ProjectFiles/Advertising_Email_Deliveries_2024.xlsx',
    'engagement': '/Users/prasanthbalaji/desktop/MCCS-ProjectFiles/Advertising_Email_Engagement_2024.xlsx',
    'performance': '/Users/prasanthbalaji/desktop/MCCS-ProjectFiles/Advertising_Email_Performance_2024.xlsx',
    'social_media': '/Users/prasanthbalaji/desktop/MCCS-ProjectFiles/Social_Media_Performance_2024.xlsx'
}

def print_sheet_info(file_path, sheet_name):
    """Print information about a specific sheet"""
    try:
        print(f"\n=== {sheet_name} ===")
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=None)
        print(f"Shape: {df.shape}")
        print("First 10 rows:")
        print(df.head(10))
        print("\nColumn names (first row):")
        print(df.iloc[0].tolist())
    except Exception as e:
        print(f"Error reading {sheet_name}: {e}")

def debug_file(file_name, file_path):
    """Debug a specific Excel file"""
    print(f"\n{'='*50}")
    print(f"DEBUGGING: {file_name.upper()}")
    print(f"Path: {file_path}")
    print(f"{'='*50}")

    if not os.path.exists(file_path):
        print(f"FILE NOT FOUND: {file_path}")
        return

    try:
        # Get all sheet names
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        sheets = xl.sheet_names
        print(f"Available sheets: {sheets}")

        # Debug specific sheets based on the errors
        if file_name == 'engagement':
            print_sheet_info(file_path, 'Email Engagement Details')
        elif file_name == 'performance':
            print_sheet_info(file_path, 'Email Performance Email Sends T')
        elif file_name == 'social_media':
            # Check multiple sheets for social media
            for sheet in ['L1 Performance Metrics', 'Engagement Summary', 'Top 5 Channels by Followers']:
                if sheet in sheets:
                    print_sheet_info(file_path, sheet)
        elif file_name == 'deliveries':
            print_sheet_info(file_path, 'Email Deliveries Details')

    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Debug all files
for name, path in files.items():
    debug_file(name, path)

# Also check retail file
retail_path = '/Users/prasanthbalaji/Desktop/MCCS-ProjectFiles/Retail_Data(Apr-Jun-24).parquet'
print(f"\n{'='*50}")
print("CHECKING RETAIL FILE")
print(f"Path: {retail_path}")
print(f"{'='*50}")

if os.path.exists(retail_path):
    print("Retail file exists")
    try:
        # Try to read parquet file
        df = pd.read_parquet(retail_path)
        print(f"Shape: {df.shape}")
        print("First 10 rows:")
        print(df.head(10))
        print("\nColumns:")
        print(df.columns.tolist())
    except Exception as e:
        print(f"Error reading retail file: {e}")
else:
    print("Retail file NOT FOUND")

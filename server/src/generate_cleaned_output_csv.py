"""
CSV Cleaning Module
Dynamically cleans CSV files by removing duplicates, handling missing values,
validating data types, and trimming whitespace.
"""

import pandas as pd
import numpy as np
import os
import re
from typing import Dict, Tuple


def infer_column_type(series: pd.Series, column_name: str) -> str:
    """
    Dynamically infer the data type of a column based on its name and content.
    
    Args:
        series: pandas Series to analyze
        column_name: name of the column
        
    Returns:
        str: Column type ('numeric', 'email', 'phone', 'date', 'categorical')
    """
    # Already numeric type
    if series.dtype in ['int64', 'float64', 'int32', 'float32']:
        return 'numeric'
    
    # Get non-null sample values
    sample_values = series.dropna().astype(str).head(10)
    
    if len(sample_values) == 0:
        return 'categorical'
    
    # Pattern matching for data type detection
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^[\d\-\(\)\+\s\.]+$'
    date_keywords = ['date', 'time', 'joined', 'created', 'updated', 'modified', 'birth', 'dob']
    email_keywords = ['email', 'e-mail', 'mail']
    phone_keywords = ['phone', 'tel', 'mobile', 'cell', 'fax']
    
    # Check column name first
    col_lower = column_name.lower()
    
    # Date detection by column name (check first to avoid confusion with phone)
    if any(keyword in col_lower for keyword in date_keywords):
        return 'date'
    
    # Email detection
    if any(keyword in col_lower for keyword in email_keywords):
        return 'email'
    
    # Check if values look like emails
    email_matches = sample_values.str.match(email_pattern, na=False).sum()
    if email_matches / len(sample_values) > 0.5:
        return 'email'
    
    # Phone detection
    if any(keyword in col_lower for keyword in phone_keywords):
        return 'phone'
    
    # Check if values look like phone numbers
    phone_matches = sample_values.str.match(phone_pattern, na=False).sum()
    if phone_matches / len(sample_values) > 0.7 and sample_values.str.len().mean() < 20:
        return 'phone'
    
    # Try to parse as dates
    try:
        parsed = pd.to_datetime(sample_values, errors='coerce')
        if parsed.notna().sum() / len(sample_values) > 0.7:
            return 'date'
    except:
        pass
    
    return 'categorical'


def validate_and_clean_column(df: pd.DataFrame, col: str, col_type: str, verbose: bool = True) -> pd.DataFrame:
    """
    Validate and clean a specific column based on its inferred type.
    
    Args:
        df: DataFrame to clean
        col: Column name
        col_type: Inferred column type
        verbose: Whether to print cleaning information
        
    Returns:
        DataFrame with cleaned column
    """
    if col_type == 'email':
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_mask = ~df[col].astype(str).str.match(email_pattern, na=False)
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0 and verbose:
            print(f"  Invalid emails found in '{col}': {invalid_count}")
        
        # Set invalid emails to NaN (but don't overwrite actual NaN)
        df.loc[invalid_mask & df[col].notna(), col] = np.nan
    
    elif col_type == 'phone':
        # Replace 'nan' strings with actual NaN
        df.loc[df[col].astype(str) == 'nan', col] = np.nan
    
    elif col_type == 'date':
        if verbose:
            print(f"  Standardizing dates in '{col}'...")
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df


def generate_cleaned_output_csv(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict:
    """
    Clean a CSV file by handling missing values, duplicates, whitespace, and data validation.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save cleaned CSV (default: ../output/)
        verbose: Whether to print detailed information during processing
        
    Returns:
        dict: Metadata about the cleaning process including:
            - input_file: path to input file
            - output_file: path to output file
            - original_shape: tuple of (rows, columns) before cleaning
            - cleaned_shape: tuple of (rows, columns) after cleaning
            - duplicates_removed: number of duplicate rows removed
            - missing_values_filled: dict of column -> count of filled values
            - column_types: dict of column -> inferred type
    """
    # Validate input file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    # Read CSV
    if verbose:
        print("=" * 60)
        print(f"READING CSV: {os.path.basename(csv_file)}")
        print("=" * 60)
    
    df = pd.read_csv(csv_file, skipinitialspace=True)
    original_shape = df.shape
    
    if verbose:
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {list(df.columns)}\n")
    
    # ===== STEP 1: TRIM WHITESPACE =====
    df.columns = df.columns.str.strip()
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    
    if verbose:
        print("✓ Whitespace trimmed from columns and values")
    
    # ===== STEP 2: INFER COLUMN TYPES =====
    if verbose:
        print("\n" + "=" * 60)
        print("INFERRING COLUMN TYPES")
        print("=" * 60)
    
    column_info = {}
    for col in df.columns:
        col_type = infer_column_type(df[col], col)
        column_info[col] = col_type
        
        if verbose:
            non_null_count = df[col].notna().sum()
            print(f"  {col}: {col_type} ({non_null_count} non-null values)")
    
    # ===== STEP 3: VALIDATE AND CLEAN DATA TYPES =====
    if verbose:
        print("\n" + "=" * 60)
        print("VALIDATING AND CLEANING DATA")
        print("=" * 60)
    
    for col in df.columns:
        df = validate_and_clean_column(df, col, column_info[col], verbose)
    
    # ===== STEP 4: REMOVE DUPLICATE ROWS =====
    if verbose:
        print("\n" + "=" * 60)
        print("REMOVING DUPLICATES")
        print("=" * 60)
    
    rows_before = len(df)
    duplicates_count = df.duplicated().sum()
    df = df.drop_duplicates(keep='first')
    rows_after = len(df)
    
    if verbose:
        print(f"Duplicate rows removed: {duplicates_count}")
        print(f"Rows: {rows_before} → {rows_after}")
    
    # ===== STEP 5: REMOVE COMPLETELY EMPTY ROWS =====
    if verbose:
        print("\n" + "=" * 60)
        print("REMOVING BLANK ROWS")
        print("=" * 60)
    
    rows_before_blank = len(df)
    df = df.dropna(how='all')
    blank_rows_removed = rows_before_blank - len(df)
    
    if verbose:
        print(f"Completely blank rows removed: {blank_rows_removed}")
        print(f"Rows: {rows_before_blank} → {len(df)}")
    
    # ===== STEP 6: HANDLE MISSING VALUES =====
    if verbose:
        print("\n" + "=" * 60)
        print("HANDLING MISSING VALUES")
        print("=" * 60)
    
    missing_before = df.isnull().sum().to_dict()
    missing_values_filled = {}
    
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        
        if missing_count > 0:
            col_type = column_info[col]
            
            if col_type == 'numeric':
                df[col] = df[col].fillna(0)
                fill_value = 0
            elif col_type == 'categorical':
                df[col] = df[col].fillna('Unknown')
                fill_value = 'Unknown'
            elif col_type in ['email', 'phone']:
                df[col] = df[col].fillna('Not Provided')
                fill_value = 'Not Provided'
            elif col_type == 'date':
                fill_value = 'NaT (kept)'
            else:
                df[col] = df[col].fillna('Unknown')
                fill_value = 'Unknown'
            
            missing_values_filled[col] = {
                'count': missing_count,
                'filled_with': fill_value
            }
            
            if verbose:
                print(f"  {col}: {missing_count} missing → filled with {fill_value}")
    
    # ===== SAVE CLEANED DATA =====
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(csv_file), '../output'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    input_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_path = os.path.join(output_dir, f"{input_filename}_cleaned.csv")
    df.to_csv(output_path, index=False)
    
    if verbose:
        print("\n" + "=" * 60)
        print("CLEANING COMPLETE")
        print("=" * 60)
        print(f"Final shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"✓ Cleaned CSV saved to: {output_path}\n")
    
    # Return metadata
    return {
        'input_file': csv_file,
        'output_file': output_path,
        'original_shape': original_shape,
        'cleaned_shape': df.shape,
        'duplicates_removed': duplicates_count,
        'missing_values_filled': missing_values_filled,
        'column_types': column_info,
        'success': True
    }


if __name__ == '__main__':
    import sys
    
    # Check if CSV file is provided as command-line argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Default to example file for testing
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
    
    # Run the cleaning function
    try:
        metadata = generate_cleaned_output_csv(csv_file)
        print(f"Success! Cleaned {metadata['original_shape'][0]} rows down to {metadata['cleaned_shape'][0]} rows.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
"""
Summary Report Generator Module
Generates a summary report CSV with statistics about the input data.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Any


def generate_summary_report_csv(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Generate a summary report CSV with statistics about the input data.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save summary report (default: ../output/)
        verbose: Whether to print detailed information
        
    Returns:
        dict: Metadata about the summary report including:
            - input_file: path to input file
            - output_file: path to summary report
            - total_rows: total number of rows
            - total_columns: total number of columns
            - summary_stats: dictionary of summary statistics
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if verbose:
        print("=" * 60)
        print(f"GENERATING SUMMARY REPORT: {os.path.basename(csv_file)}")
        print("=" * 60)
    
    # Read CSV
    df = pd.read_csv(csv_file, skipinitialspace=True)
    
    # Calculate summary statistics
    summary_data = []
    
    for col in df.columns:
        col_summary = {
            'Column': col,
            'Data Type': str(df[col].dtype),
            'Non-Null Count': df[col].notna().sum(),
            'Null Count': df[col].isna().sum(),
            'Null Percentage': f"{(df[col].isna().sum() / len(df) * 100):.2f}%",
            'Unique Values': df[col].nunique(),
        }
        
        # Add numeric-specific stats
        if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            col_summary['Mean'] = f"{df[col].mean():.2f}" if not df[col].isna().all() else 'N/A'
            col_summary['Median'] = f"{df[col].median():.2f}" if not df[col].isna().all() else 'N/A'
            col_summary['Min'] = f"{df[col].min():.2f}" if not df[col].isna().all() else 'N/A'
            col_summary['Max'] = f"{df[col].max():.2f}" if not df[col].isna().all() else 'N/A'
        else:
            col_summary['Mean'] = 'N/A'
            col_summary['Median'] = 'N/A'
            col_summary['Min'] = 'N/A'
            col_summary['Max'] = 'N/A'
        
        summary_data.append(col_summary)
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(csv_file), '../output'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save summary report
    input_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_path = os.path.join(output_dir, f"{input_filename}_summary_report.csv")
    summary_df.to_csv(output_path, index=False)
    
    if verbose:
        print(f"\n{summary_df.to_string(index=False)}")
        print(f"\n✓ Summary report saved to: {output_path}\n")
    
    return {
        'input_file': csv_file,
        'output_file': output_path,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'summary_stats': summary_data,
        'success': True
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
    
    try:
        metadata = generate_summary_report_csv(csv_file)
        print(f"Success! Generated summary report for {metadata['total_columns']} columns.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

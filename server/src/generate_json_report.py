"""
JSON Report Generator Module
Generates a comprehensive JSON report with detailed data analysis.
"""

import pandas as pd
import numpy as np
import os
import json
from typing import Dict, Any
from datetime import datetime


def generate_json_report(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Generate a comprehensive JSON report with data analysis and quality metrics.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save JSON report (default: ../output/)
        verbose: Whether to print detailed information
        
    Returns:
        dict: Metadata about the JSON report including:
            - input_file: path to input file
            - output_file: path to JSON report
            - report_data: the generated report data
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if verbose:
        print("=" * 60)
        print(f"GENERATING JSON REPORT: {os.path.basename(csv_file)}")
        print("=" * 60)
    
    # Read CSV
    df = pd.read_csv(csv_file, skipinitialspace=True)
    
    # Build comprehensive report
    report = {
        'metadata': {
            'report_generated_at': datetime.now().isoformat(),
            'input_file': os.path.basename(csv_file),
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_bytes': int(df.memory_usage(deep=True).sum())
        },
        'columns': {},
        'data_quality': {
            'total_missing_values': int(df.isna().sum().sum()),
            'missing_percentage': float(df.isna().sum().sum() / (len(df) * len(df.columns)) * 100),
            'duplicate_rows': int(df.duplicated().sum()),
            'duplicate_percentage': float(df.duplicated().sum() / len(df) * 100 if len(df) > 0 else 0)
        },
        'sample_data': df.head(5).to_dict(orient='records')
    }
    
    # Analyze each column
    for col in df.columns:
        col_info = {
            'data_type': str(df[col].dtype),
            'non_null_count': int(df[col].notna().sum()),
            'null_count': int(df[col].isna().sum()),
            'null_percentage': float(df[col].isna().sum() / len(df) * 100 if len(df) > 0 else 0),
            'unique_values': int(df[col].nunique()),
            'uniqueness_percentage': float(df[col].nunique() / len(df) * 100 if len(df) > 0 else 0)
        }
        
        # Numeric column stats
        if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            col_info['statistics'] = {
                'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                'median': float(df[col].median()) if not df[col].isna().all() else None,
                'std': float(df[col].std()) if not df[col].isna().all() else None,
                'min': float(df[col].min()) if not df[col].isna().all() else None,
                'max': float(df[col].max()) if not df[col].isna().all() else None,
                'q25': float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                'q75': float(df[col].quantile(0.75)) if not df[col].isna().all() else None
            }
        else:
            # Categorical column stats
            top_values = df[col].value_counts().head(5).to_dict()
            col_info['top_values'] = {str(k): int(v) for k, v in top_values.items()}
        
        report['columns'][col] = col_info
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(csv_file), '../output'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON report
    input_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_path = os.path.join(output_dir, f"{input_filename}_report.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    if verbose:
        print(f"Report Summary:")
        print(f"  Total Rows: {report['metadata']['total_rows']}")
        print(f"  Total Columns: {report['metadata']['total_columns']}")
        print(f"  Missing Values: {report['data_quality']['total_missing_values']} ({report['data_quality']['missing_percentage']:.2f}%)")
        print(f"  Duplicates: {report['data_quality']['duplicate_rows']} ({report['data_quality']['duplicate_percentage']:.2f}%)")
        print(f"\n✓ JSON report saved to: {output_path}\n")
    
    return {
        'input_file': csv_file,
        'output_file': output_path,
        'report_data': report,
        'success': True
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
    
    try:
        metadata = generate_json_report(csv_file)
        print(f"Success! Generated JSON report with {len(metadata['report_data']['columns'])} column analyses.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

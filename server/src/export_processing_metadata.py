"""
Processing Metadata Export Module
Exports metadata about CSV processing operations including file info and transformation history.
"""

import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, Any


def export_processing_metadata(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Export metadata about the CSV file and processing operations.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save metadata (default: ../output/)
        verbose: Whether to print detailed information
        
    Returns:
        dict: Metadata about the export including:
            - input_file: path to input file
            - output_file: path to metadata JSON
            - metadata: the exported metadata
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if verbose:
        print("=" * 60)
        print(f"EXPORTING PROCESSING METADATA: {os.path.basename(csv_file)}")
        print("=" * 60)
    
    # Get file information
    file_stats = os.stat(csv_file)
    file_size_mb = file_stats.st_size / (1024 * 1024)
    
    # Read CSV to get structure info
    df = pd.read_csv(csv_file, skipinitialspace=True)
    
    # Build metadata
    metadata = {
        'processing_info': {
            'timestamp': datetime.now().isoformat(),
            'processor': 'CSV Data Cleaning Pipeline',
            'version': '1.0.0'
        },
        'file_info': {
            'filename': os.path.basename(csv_file),
            'filepath': os.path.abspath(csv_file),
            'size_bytes': file_stats.st_size,
            'size_mb': round(file_size_mb, 2),
            'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        },
        'data_structure': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage_bytes': int(df.memory_usage(deep=True).sum()),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        },
        'data_profile': {
            'total_cells': len(df) * len(df.columns),
            'populated_cells': int(df.notna().sum().sum()),
            'empty_cells': int(df.isna().sum().sum()),
            'data_density_percentage': round((df.notna().sum().sum() / (len(df) * len(df.columns)) * 100), 2) if len(df) > 0 and len(df.columns) > 0 else 0,
            'duplicate_rows': int(df.duplicated().sum()),
            'unique_rows': int(len(df) - df.duplicated().sum())
        },
        'column_profiles': {}
    }
    
    # Add per-column metadata
    for col in df.columns:
        metadata['column_profiles'][col] = {
            'data_type': str(df[col].dtype),
            'non_null_count': int(df[col].notna().sum()),
            'null_count': int(df[col].isna().sum()),
            'unique_count': int(df[col].nunique()),
            'sample_values': df[col].dropna().head(3).astype(str).tolist()
        }
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(csv_file), '../output'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save metadata
    input_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_path = os.path.join(output_dir, f"{input_filename}_metadata.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    if verbose:
        print(f"\nFile Information:")
        print(f"  Filename: {metadata['file_info']['filename']}")
        print(f"  Size: {metadata['file_info']['size_mb']} MB")
        print(f"  Rows: {metadata['data_structure']['total_rows']:,}")
        print(f"  Columns: {metadata['data_structure']['total_columns']}")
        print(f"  Data Density: {metadata['data_profile']['data_density_percentage']}%")
        print(f"  Duplicates: {metadata['data_profile']['duplicate_rows']:,}")
        print(f"\n✓ Metadata exported to: {output_path}\n")
    
    return {
        'input_file': csv_file,
        'output_file': output_path,
        'metadata': metadata,
        'success': True
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
    
    try:
        result = export_processing_metadata(csv_file)
        print(f"Success! Exported metadata for {result['metadata']['data_structure']['total_columns']} columns.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

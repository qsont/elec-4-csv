"""
Quality Score Report Generator Module
Calculates and reports data quality scores based on various metrics.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Any


def calculate_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate data quality score based on multiple factors.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Quality metrics and scores
    """
    total_cells = len(df) * len(df.columns)
    
    # Completeness Score (100 - missing data percentage)
    missing_cells = df.isna().sum().sum()
    completeness_score = (1 - (missing_cells / total_cells)) * 100 if total_cells > 0 else 0
    
    # Uniqueness Score (based on duplicate rows)
    duplicate_rows = df.duplicated().sum()
    uniqueness_score = (1 - (duplicate_rows / len(df))) * 100 if len(df) > 0 else 100
    
    # Validity Score (placeholder - would check data format validity)
    # For now, assume 95% validity (this would be enhanced with actual validation)
    validity_score = 95.0
    
    # Consistency Score (based on data type consistency)
    consistency_issues = 0
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check for mixed types or inconsistent formatting
            non_null = df[col].dropna()
            if len(non_null) > 0:
                # Simple heuristic: check if values have wildly different lengths
                lengths = non_null.astype(str).str.len()
                if lengths.std() > lengths.mean() * 0.5:
                    consistency_issues += 1
    
    consistency_score = (1 - (consistency_issues / len(df.columns))) * 100 if len(df.columns) > 0 else 100
    
    # Overall Quality Score (weighted average)
    weights = {
        'completeness': 0.35,
        'uniqueness': 0.25,
        'validity': 0.25,
        'consistency': 0.15
    }
    
    overall_score = (
        completeness_score * weights['completeness'] +
        uniqueness_score * weights['uniqueness'] +
        validity_score * weights['validity'] +
        consistency_score * weights['consistency']
    )
    
    return {
        'overall_score': round(overall_score, 2),
        'completeness_score': round(completeness_score, 2),
        'uniqueness_score': round(uniqueness_score, 2),
        'validity_score': round(validity_score, 2),
        'consistency_score': round(consistency_score, 2),
        'grade': get_quality_grade(overall_score),
        'details': {
            'total_cells': total_cells,
            'missing_cells': int(missing_cells),
            'duplicate_rows': int(duplicate_rows),
            'consistency_issues': consistency_issues
        }
    }


def get_quality_grade(score: float) -> str:
    """Convert quality score to letter grade."""
    if score >= 95:
        return 'A+ (Excellent)'
    elif score >= 90:
        return 'A (Very Good)'
    elif score >= 85:
        return 'B+ (Good)'
    elif score >= 80:
        return 'B (Above Average)'
    elif score >= 70:
        return 'C (Average)'
    elif score >= 60:
        return 'D (Below Average)'
    else:
        return 'F (Poor)'


def generate_quality_score_report(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Generate a data quality score report for the CSV file.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save quality report (default: ../output/)
        verbose: Whether to print detailed information
        
    Returns:
        dict: Metadata about the quality report including:
            - input_file: path to input file
            - output_file: path to quality report
            - quality_metrics: calculated quality scores
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if verbose:
        print("=" * 60)
        print(f"GENERATING QUALITY SCORE REPORT: {os.path.basename(csv_file)}")
        print("=" * 60)
    
    # Read CSV
    df = pd.read_csv(csv_file, skipinitialspace=True)
    
    # Calculate quality scores
    quality_metrics = calculate_quality_score(df)
    
    # Create report DataFrame
    report_data = [
        {'Metric': 'Overall Quality Score', 'Score': f"{quality_metrics['overall_score']}%", 'Grade': quality_metrics['grade']},
        {'Metric': 'Completeness', 'Score': f"{quality_metrics['completeness_score']}%", 'Grade': get_quality_grade(quality_metrics['completeness_score'])},
        {'Metric': 'Uniqueness', 'Score': f"{quality_metrics['uniqueness_score']}%", 'Grade': get_quality_grade(quality_metrics['uniqueness_score'])},
        {'Metric': 'Validity', 'Score': f"{quality_metrics['validity_score']}%", 'Grade': get_quality_grade(quality_metrics['validity_score'])},
        {'Metric': 'Consistency', 'Score': f"{quality_metrics['consistency_score']}%", 'Grade': get_quality_grade(quality_metrics['consistency_score'])},
    ]
    
    report_df = pd.DataFrame(report_data)
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(csv_file), '../output'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save quality report
    input_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_path = os.path.join(output_dir, f"{input_filename}_quality_report.csv")
    report_df.to_csv(output_path, index=False)
    
    if verbose:
        print(f"\n{report_df.to_string(index=False)}")
        print(f"\nDetails:")
        print(f"  Total Cells: {quality_metrics['details']['total_cells']:,}")
        print(f"  Missing Cells: {quality_metrics['details']['missing_cells']:,}")
        print(f"  Duplicate Rows: {quality_metrics['details']['duplicate_rows']:,}")
        print(f"  Consistency Issues: {quality_metrics['details']['consistency_issues']}")
        print(f"\n✓ Quality report saved to: {output_path}\n")
    
    return {
        'input_file': csv_file,
        'output_file': output_path,
        'quality_metrics': quality_metrics,
        'success': True
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
    
    try:
        metadata = generate_quality_score_report(csv_file)
        print(f"Success! Overall quality score: {metadata['quality_metrics']['overall_score']}% ({metadata['quality_metrics']['grade']})")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

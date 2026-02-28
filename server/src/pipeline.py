"""
CSV Processing Pipeline
Main orchestrator for running all CSV processing functions.
Perfect for CI/CD environments like GitHub Actions.
"""

import sys
import os
from typing import List, Dict, Any

# Import all processing functions
from generate_cleaned_output_csv import generate_cleaned_output_csv
from generate_summary_report_csv import generate_summary_report_csv
from generate_json_report import generate_json_report
from generate_quality_score_report import generate_quality_score_report
from export_processing_metadata import export_processing_metadata


def run_pipeline(csv_file: str, output_dir: str = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Run the complete CSV processing pipeline.
    
    Args:
        csv_file: Path to input CSV file
        output_dir: Directory to save all outputs (default: ../output/)
        verbose: Whether to print detailed information
        
    Returns:
        dict: Results from all processing steps
    """
    print("=" * 70)
    print("CSV PROCESSING PIPELINE")
    print("=" * 70)
    print(f"Input File: {csv_file}")
    print(f"Output Directory: {output_dir or 'default (../output/)'}")
    print("=" * 70)
    print()
    
    results = {
        'input_file': csv_file,
        'pipeline_status': 'running',
        'steps': {}
    }
    
    try:
        # Step 1: Clean CSV
        print("\n[1/5] Running CSV Cleaning...")
        results['steps']['cleaning'] = generate_cleaned_output_csv(csv_file, output_dir, verbose)
        
        # Step 2: Generate Summary Report
        print("\n[2/5] Generating Summary Report...")
        results['steps']['summary'] = generate_summary_report_csv(csv_file, output_dir, verbose)
        
        # Step 3: Generate JSON Report
        print("\n[3/5] Generating JSON Report...")
        results['steps']['json_report'] = generate_json_report(csv_file, output_dir, verbose)
        
        # Step 4: Generate Quality Score Report
        print("\n[4/5] Generating Quality Score Report...")
        results['steps']['quality'] = generate_quality_score_report(csv_file, output_dir, verbose)
        
        # Step 5: Export Processing Metadata
        print("\n[5/5] Exporting Processing Metadata...")
        results['steps']['metadata'] = export_processing_metadata(csv_file, output_dir, verbose)
        
        results['pipeline_status'] = 'completed'
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nGenerated Files:")
        for step, data in results['steps'].items():
            if 'output_file' in data:
                print(f"  ✓ {step.upper()}: {os.path.basename(data['output_file'])}")
        
        return results
        
    except Exception as e:
        results['pipeline_status'] = 'failed'
        results['error'] = str(e)
        print(f"\n❌ Pipeline failed: {e}")
        raise


def process_directory(input_dir: str, output_dir: str = None, verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Process all CSV files in a directory.
    
    Args:
        input_dir: Directory containing CSV files
        output_dir: Directory to save all outputs
        verbose: Whether to print detailed information
        
    Returns:
        list: Results from processing each file
    """
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return []
    
    print(f"Found {len(csv_files)} CSV file(s) to process")
    print()
    
    all_results = []
    
    for i, csv_file in enumerate(csv_files, 1):
        csv_path = os.path.join(input_dir, csv_file)
        print(f"\n{'=' * 70}")
        print(f"Processing file {i}/{len(csv_files)}: {csv_file}")
        print(f"{'=' * 70}\n")
        
        try:
            result = run_pipeline(csv_path, output_dir, verbose)
            all_results.append(result)
        except Exception as e:
            print(f"Failed to process {csv_file}: {e}")
            all_results.append({
                'input_file': csv_path,
                'pipeline_status': 'failed',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in all_results if r['pipeline_status'] == 'completed')
    failed = sum(1 for r in all_results if r['pipeline_status'] == 'failed')
    
    print(f"Total files: {len(csv_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    return all_results


if __name__ == '__main__':
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Process single file: python pipeline.py <csv_file>")
        print("  Process directory:   python pipeline.py --dir <input_dir> [--output <output_dir>]")
        print()
        print("Running with default test file...")
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
        run_pipeline(csv_file)
        sys.exit(0)
    
    # Check for directory mode
    if sys.argv[1] == '--dir':
        if len(sys.argv) < 3:
            print("Error: Please specify input directory")
            sys.exit(1)
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == '--output' else None
        
        results = process_directory(input_dir, output_dir)
        
        # Exit with error code if any processing failed
        if any(r['pipeline_status'] == 'failed' for r in results):
            sys.exit(1)
    else:
        # Single file mode
        csv_file = sys.argv[1]
        output_dir = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--output' else None
        
        try:
            run_pipeline(csv_file, output_dir)
        except Exception as e:
            sys.exit(1)

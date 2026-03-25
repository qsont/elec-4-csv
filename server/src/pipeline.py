"""
CSV Processing Pipeline
Main orchestrator for running all CSV processing functions.
Perfect for CI/CD environments like GitHub Actions.
"""

import sys
import os
import logging
from typing import List, Dict, Any

# --- LOGGING SETUP ---
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'pipeline_execution.log'), mode='a'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Ensures logging config is not overridden by pytest or other modules
)
# ---------------------

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
    logging.info("=" * 70)
    logging.info("CSV PROCESSING PIPELINE")
    logging.info("=" * 70)
    logging.info(f"Input File: {csv_file}")
    logging.info(f"Output Directory: {output_dir or 'default (../output/)'}")
    logging.info("=" * 70)
    logging.info("")
    
    results = {
        'input_file': csv_file,
        'pipeline_status': 'running',
        'steps': {}
    }
    
    try:
        # Step 1: Clean CSV
        logging.info("\n[1/5] Running CSV Cleaning...")
        results['steps']['cleaning'] = generate_cleaned_output_csv(csv_file, output_dir, verbose)
        
        # Step 2: Generate Summary Report
        logging.info("\n[2/5] Generating Summary Report...")
        results['steps']['summary'] = generate_summary_report_csv(csv_file, output_dir, verbose)
        
        # Step 3: Generate JSON Report
        logging.info("\n[3/5] Generating JSON Report...")
        results['steps']['json_report'] = generate_json_report(csv_file, output_dir, verbose)
        
        # Step 4: Generate Quality Score Report
        logging.info("\n[4/5] Generating Quality Score Report...")
        results['steps']['quality'] = generate_quality_score_report(csv_file, output_dir, verbose)
        
        # Step 5: Export Processing Metadata
        logging.info("\n[5/5] Exporting Processing Metadata...")
        results['steps']['metadata'] = export_processing_metadata(csv_file, output_dir, verbose)
        
        results['pipeline_status'] = 'completed'
        
        logging.info("\n" + "=" * 70)
        logging.info("PIPELINE COMPLETED SUCCESSFULLY")
        logging.info("=" * 70)
        logging.info(f"\nGenerated Files:")
        for step, data in results['steps'].items():
            if 'output_file' in data:
                logging.info(f"  - {step.upper()}: {os.path.basename(data['output_file'])}")
        
        return results
        
    except Exception as e:
        results['pipeline_status'] = 'failed'
        results['error'] = str(e)
        logging.error(f"\nPipeline failed: {e}")
    
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
    dir_contents = os.listdir(input_dir)
    logging.info(f"Input directory contents: {dir_contents}")
    csv_files = [f for f in dir_contents if f.endswith('.csv')]

    if not csv_files:
        logging.info(f"No CSV files found in {input_dir}. If you expected files, check your commit and workflow paths.")
        return []

    logging.info(f"Found {len(csv_files)} CSV file(s) to process: {csv_files}")
    logging.info("")
    
    all_results = []
    
    for i, csv_file in enumerate(csv_files, 1):
        csv_path = os.path.join(input_dir, csv_file)
        logging.info(f"\n{'=' * 70}")
        logging.info(f"Processing file {i}/{len(csv_files)}: {csv_file}")
        logging.info(f"{'=' * 70}\n")
        
        try:
            result = run_pipeline(csv_path, output_dir, verbose)
            all_results.append(result)
        except Exception as e:
            logging.error(f"Failed to process {csv_file}: {e}")
            all_results.append({
                'input_file': csv_path,
                'pipeline_status': 'failed',
                'error': str(e)
            })
    
    # Summary
    logging.info("\n" + "=" * 70)
    logging.info("BATCH PROCESSING SUMMARY")
    logging.info("=" * 70)
    
    successful = sum(1 for r in all_results if r['pipeline_status'] == 'completed')
    failed = sum(1 for r in all_results if r['pipeline_status'] == 'failed')
    
    logging.info(f"Total files: {len(csv_files)}")
    logging.info(f"Successful: {successful}")
    logging.info(f"Failed: {failed}")
    
    return all_results


if __name__ == '__main__':
    # Parse command-line arguments
    if len(sys.argv) < 2:
        logging.info("Usage:")
        logging.info("  Process single file: python pipeline.py <csv_file>")
        logging.info("  Process directory:   python pipeline.py --dir <input_dir> [--output <output_dir>]")
        logging.info("")
        logging.info("Running with default test file...")
        csv_file = os.path.abspath('../input/csv-cleaner-example.csv')
        run_pipeline(csv_file)
        sys.exit(0)
    
    # Check for directory mode
    if sys.argv[1] == '--dir':
        if len(sys.argv) < 3:
            logging.error("Error: Please specify input directory")
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
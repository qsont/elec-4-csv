"""
Tests for pipeline module
"""

import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pipeline import run_pipeline, process_directory


class TestRunPipeline:
    """Tests for main pipeline function."""
    
    @pytest.mark.parametrize("csv_file_fixture", ["sample_csv_clean", "input_csv_files"], indirect=True)
    def test_run_pipeline_success(self, csv_file_fixture, output_dir):
        """Test that pipeline runs successfully for sample and input CSVs."""
        # csv_file_fixture can be a list (input_csv_files) or a single file (sample_csv_clean)
        files = csv_file_fixture if isinstance(csv_file_fixture, list) else [csv_file_fixture]
        for csv_file in files:
            result = run_pipeline(csv_file, output_dir, verbose=False)
            assert result['pipeline_status'] == 'completed'
            assert 'steps' in result
            assert len(result['steps']) == 5
    
    def test_run_pipeline_all_steps(self, sample_csv_clean, output_dir):
        """Test that all pipeline steps are executed."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        
        steps = result['steps']
        
        assert 'cleaning' in steps
        assert 'summary' in steps
        assert 'json_report' in steps
        assert 'quality' in steps
        assert 'metadata' in steps
        
        # All steps should be successful
        for step_name, step_result in steps.items():
            assert step_result['success'] is True
    
    def test_pipeline_generates_all_files(self, sample_csv_clean, output_dir):
        """Test that pipeline generates all expected output files."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        
        # Check all output files exist
        for step_name, step_result in result['steps'].items():
            assert 'output_file' in step_result
            assert os.path.exists(step_result['output_file'])
    
    def test_pipeline_cleaning_step(self, sample_csv_messy, output_dir):
        """Test cleaning step in pipeline."""
        result = run_pipeline(sample_csv_messy, output_dir, verbose=False)
        
        cleaning = result['steps']['cleaning']
        assert 'duplicates_removed' in cleaning
        assert 'missing_values_filled' in cleaning
        assert 'column_types' in cleaning
    
    def test_pipeline_quality_step(self, sample_csv_clean, output_dir):
        """Test quality step in pipeline."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        
        quality = result['steps']['quality']
        assert 'quality_metrics' in quality
        assert 'overall_score' in quality['quality_metrics']
    
    def test_pipeline_invalid_file(self, output_dir):
        """Test pipeline handling of invalid file."""
        with pytest.raises(Exception):
            run_pipeline('non_existent.csv', output_dir, verbose=False)
    
    def test_pipeline_input_file_recorded(self, sample_csv_clean, output_dir):
        """Test that input file is recorded in result."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        
        assert 'input_file' in result
        assert result['input_file'] == sample_csv_clean


class TestProcessDirectory:
    """Tests for directory processing function."""
    
    def test_process_directory_multiple_files(self, temp_dir, output_dir):
        """Test processing multiple CSV files in a directory."""
        # Create multiple CSV files
        for i in range(3):
            csv_path = os.path.join(temp_dir, f'test_{i}.csv')
            df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
            df.to_csv(csv_path, index=False)
        
        results = process_directory(temp_dir, output_dir, verbose=False)
        
        assert len(results) == 3
        
        # All should be successful
        for result in results:
            assert result['pipeline_status'] == 'completed'
    
    def test_process_directory_empty(self, temp_dir, output_dir):
        """Test processing empty directory."""
        results = process_directory(temp_dir, output_dir, verbose=False)
        
        assert len(results) == 0
    
    def test_process_directory_single_file(self, temp_dir, output_dir):
        """Test processing directory with single file."""
        csv_path = os.path.join(temp_dir, 'test.csv')
        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        df.to_csv(csv_path, index=False)
        
        results = process_directory(temp_dir, output_dir, verbose=False)
        
        assert len(results) == 1
        assert results[0]['pipeline_status'] == 'completed'
    
    def test_process_directory_mixed_results(self, temp_dir, output_dir):
        """Test directory processing with some failures."""
        # Create valid CSV
        csv_path1 = os.path.join(temp_dir, 'valid.csv')
        df = pd.DataFrame({'A': [1, 2, 3]})
        df.to_csv(csv_path1, index=False)
        
        # Create invalid CSV (corrupted)
        csv_path2 = os.path.join(temp_dir, 'invalid.csv')
        with open(csv_path2, 'w') as f:
            f.write('invalid,csv,content\n')
            f.write('this,is,broken\n' * 100)
        
        results = process_directory(temp_dir, output_dir, verbose=False)
        
        # Should process both files
        assert len(results) >= 1
    
    def test_process_directory_filters_csv_only(self, temp_dir, output_dir):
        """Test that only CSV files are processed."""
        # Create CSV file
        csv_path = os.path.join(temp_dir, 'test.csv')
        df = pd.DataFrame({'A': [1, 2]})
        df.to_csv(csv_path, index=False)
        
        # Create non-CSV file
        txt_path = os.path.join(temp_dir, 'test.txt')
        with open(txt_path, 'w') as f:
            f.write('not a csv')
        
        results = process_directory(temp_dir, output_dir, verbose=False)
        
        # Should only process CSV file
        assert len(results) == 1


class TestPipelineIntegration:
    """Integration tests for complete pipeline."""

    def test_input_csv_count(self, input_csv_count, input_csv_files):
        """Test that the number of CSV files in input folder is counted correctly."""
        assert input_csv_count == len(input_csv_files)
        # Optionally, print the files for debug
        print(f"Input CSV files: {input_csv_files}")

    def test_end_to_end_clean_data(self, sample_csv_clean, output_dir):
        """Test end-to-end pipeline with clean data."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        # Verify all outputs
        assert result['pipeline_status'] == 'completed'
        assert result['steps']['cleaning']['success']
        assert result['steps']['quality']['quality_metrics']['overall_score'] >= 90

    def test_end_to_end_messy_data(self, sample_csv_messy, output_dir):
        """Test end-to-end pipeline with messy data."""
        result = run_pipeline(sample_csv_messy, output_dir, verbose=False)
        # Should complete but with lower quality scores
        assert result['pipeline_status'] == 'completed'
        assert result['steps']['quality']['quality_metrics']['overall_score'] < 100
        assert result['steps']['cleaning']['duplicates_removed'] >= 0

    def test_pipeline_output_consistency(self, sample_csv_clean, output_dir):
        """Test that pipeline outputs are consistent across steps."""
        result = run_pipeline(sample_csv_clean, output_dir, verbose=False)
        cleaning_output = result['steps']['cleaning']['output_file']
        # Read cleaned CSV
        cleaned_df = pd.read_csv(cleaning_output)
        # Summary should have one row per column
        summary_output = result['steps']['summary']['output_file']
        summary_df = pd.read_csv(summary_output)
        assert len(summary_df) == len(cleaned_df.columns)

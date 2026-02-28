"""
Tests for generate_json_report module
"""

import pytest
import pandas as pd
import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from generate_json_report import generate_json_report


class TestGenerateJSONReport:
    """Tests for JSON report generation function."""
    
    def test_generate_json_report(self, sample_csv_clean, output_dir):
        """Test basic JSON report generation."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        assert result['success'] is True
        assert os.path.exists(result['output_file'])
        assert result['output_file'].endswith('_report.json')
    
    def test_json_report_structure(self, sample_csv_clean, output_dir):
        """Test that JSON report has correct structure."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        # Check main sections exist
        assert 'metadata' in report
        assert 'columns' in report
        assert 'data_quality' in report
        assert 'sample_data' in report
    
    def test_json_report_metadata(self, sample_csv_clean, output_dir):
        """Test metadata section of JSON report."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        metadata = report['metadata']
        assert 'report_generated_at' in metadata
        assert 'input_file' in metadata
        assert 'total_rows' in metadata
        assert 'total_columns' in metadata
        assert metadata['total_rows'] > 0
    
    def test_json_report_column_analysis(self, sample_csv_clean, output_dir):
        """Test column analysis in JSON report."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        columns = report['columns']
        assert len(columns) > 0
        
        # Check first column has required fields
        first_col = list(columns.values())[0]
        assert 'data_type' in first_col
        assert 'non_null_count' in first_col
        assert 'null_count' in first_col
        assert 'unique_values' in first_col
    
    def test_json_report_numeric_statistics(self, sample_csv_clean, output_dir):
        """Test that numeric columns have statistical data."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        # Find a numeric column
        for col_name, col_data in report['columns'].items():
            if 'statistics' in col_data:
                stats = col_data['statistics']
                assert 'mean' in stats
                assert 'median' in stats
                assert 'std' in stats
                assert 'min' in stats
                assert 'max' in stats
                break
    
    def test_json_report_categorical_top_values(self, sample_csv_clean, output_dir):
        """Test that categorical columns have top values."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        # Find a categorical column
        for col_name, col_data in report['columns'].items():
            if 'top_values' in col_data:
                assert len(col_data['top_values']) > 0
                break
    
    def test_json_report_data_quality_metrics(self, sample_csv_messy, output_dir):
        """Test data quality metrics in JSON report."""
        result = generate_json_report(sample_csv_messy, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        quality = report['data_quality']
        assert 'total_missing_values' in quality
        assert 'missing_percentage' in quality
        assert 'duplicate_rows' in quality
        assert 'duplicate_percentage' in quality
        assert quality['total_missing_values'] >= 0
    
    def test_json_report_sample_data(self, sample_csv_clean, output_dir):
        """Test that sample data is included."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            report = json.load(f)
        
        sample_data = report['sample_data']
        assert len(sample_data) <= 5  # Should have max 5 sample rows
        assert isinstance(sample_data, list)
    
    def test_json_report_invalid_file(self, output_dir):
        """Test handling of invalid file path."""
        with pytest.raises(FileNotFoundError):
            generate_json_report('non_existent.csv', output_dir, verbose=False)
    
    def test_json_report_return_metadata(self, sample_csv_clean, output_dir):
        """Test that function returns correct metadata."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        assert 'input_file' in result
        assert 'output_file' in result
        assert 'report_data' in result
        assert 'success' in result
        assert result['success'] is True
    
    def test_json_report_valid_json(self, sample_csv_clean, output_dir):
        """Test that generated file is valid JSON."""
        result = generate_json_report(sample_csv_clean, output_dir, verbose=False)
        
        # Should not raise exception
        with open(result['output_file'], 'r') as f:
            json.load(f)

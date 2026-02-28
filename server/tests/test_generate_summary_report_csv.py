"""
Tests for generate_summary_report_csv module
"""

import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from generate_summary_report_csv import generate_summary_report_csv


class TestGenerateSummaryReportCSV:
    """Tests for summary report generation function."""
    
    def test_generate_summary_report(self, sample_csv_clean, output_dir):
        """Test basic summary report generation."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        assert result['success'] is True
        assert os.path.exists(result['output_file'])
        assert result['output_file'].endswith('_summary_report.csv')
    
    def test_summary_report_content(self, sample_csv_clean, output_dir):
        """Test that summary report contains expected columns."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        summary_df = pd.read_csv(result['output_file'])
        
        # Check required columns exist
        expected_columns = ['Column', 'Data Type', 'Non-Null Count', 'Null Count', 
                          'Null Percentage', 'Unique Values']
        for col in expected_columns:
            assert col in summary_df.columns
    
    def test_summary_report_row_count(self, sample_csv_clean, output_dir):
        """Test that summary has one row per column in input."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        original_df = pd.read_csv(sample_csv_clean)
        summary_df = pd.read_csv(result['output_file'])
        
        assert len(summary_df) == len(original_df.columns)
    
    def test_summary_report_metadata(self, sample_csv_clean, output_dir):
        """Test that metadata is returned correctly."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        assert 'input_file' in result
        assert 'output_file' in result
        assert 'total_rows' in result
        assert 'total_columns' in result
        assert 'summary_stats' in result
        assert result['total_columns'] > 0
    
    def test_summary_report_numeric_stats(self, sample_csv_clean, output_dir):
        """Test that numeric columns have statistical summaries."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        summary_df = pd.read_csv(result['output_file'])
        
        # Find numeric columns
        numeric_rows = summary_df[summary_df['Column'] == 'Age']
        if len(numeric_rows) > 0:
            assert numeric_rows['Mean'].iloc[0] != 'N/A'
            assert numeric_rows['Median'].iloc[0] != 'N/A'
    
    def test_summary_report_categorical_stats(self, sample_csv_clean, output_dir):
        """Test that categorical columns show N/A for numeric stats."""
        result = generate_summary_report_csv(sample_csv_clean, output_dir, verbose=False)
        
        summary_df = pd.read_csv(result['output_file'])
        
        # Find categorical columns
        categorical_rows = summary_df[summary_df['Column'] == 'Name']
        if len(categorical_rows) > 0:
            # Mean should be N/A string or nan for categorical
            mean_val = str(categorical_rows['Mean'].iloc[0])
            assert mean_val == 'N/A' or mean_val == 'nan'
    
    def test_summary_report_missing_values(self, sample_csv_messy, output_dir):
        """Test that missing values are correctly counted."""
        result = generate_summary_report_csv(sample_csv_messy, output_dir, verbose=False)
        
        summary_df = pd.read_csv(result['output_file'])
        
        # Check that null counts are present
        assert summary_df['Null Count'].sum() > 0
    
    def test_summary_report_invalid_file(self, output_dir):
        """Test handling of invalid file path."""
        with pytest.raises(FileNotFoundError):
            generate_summary_report_csv('non_existent.csv', output_dir, verbose=False)
    
    def test_summary_report_empty_csv(self, sample_csv_empty, output_dir):
        """Test summary generation for empty CSV."""
        result = generate_summary_report_csv(sample_csv_empty, output_dir, verbose=False)
        
        assert result['success'] is True
        assert result['total_rows'] == 0
        assert result['total_columns'] == 3
    
    def test_summary_report_unique_values(self, sample_csv_with_duplicates, output_dir):
        """Test that unique value counts are accurate."""
        result = generate_summary_report_csv(sample_csv_with_duplicates, output_dir, verbose=False)
        
        summary_df = pd.read_csv(result['output_file'])
        
        # ID column should have fewer unique values than total rows
        id_row = summary_df[summary_df['Column'] == 'ID']
        assert int(id_row['Unique Values'].iloc[0]) < result['total_rows']

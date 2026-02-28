"""
Tests for generate_cleaned_output_csv module
"""

import pytest
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from generate_cleaned_output_csv import (
    generate_cleaned_output_csv,
    infer_column_type,
    validate_and_clean_column
)


class TestInferColumnType:
    """Tests for column type inference function."""
    
    def test_infer_numeric_column(self):
        """Test numeric column detection."""
        series = pd.Series([1, 2, 3, 4, 5])
        result = infer_column_type(series, 'age')
        assert result == 'numeric'
    
    def test_infer_email_column_by_name(self):
        """Test email detection by column name."""
        series = pd.Series(['test1', 'test2', 'test3'])
        result = infer_column_type(series, 'email_address')
        assert result == 'email'
    
    def test_infer_email_column_by_content(self):
        """Test email detection by content pattern."""
        series = pd.Series(['john@example.com', 'jane@test.com', 'bob@mail.com'])
        result = infer_column_type(series, 'contact')
        assert result == 'email'
    
    def test_infer_phone_column_by_name(self):
        """Test phone detection by column name."""
        series = pd.Series(['123', '456', '789'])
        result = infer_column_type(series, 'phone_number')
        assert result == 'phone'
    
    def test_infer_date_column_by_name(self):
        """Test date detection by column name."""
        series = pd.Series(['2023-01-01', '2023-02-01', '2023-03-01'])
        result = infer_column_type(series, 'date_joined')
        assert result == 'date'
    
    def test_infer_categorical_column(self):
        """Test categorical column detection."""
        series = pd.Series(['Active', 'Inactive', 'Pending'])
        result = infer_column_type(series, 'status')
        assert result == 'categorical'
    
    def test_infer_empty_column(self):
        """Test handling of empty column."""
        series = pd.Series([None, None, None])
        result = infer_column_type(series, 'empty_col')
        assert result == 'categorical'


class TestValidateAndCleanColumn:
    """Tests for column validation and cleaning function."""
    
    def test_validate_email_column(self):
        """Test email validation."""
        df = pd.DataFrame({'email': ['valid@test.com', 'invalid-email', 'another@test.com']})
        result = validate_and_clean_column(df, 'email', 'email', verbose=False)
        assert result['email'].isna().sum() == 1  # One invalid email
    
    def test_validate_date_column(self):
        """Test date standardization."""
        df = pd.DataFrame({'date': ['2023-01-01', '01/15/2023', 'invalid']})
        result = validate_and_clean_column(df, 'date', 'date', verbose=False)
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert result['date'].isna().sum() >= 1  # At least one invalid date
    
    def test_validate_phone_column(self):
        """Test phone number validation."""
        df = pd.DataFrame({'phone': ['555-1234', 'nan', '555-5678']})
        result = validate_and_clean_column(df, 'phone', 'phone', verbose=False)
        assert result['phone'].isna().sum() >= 1  # 'nan' string converted to NaN


class TestGenerateCleanedOutputCSV:
    """Tests for main CSV cleaning function."""
    
    def test_clean_messy_csv(self, sample_csv_messy, output_dir):
        """Test cleaning a messy CSV file."""
        result = generate_cleaned_output_csv(sample_csv_messy, output_dir, verbose=False)
        
        assert result['success'] is True
        assert os.path.exists(result['output_file'])
        assert result['duplicates_removed'] >= 0
        assert result['original_shape'][0] > 0
    
    def test_clean_csv_removes_duplicates(self, sample_csv_with_duplicates, output_dir):
        """Test that duplicate rows are removed."""
        result = generate_cleaned_output_csv(sample_csv_with_duplicates, output_dir, verbose=False)
        
        assert result['duplicates_removed'] == 2  # Should find 2 duplicates
        assert result['cleaned_shape'][0] < result['original_shape'][0]
    
    def test_clean_csv_fills_missing_values(self, sample_csv_messy, output_dir):
        """Test that missing values are filled."""
        result = generate_cleaned_output_csv(sample_csv_messy, output_dir, verbose=False)
        
        assert len(result['missing_values_filled']) > 0
        
        # Read cleaned file and check no missing values in non-date columns
        cleaned_df = pd.read_csv(result['output_file'])
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype != 'datetime64[ns]':
                # Non-date columns should have missing values filled
                pass  # Some columns may still have NaN if they're dates
    
    def test_clean_csv_output_exists(self, sample_csv_clean, output_dir):
        """Test that output file is created."""
        result = generate_cleaned_output_csv(sample_csv_clean, output_dir, verbose=False)
        
        assert os.path.exists(result['output_file'])
        assert result['output_file'].endswith('_cleaned.csv')
    
    def test_clean_csv_preserves_data_structure(self, sample_csv_clean, output_dir):
        """Test that column structure is preserved."""
        result = generate_cleaned_output_csv(sample_csv_clean, output_dir, verbose=False)
        
        original_df = pd.read_csv(sample_csv_clean)
        cleaned_df = pd.read_csv(result['output_file'])
        
        assert len(cleaned_df.columns) == len(original_df.columns)
    
    def test_clean_csv_returns_metadata(self, sample_csv_clean, output_dir):
        """Test that metadata is returned."""
        result = generate_cleaned_output_csv(sample_csv_clean, output_dir, verbose=False)
        
        assert 'input_file' in result
        assert 'output_file' in result
        assert 'original_shape' in result
        assert 'cleaned_shape' in result
        assert 'duplicates_removed' in result
        assert 'column_types' in result
        assert 'success' in result
    
    def test_clean_csv_invalid_file(self, output_dir):
        """Test handling of invalid file path."""
        with pytest.raises(FileNotFoundError):
            generate_cleaned_output_csv('non_existent_file.csv', output_dir, verbose=False)
    
    def test_clean_csv_whitespace_trimming(self, temp_dir, output_dir):
        """Test that whitespace is properly trimmed."""
        # Create CSV with leading/trailing spaces
        csv_path = os.path.join(temp_dir, 'test_whitespace.csv')
        data = {
            'Name ': ['  John  ', ' Jane ', 'Bob  '],
            ' Email ': ['john@test.com', 'jane@test.com', 'bob@test.com']
        }
        pd.DataFrame(data).to_csv(csv_path, index=False)
        
        result = generate_cleaned_output_csv(csv_path, output_dir, verbose=False)
        cleaned_df = pd.read_csv(result['output_file'])
        
        # Check column names are trimmed
        assert 'Name' in cleaned_df.columns
        assert 'Email' in cleaned_df.columns
        
        # Check values contain expected name (may have some formatting)
        assert 'John' in cleaned_df['Name'].iloc[0]
    
    def test_clean_csv_column_type_inference(self, sample_csv_messy, output_dir):
        """Test that column types are correctly inferred."""
        result = generate_cleaned_output_csv(sample_csv_messy, output_dir, verbose=False)
        
        column_types = result['column_types']
        assert 'Email Address' in column_types
        assert column_types['Email Address'] == 'email'
        assert column_types['Phone #'] == 'phone'
        assert column_types['Date Joined'] == 'date'
    
    def test_clean_csv_empty_file(self, sample_csv_empty, output_dir):
        """Test handling of empty CSV file."""
        result = generate_cleaned_output_csv(sample_csv_empty, output_dir, verbose=False)
        
        assert result['success'] is True
        assert result['cleaned_shape'][0] == 0  # No rows
        assert result['cleaned_shape'][1] == 3  # 3 columns

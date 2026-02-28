"""
Tests for export_processing_metadata module
"""

import pytest
import pandas as pd
import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from export_processing_metadata import export_processing_metadata


class TestExportProcessingMetadata:
    """Tests for metadata export function."""
    
    def test_export_metadata(self, sample_csv_clean, output_dir):
        """Test basic metadata export."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        assert result['success'] is True
        assert os.path.exists(result['output_file'])
        assert result['output_file'].endswith('_metadata.json')
    
    def test_metadata_structure(self, sample_csv_clean, output_dir):
        """Test that metadata has correct structure."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        # Check main sections
        assert 'processing_info' in metadata
        assert 'file_info' in metadata
        assert 'data_structure' in metadata
        assert 'data_profile' in metadata
        assert 'column_profiles' in metadata
    
    def test_metadata_processing_info(self, sample_csv_clean, output_dir):
        """Test processing info section."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        proc_info = metadata['processing_info']
        assert 'timestamp' in proc_info
        assert 'processor' in proc_info
        assert 'version' in proc_info
    
    def test_metadata_file_info(self, sample_csv_clean, output_dir):
        """Test file info section."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        file_info = metadata['file_info']
        assert 'filename' in file_info
        assert 'filepath' in file_info
        assert 'size_bytes' in file_info
        assert 'size_mb' in file_info
        assert file_info['size_bytes'] > 0
    
    def test_metadata_data_structure(self, sample_csv_clean, output_dir):
        """Test data structure section."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        structure = metadata['data_structure']
        assert 'total_rows' in structure
        assert 'total_columns' in structure
        assert 'column_names' in structure
        assert 'column_types' in structure
        assert structure['total_rows'] > 0
        assert len(structure['column_names']) == structure['total_columns']
    
    def test_metadata_data_profile(self, sample_csv_clean, output_dir):
        """Test data profile section."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        profile = metadata['data_profile']
        assert 'total_cells' in profile
        assert 'populated_cells' in profile
        assert 'empty_cells' in profile
        assert 'data_density_percentage' in profile
        assert 'duplicate_rows' in profile
        assert 'unique_rows' in profile
        assert profile['data_density_percentage'] >= 0
        assert profile['data_density_percentage'] <= 100
    
    def test_metadata_column_profiles(self, sample_csv_clean, output_dir):
        """Test column profiles section."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        col_profiles = metadata['column_profiles']
        assert len(col_profiles) > 0
        
        # Check first column profile
        first_col = list(col_profiles.values())[0]
        assert 'data_type' in first_col
        assert 'non_null_count' in first_col
        assert 'null_count' in first_col
        assert 'unique_count' in first_col
        assert 'sample_values' in first_col
    
    def test_metadata_return_values(self, sample_csv_clean, output_dir):
        """Test that function returns correct values."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        assert 'input_file' in result
        assert 'output_file' in result
        assert 'metadata' in result
        assert 'success' in result
        assert result['success'] is True
    
    def test_metadata_invalid_file(self, output_dir):
        """Test handling of invalid file path."""
        with pytest.raises(FileNotFoundError):
            export_processing_metadata('non_existent.csv', output_dir, verbose=False)
    
    def test_metadata_valid_json(self, sample_csv_clean, output_dir):
        """Test that generated file is valid JSON."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        # Should not raise exception
        with open(result['output_file'], 'r') as f:
            json.load(f)
    
    def test_metadata_sample_values(self, sample_csv_clean, output_dir):
        """Test that sample values are included for columns."""
        result = export_processing_metadata(sample_csv_clean, output_dir, verbose=False)
        
        with open(result['output_file'], 'r') as f:
            metadata = json.load(f)
        
        col_profiles = metadata['column_profiles']
        for col_data in col_profiles.values():
            assert isinstance(col_data['sample_values'], list)
            assert len(col_data['sample_values']) <= 3

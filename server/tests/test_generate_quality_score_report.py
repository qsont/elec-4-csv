"""
Tests for generate_quality_score_report module
"""

import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from generate_quality_score_report import (
    generate_quality_score_report,
    calculate_quality_score,
    get_quality_grade
)


class TestGetQualityGrade:
    """Tests for quality grade conversion function."""
    
    def test_grade_a_plus(self):
        """Test A+ grade for excellent scores."""
        assert get_quality_grade(97) == 'A+ (Excellent)'
    
    def test_grade_a(self):
        """Test A grade for very good scores."""
        assert get_quality_grade(92) == 'A (Very Good)'
    
    def test_grade_b_plus(self):
        """Test B+ grade for good scores."""
        assert get_quality_grade(87) == 'B+ (Good)'
    
    def test_grade_b(self):
        """Test B grade for above average scores."""
        assert get_quality_grade(82) == 'B (Above Average)'
    
    def test_grade_c(self):
        """Test C grade for average scores."""
        assert get_quality_grade(75) == 'C (Average)'
    
    def test_grade_d(self):
        """Test D grade for below average scores."""
        assert get_quality_grade(65) == 'D (Below Average)'
    
    def test_grade_f(self):
        """Test F grade for poor scores."""
        assert get_quality_grade(50) == 'F (Poor)'


class TestCalculateQualityScore:
    """Tests for quality score calculation function."""
    
    def test_calculate_perfect_quality(self):
        """Test quality score for perfect data."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [10, 20, 30, 40, 50]
        })
        
        result = calculate_quality_score(df)
        
        assert result['completeness_score'] == 100.0
        assert result['uniqueness_score'] == 100.0
        assert result['overall_score'] > 90
    
    def test_calculate_quality_with_missing(self):
        """Test quality score with missing values."""
        df = pd.DataFrame({
            'A': [1, None, 3, None, 5],
            'B': ['a', 'b', None, 'd', 'e']
        })
        
        result = calculate_quality_score(df)
        
        assert result['completeness_score'] < 100.0
        assert result['completeness_score'] > 0
    
    def test_calculate_quality_with_duplicates(self):
        """Test quality score with duplicate rows."""
        df = pd.DataFrame({
            'A': [1, 2, 1, 3],
            'B': ['a', 'b', 'a', 'c']
        })
        
        result = calculate_quality_score(df)
        
        assert result['uniqueness_score'] < 100.0
    
    def test_quality_score_structure(self):
        """Test that quality score has all required fields."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        result = calculate_quality_score(df)
        
        assert 'overall_score' in result
        assert 'completeness_score' in result
        assert 'uniqueness_score' in result
        assert 'validity_score' in result
        assert 'consistency_score' in result
        assert 'grade' in result
        assert 'details' in result


class TestGenerateQualityScoreReport:
    """Tests for quality score report generation function."""
    
    def test_generate_quality_report(self, sample_csv_clean, output_dir):
        """Test basic quality report generation."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        assert result['success'] is True
        assert os.path.exists(result['output_file'])
        assert result['output_file'].endswith('_quality_report.csv')
    
    def test_quality_report_content(self, sample_csv_clean, output_dir):
        """Test that quality report contains expected metrics."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        report_df = pd.read_csv(result['output_file'])
        
        # Check required columns
        assert 'Metric' in report_df.columns
        assert 'Score' in report_df.columns
        assert 'Grade' in report_df.columns
        
        # Check required metrics
        metrics = report_df['Metric'].tolist()
        assert 'Overall Quality Score' in metrics
        assert 'Completeness' in metrics
        assert 'Uniqueness' in metrics
        assert 'Validity' in metrics
        assert 'Consistency' in metrics
    
    def test_quality_report_metrics_returned(self, sample_csv_clean, output_dir):
        """Test that quality metrics are returned."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        metrics = result['quality_metrics']
        
        assert 'overall_score' in metrics
        assert 'completeness_score' in metrics
        assert 'uniqueness_score' in metrics
        assert 'grade' in metrics
        assert metrics['overall_score'] >= 0
        assert metrics['overall_score'] <= 100
    
    def test_quality_report_messy_data(self, sample_csv_messy, output_dir):
        """Test quality report for messy data."""
        result = generate_quality_score_report(sample_csv_messy, output_dir, verbose=False)
        
        metrics = result['quality_metrics']
        
        # Messy data should have lower scores
        assert metrics['completeness_score'] < 100
        assert metrics['uniqueness_score'] < 100
    
    def test_quality_report_clean_data(self, sample_csv_clean, output_dir):
        """Test quality report for clean data."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        metrics = result['quality_metrics']
        
        # Clean data should have high scores
        assert metrics['completeness_score'] == 100
        assert metrics['uniqueness_score'] == 100
    
    def test_quality_report_invalid_file(self, output_dir):
        """Test handling of invalid file path."""
        with pytest.raises(FileNotFoundError):
            generate_quality_score_report('non_existent.csv', output_dir, verbose=False)
    
    def test_quality_report_grade_assignment(self, sample_csv_clean, output_dir):
        """Test that grades are correctly assigned."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        report_df = pd.read_csv(result['output_file'])
        
        # All grades should be non-empty
        for grade in report_df['Grade']:
            assert grade != ''
            assert isinstance(grade, str)
    
    def test_quality_report_details(self, sample_csv_clean, output_dir):
        """Test that quality details are included."""
        result = generate_quality_score_report(sample_csv_clean, output_dir, verbose=False)
        
        details = result['quality_metrics']['details']
        
        assert 'total_cells' in details
        assert 'missing_cells' in details
        assert 'duplicate_rows' in details
        assert details['total_cells'] > 0

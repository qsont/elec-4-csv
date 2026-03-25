import pytest
import pandas as pd
import os
import tempfile
import shutil

"""
PyTest Configuration and Shared Fixtures
"""

@pytest.fixture(scope="session")
def input_csv_files():
    """List all CSV files in the input folder for testing."""
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../input'))
    csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]
    return csv_files

@pytest.fixture(scope="session")
def input_csv_count(input_csv_files):
    """Return the number of CSV files in the input folder."""
    return len(input_csv_files)
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_csv_clean(temp_dir):
    """Create a clean sample CSV file for testing."""
    csv_path = os.path.join(temp_dir, 'test_clean.csv')
    data = {
        'Name': ['John Doe', 'Jane Smith', 'Bob Jones', 'Alice Brown', 'Charlie Davis'],
        'Email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
        'Age': [30, 25, 35, 28, 42],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'Status': ['Active', 'Active', 'Inactive', 'Active', 'Active']
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_csv_messy(temp_dir):
    """Create a messy CSV file with data quality issues for testing."""
    csv_path = os.path.join(temp_dir, 'test_messy.csv')
    data = {
        'Name ': ['John Doe', 'Jane Smith', '', 'Alice Brown', 'John Doe', '  ', 'Charlie Davis', None],
        'Email Address': ['john@example.com', 'jane@example.com', None, 'alice@example.com', 'john@example.com', 'invalid-email', 'charlie@', ''],
        'Phone #': ['555-1234', '555-5678', '', '555-9999', '555-1234', None, '555-1111', '123'],
        'Date Joined': ['01/15/2023', '2023-02-20', '', '2023-04-05', '01/15/2023', None, '05-15-2023', 'invalid'],
        'Salary': [50000, 60000, None, 70000, 50000, None, 80000, 90000]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_csv_with_duplicates(temp_dir):
    """Create a CSV file with duplicate rows."""
    csv_path = os.path.join(temp_dir, 'test_duplicates.csv')
    data = {
        'ID': [1, 2, 3, 1, 4, 2],
        'Name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David', 'Bob'],
        'Value': [100, 200, 300, 100, 400, 200]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_csv_empty(temp_dir):
    """Create an empty CSV file (only headers)."""
    csv_path = os.path.join(temp_dir, 'test_empty.csv')
    data = pd.DataFrame(columns=['Col1', 'Col2', 'Col3'])
    data.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def output_dir(temp_dir):
    """Create output directory for test results."""
    out_dir = os.path.join(temp_dir, 'output')
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


@pytest.fixture
def sys_path_setup():
    """Add src directory to Python path for imports."""
    import sys
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    yield
    if src_path in sys.path:
        sys.path.remove(src_path)

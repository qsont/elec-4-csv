# Quick Start Guide

## Run the Pipeline

### Process a single CSV file:
```bash
cd server/src
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python pipeline.py ../input/your-file.csv
```

### Process all CSV files in a directory:
```bash
python pipeline.py --dir ../input
```

## What Gets Generated

For each CSV file, you get 5 output files:

1. **`*_cleaned.csv`** - Cleaned data
   - Duplicates removed
   - Missing values filled
   - Whitespace trimmed
   - Data validated

2. **`*_summary_report.csv`** - Statistics per column
   - Data types
   - Missing value counts
   - Unique values
   - Min/Max/Mean (for numeric columns)

3. **`*_report.json`** - Comprehensive analysis
   - Detailed column statistics
   - Top values for categorical data
   - Sample data preview
   - Data quality metrics

4. **`*_quality_report.csv`** - Quality scores
   - Overall quality grade
   - Completeness score
   - Uniqueness score
   - Validity score
   - Consistency score

5. **`*_metadata.json`** - File metadata
   - File size and timestamps
   - Column structure
   - Memory usage
   - Data profile

## GitHub Actions Setup

1. **Commit your workflow file** (already created at `.github/workflows/csv-pipeline.yml`)

2. **Push CSV files** to `server/input/` directory

3. **Automatic processing** triggers on:
   - Push to main/develop
   - Pull requests
   - Manual workflow dispatch

4. **Download results** from Actions -> Artifacts

## Command Line Arguments

```bash
# Single file with custom output
python pipeline.py path/to/file.csv --output path/to/output

# Directory processing with custom output
python pipeline.py --dir path/to/input --output path/to/output

# Default test run (uses csv-cleaner-example.csv)
python pipeline.py
```

## Individual Functions

Use any function standalone:

```bash
# 1. Clean CSV
python generate_cleaned_output_csv.py ../input/file.csv

# 2. Summary report
python generate_summary_report_csv.py ../input/file.csv

# 3. JSON report
python generate_json_report.py ../input/file.csv

# 4. Quality score
python generate_quality_score_report.py ../input/file.csv

# 5. Metadata
python export_processing_metadata.py ../input/file.csv
```

## Python API Usage

```python
# Import functions
from pipeline import run_pipeline

# Run complete pipeline
results = run_pipeline('path/to/file.csv')

# Check results
print(f"Quality Score: {results['steps']['quality']['quality_metrics']['overall_score']}%")
print(f"Duplicates Removed: {results['steps']['cleaning']['duplicates_removed']}")
print(f"Cleaned File: {results['steps']['cleaning']['output_file']}")
```

## Customization

### Change missing value strategy
Edit `generate_cleaned_output_csv.py` line ~129:
```python
if col_type == 'numeric':
    df[col] = df[col].fillna(0)  # Change to median: df[col].fillna(df[col].median())
```

### Adjust quality score weights
Edit `generate_quality_score_report.py` line ~31:
```python
weights = {
    'completeness': 0.35,   # Customize these
    'uniqueness': 0.25,
    'validity': 0.25,
    'consistency': 0.15
}
```

## Troubleshooting

**Problem**: Module not found
```bash
# Solution: Install dependencies
pip install pandas numpy
```

**Problem**: File not found
```bash
# Solution: Use correct relative path
cd server/src
python pipeline.py ../input/file.csv  # Note the ../
```

**Problem**: Virtual environment not activated
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

## Next Steps

1. ✅ Place your CSV files in `server/input/`
2. ✅ Run the pipeline locally to test
3. ✅ Push to GitHub to trigger automatic processing
4. ✅ Download results from GitHub Actions artifacts
5. ✅ Customize cleaning strategies as needed

## Example Output

**Quality Report:**
```
Metric                    Score    Grade
Overall Quality Score     82.0%    B (Above Average)
Completeness             70.0%    C (Average)
Uniqueness               75.0%    C (Average)
Validity                 95.0%    A+ (Excellent)
Consistency             100.0%    A+ (Excellent)
```

**Summary Statistics:**
```
Column          Data Type  Non-Null  Null  Unique
Name            str        95        5     87
Email Address   str        98        2     98
Phone #         str        92        8     85
Date Joined     date       100       0     45
Status          str        100       0     3
```

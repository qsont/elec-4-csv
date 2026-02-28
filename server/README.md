# CSV Data Processing Pipeline

A comprehensive, dynamic CSV data cleaning and analysis pipeline designed for CI/CD environments like GitHub Actions.

## Features

- **Dynamic Column Detection**: Automatically infers column types (email, phone, date, numeric, categorical) without hardcoding
- **Data Cleaning**: Removes duplicates, handles missing values, trims whitespace, validates data formats
- **Multiple Report Formats**: Generates cleaned CSV, summary reports, JSON reports, quality scores, and metadata
- **CI/CD Ready**: Designed to run automatically in GitHub Actions on push/pull requests
- **Batch Processing**: Can process single files or entire directories

## Project Structure

```
server/
├── input/                          # Place your CSV files here
│   ├── customers-100.csv
│   └── csv-cleaner-example.csv
├── output/                         # Generated reports and cleaned files
├── src/                            # Source code
│   ├── generate_cleaned_output_csv.py      # [1] CSV cleaning module
│   ├── generate_summary_report_csv.py      # [2] Summary statistics
│   ├── generate_json_report.py             # [3] JSON report generator
│   ├── generate_quality_score_report.py    # [4] Data quality scoring
│   ├── export_processing_metadata.py       # [5] Metadata extraction
│   └── pipeline.py                         # Main orchestrator
└── tests/                          # Unit tests (to be added)
```

## Installation

### Local Development

1. **Set up virtual environment:**
   ```bash
   cd server/src
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install pandas numpy
   ```

### GitHub Actions

No installation needed - the workflow automatically sets up Python and installs dependencies.

## Usage

### 1. Process a Single CSV File

```bash
cd server/src
python pipeline.py ../input/your-file.csv
```

### 2. Process All CSV Files in a Directory

```bash
python pipeline.py --dir ../input
```

### 3. Specify Custom Output Directory

```bash
python pipeline.py ../input/file.csv --output ../custom-output
```

### 4. Run Individual Functions

Each function can be used standalone:

```bash
# Clean CSV only
python generate_cleaned_output_csv.py ../input/file.csv

# Generate quality report only
python generate_quality_score_report.py ../input/file.csv

# Export metadata only
python export_processing_metadata.py ../input/file.csv
```

### 5. Use as Python Module

```python
from generate_cleaned_output_csv import generate_cleaned_output_csv
from generate_quality_score_report import generate_quality_score_report

# Clean a CSV and get metadata
result = generate_cleaned_output_csv('path/to/file.csv')
print(f"Cleaned {result['duplicates_removed']} duplicates")

# Get quality score
quality = generate_quality_score_report('path/to/file.csv')
print(f"Quality Score: {quality['quality_metrics']['overall_score']}%")
```

## Output Files

For each input CSV file, the pipeline generates:

| File | Description |
|------|-------------|
| `*_cleaned.csv` | Cleaned CSV with duplicates removed, missing values filled |
| `*_summary_report.csv` | Column-by-column statistics and data types |
| `*_report.json` | Comprehensive JSON report with detailed analysis |
| `*_quality_report.csv` | Data quality scores (completeness, uniqueness, validity, consistency) |
| `*_metadata.json` | File metadata, structure info, and processing details |

## Data Cleaning Features

### 1. Missing Values Handling
- **Numeric columns**: Filled with `0`
- **Categorical columns**: Filled with `"Unknown"`
- **Email/Phone columns**: Filled with `"Not Provided"`
- **Date columns**: Left as `NaT` (can be configured to drop rows)

### 2. Duplicate Removal
- Identifies duplicate rows
- Keeps first occurrence, removes subsequent duplicates

### 3. Whitespace Trimming
- Trims leading/trailing spaces from column names
- Trims spaces from all string values

### 4. Data Type Validation
- **Email validation**: Checks format with regex pattern
- **Phone validation**: Ensures proper formatting
- **Date standardization**: Converts various date formats to ISO format

### 5. Column Type Inference
Automatically detects column types based on:
- Column name keywords
- Value patterns using regex
- Statistical analysis of content

## Quality Score Metrics

The quality report calculates:

- **Completeness** (35% weight): Percentage of non-missing data
- **Uniqueness** (25% weight): Percentage of non-duplicate rows
- **Validity** (25% weight): Data format correctness
- **Consistency** (15% weight): Formatting consistency within columns

**Overall Score**: Weighted average of all metrics

| Score | Grade |
|-------|-------|
| 95-100% | A+ (Excellent) |
| 90-94% | A (Very Good) |
| 85-89% | B+ (Good) |
| 80-84% | B (Above Average) |
| 70-79% | C (Average) |
| 60-69% | D (Below Average) |
| <60% | F (Poor) |

## GitHub Actions Integration

### Automatic Triggers

The pipeline runs automatically on:
- **Push** to `main` or `develop` branches (when CSV files or Python code changes)
- **Pull requests** to `main` branch
- **Manual trigger** via workflow dispatch

### Workflow Configuration

Located at: `.github/workflows/csv-pipeline.yml`

Features:
- Python 3.11 environment
- Automatic dependency installation
- Processes all CSV files in `server/input/`
- Uploads results as artifacts (retained for 30 days)
- Creates issues on pipeline failures
- Generates summary in GitHub Actions UI

### Manual Run

1. Go to **Actions** tab in GitHub
2. Select **CSV Processing Pipeline**
3. Click **Run workflow**
4. Optionally specify a CSV file or process all files

## Configuration

### Modify Missing Value Strategy

Edit the `generate_cleaned_output_csv.py` file:

```python
# In the HANDLE MISSING VALUES section
if col_type == 'numeric':
    df[col] = df[col].fillna(0)  # Change 0 to df[col].median() for median imputation
```

### Adjust Quality Score Weights

Edit `generate_quality_score_report.py`:

```python
weights = {
    'completeness': 0.35,  # Adjust these weights
    'uniqueness': 0.25,
    'validity': 0.25,
    'consistency': 0.15
}
```

### Add Custom Column Type Detection

Edit the `infer_column_type()` function in `generate_cleaned_output_csv.py`:

```python
# Add custom keywords
custom_keywords = ['your', 'custom', 'keywords']
if any(keyword in col_lower for keyword in custom_keywords):
    return 'custom_type'
```

## Testing

```bash
cd server/src

# Test with example file
python pipeline.py ../input/csv-cleaner-example.csv

# Test with production file
python pipeline.py ../input/customers-100.csv

# Test batch processing
python pipeline.py --dir ../input
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution**: Activate virtual environment and install dependencies
```bash
.\venv\Scripts\Activate.ps1
pip install pandas numpy
```

### Issue: "FileNotFoundError: CSV file not found"
**Solution**: Check file path is correct and relative to current directory
```bash
# Use absolute path or ensure you're in server/src/
python pipeline.py "C:\full\path\to\file.csv"
```

### Issue: Pipeline runs but no output files generated
**Solution**: Check output directory permissions
```bash
mkdir -p ../output
chmod 755 ../output  # Linux/Mac
```

## Future Enhancements

- [ ] Add unit tests with pytest
- [ ] Support for Excel files (.xlsx)
- [ ] Database export functionality
- [ ] Data visualization reports (charts/graphs)
- [ ] Email notifications on completion
- [ ] Parallel processing for large files
- [ ] Custom validation rules via config file
- [ ] Data profiling and anomaly detection

## Contributing

1. Place test CSV files in `server/input/`
2. Run pipeline locally to verify
3. Commit changes and create pull request
4. GitHub Actions will automatically process the files

## License

MIT License

## Support

For issues or questions, please create an issue in the GitHub repository.

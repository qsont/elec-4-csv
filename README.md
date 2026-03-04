# CSV Data Processing Pipeline

A comprehensive, dynamic CSV data cleaning and analysis pipeline designed for both local development and CI/CD environments like GitHub Actions.

## 📋 Overview

This project provides an automated pipeline for cleaning, validating, and analyzing CSV files. It dynamically detects column types (email, phone, date, numeric, categorical) without hardcoding and generates multiple report formats including cleaned CSV files, summary statistics, JSON reports, and quality scores.

## 🗂️ Project Structure

```
elec-4-csv/
├── README.md                          # This file
├── QUICK_START.md                     # Quick setup and usage guide
├── GITHUB_ACTIONS_SETUP.md            # CI/CD setup instructions
└── server/                            # Main project directory
    ├── src/                           # Python source code
    │   ├── pipeline.py                # Main orchestrator
    │   ├── generate_cleaned_output_csv.py      # CSV cleaning module
    │   ├── generate_summary_report_csv.py      # Summary statistics generator
    │   ├── generate_json_report.py             # JSON report generator
    │   ├── generate_quality_score_report.py    # Data quality scorer
    │   └── export_processing_metadata.py       # Metadata extractor
    ├── input/                         # CSV input files
    ├── output/                        # Generated reports and cleaned files
    ├── tests/                         # Unit test suite (86 tests)
    ├── htmlcov/                       # Code coverage reports
    ├── pyproject.toml                 # Pytest and coverage configuration
    ├── requirements.txt               # Python dependencies
    └── README.md                      # Detailed project documentation
```

## ⚡ Quick Start

### 1. Set Up Python Environment

```bash
cd server
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline

```bash
cd src

# Process a single CSV file
python pipeline.py ../input/your-file.csv

# Process all CSV files in the input directory
python pipeline.py --dir ../input

# Specify custom output directory
python pipeline.py ../input/file.csv --output ../custom-output
```

## 🎯 Key Features

### Dynamic Column Detection
- Automatically infers column types without hardcoding
- Detects: email, phone, date, numeric, and categorical columns
- Uses intelligent regex patterns and statistical analysis

### Data Cleaning
- **Duplicate Removal**: Identifies and removes duplicate rows
- **Missing Value Handling**: Smart imputation based on column type
- **Whitespace Trimming**: Cleans spaces from column names and values
- **Data Validation**: Validates email, phone, and date formats

### Multiple Report Formats
- **`*_cleaned.csv`** - Cleaned and validated data
- **`*_summary_report.csv`** - Column-by-column statistics
- **`*_report.json`** - Comprehensive analysis in JSON format
- **`*_quality_report.csv`** - Data quality scores and metrics
- **`*_metadata.json`** - File metadata and processing details

### Quality Metrics
The pipeline calculates data quality using four weighted metrics:
- **Completeness** (35%): Percentage of non-missing data
- **Uniqueness** (25%): Absence of duplicate rows
- **Validity** (25%): Data format correctness
- **Consistency** (15%): Formatting consistency

Letter grades assigned: A+ (95-100%), A (90-94%), B+ (85-89%), B (80-84%), C (70-79%), D (60-69%), F (<60%)

### CI/CD Ready
- GitHub Actions workflow included
- Automatic triggers on push, pull requests, and manual dispatch
- Batch processing of multiple CSV files
- Automatic artifact generation and upload

## 📦 Dependencies

- **pandas** (≥2.0.0): Data manipulation and analysis
- **numpy** (≥1.24.0): Numerical computing
- **pytest** (≥7.0.0): Unit testing framework
- **pytest-cov** (≥4.0.0): Code coverage reporting

## 🧪 Testing

The project includes a comprehensive test suite with 86 tests:

```bash
cd server

# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_pipeline.py

# View HTML coverage report
# Open htmlcov/index.html in a browser
```

## 🔧 Configuration

### Modify Missing Value Strategy
Edit `src/generate_cleaned_output_csv.py` to change how missing values are handled.

### Adjust Quality Score Weights
Edit `src/generate_quality_score_report.py` to modify the weights of quality metrics.

### Add Custom Column Type Detection
Extend the `infer_column_type()` function in `src/generate_cleaned_output_csv.py`.

## 🚀 GitHub Actions Integration

The project includes automated CI/CD with GitHub Actions:

### Automatic Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Manual trigger via workflow dispatch

### Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **CSV Processing Pipeline**
3. Click **Run workflow**
4. Optionally specify a CSV file

All results are uploaded as artifacts (retained for 30 days).

## 📚 Detailed Documentation

For complete documentation, refer to:

- **[server/README.md](server/README.md)** - Comprehensive project documentation with detailed sections on features, configuration, and troubleshooting
- **[QUICK_START.md](QUICK_START.md)** - Quick setup and usage guide
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** - GitHub Actions setup and automation guide

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'pandas'
```bash
# Activate virtual environment and install dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### FileNotFoundError: CSV file not found
Check that the file path is correct and relative to the `src/` directory.

### No output files generated
Verify output directory permissions and ensure the directory exists.

## 🔮 Future Enhancements

- [ ] Support for Excel files (.xlsx)
- [ ] Database export functionality
- [ ] Data visualization reports (charts/graphs)
- [ ] Email notifications on completion
- [ ] Parallel processing for large files
- [ ] Custom validation rules via config file
- [ ] Data profiling and anomaly detection

## 🤝 Contributing

1. Clone the repository
2. Create a feature branch
3. Make your changes and test locally
4. Commit with clear messages
5. Push and create a pull request
6. GitHub Actions will automatically validate your changes

## 📄 License

MIT License

## 💬 Support

For issues or questions, please create an issue in the GitHub repository.

---

**Last Updated**: March 2026

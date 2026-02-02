# Portfolio Report Generator

A professional portfolio report generator that creates client-ready PDF reports from CSV files containing investment holdings data.

## Features

- **Professional PDF Reports**: Generate beautifully formatted, client-ready portfolio reports
- **Comprehensive Analytics**: Automatic calculation of market values, gains/losses, and returns
- **Flexible CSV Input**: Support for multiple CSV formats with optional client metadata
- **Detailed Holdings Table**: Complete breakdown of each position with performance metrics
- **Portfolio Summary**: At-a-glance overview of total portfolio performance
- **Color-Coded Returns**: Visual indication of positive and negative performance

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd report-builder
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- reportlab (PDF generation)
- pandas (CSV parsing and data manipulation)
- python-dateutil (date handling)
- Pillow (image support)

## Quick Start

Generate a sample report using the included example data:

```bash
python3 generate_report.py data/client_portfolio.csv
```

The report will be saved to `output/portfolio_report_YYYYMMDD_HHMMSS.pdf`

## CSV File Format

The tool supports two CSV formats:

### Format 1: With Client Metadata (Recommended)

```csv
client_name,account_number,report_date
John Smith,ACC-2024-1234,2024-01-31
Symbol,Name,Quantity,Price,Cost Basis
AAPL,Apple Inc.,150,185.50,142.30
MSFT,Microsoft Corporation,200,380.75,295.60
GOOGL,Alphabet Inc. Class A,75,142.85,118.90
```

### Format 2: Simple Holdings Only

```csv
Symbol,Name,Quantity,Price,Cost Basis
AAPL,Apple Inc.,150,185.50,142.30
MSFT,Microsoft Corporation,200,380.75,295.60
GOOGL,Alphabet Inc. Class A,75,142.85,118.90
```

### Required Columns

- **Symbol**: Stock ticker symbol (e.g., AAPL, MSFT)
- **Name**: Full company name
- **Quantity**: Number of shares held
- **Price**: Current price per share
- **Cost Basis**: Original purchase price per share

## Usage

### Basic Usage

```bash
python3 generate_report.py <input_csv_file>
```

### Advanced Options

```bash
python3 generate_report.py data/holdings.csv \
  -o custom_report.pdf \
  -c "Jane Doe" \
  -a "ACC-2024-5678"
```

### Command Line Arguments

- `input_file`: Path to the CSV file containing portfolio holdings (required)
- `-o, --output`: Custom output PDF file path (default: `output/portfolio_report_YYYYMMDD_HHMMSS.pdf`)
- `-c, --client`: Client name (overrides CSV metadata if provided)
- `-a, --account`: Account number (overrides CSV metadata if provided)

### Examples

```bash
# Generate report with default settings
python3 generate_report.py data/my_portfolio.csv

# Specify custom output location
python3 generate_report.py data/my_portfolio.csv -o reports/q1_2024.pdf

# Override client information
python3 generate_report.py data/holdings.csv -c "John Smith" -a "ACC-123456"
```

## Report Contents

Each generated PDF report includes:

### 1. Header Section
- Report title
- Client name
- Account number
- Report date

### 2. Portfolio Summary
- Total market value
- Total cost basis
- Total gain/loss ($ and %)
- Number of holdings

### 3. Holdings Detail Table
For each holding:
- Symbol and company name
- Quantity of shares
- Current price
- Market value
- Cost basis
- Gain/loss ($ and %)
- Color-coded performance indicators

### 4. Footer
- Disclaimer text
- Report generation timestamp

## Sample Output

The generated PDF features:

- Professional typography and layout
- Color-coded gains (green) and losses (red)
- Alternating row colors for easy reading
- Proper currency and percentage formatting
- Summary metrics highlighted in gray
- Clean, modern design suitable for client presentations

## Project Structure

```
report-builder/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── portfolio.py          # Data models and CSV parser
│   └── report_generator.py   # PDF report generation
├── data/
│   ├── sample_holdings.csv   # Simple example data
│   └── client_portfolio.csv  # Full example with metadata
├── output/
│   └── .gitkeep             # Generated PDFs saved here
├── tests/                    # Test files (future)
├── generate_report.py        # Main CLI script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Customization

### Modifying Report Styling

Edit `src/report_generator.py` to customize:

- Color scheme (search for `HexColor` values)
- Font sizes and families
- Table layouts and column widths
- Page margins and spacing
- Header and footer content

### Adding Custom Calculations

Extend the `Holding` or `Portfolio` classes in `src/portfolio.py` to add:

- Additional metrics (e.g., dividend yield, sector allocation)
- Custom aggregations
- Performance benchmarks

## Best Practices

1. **Data Accuracy**: Ensure your CSV data is current and accurate
2. **Consistent Formatting**: Use consistent date formats (YYYY-MM-DD recommended)
3. **Backup Reports**: Save generated PDFs with descriptive names
4. **Version Control**: Keep CSV source files under version control
5. **Regular Updates**: Generate reports on a consistent schedule (monthly, quarterly)

## Troubleshooting

### Common Issues

**"File not found" error:**
- Verify the CSV file path is correct
- Use absolute paths if relative paths aren't working

**"Error tokenizing data" or parsing errors:**
- Check CSV format matches one of the supported formats
- Ensure no extra commas or special characters
- Verify all required columns are present

**Missing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**Permission errors on output directory:**
```bash
mkdir -p output
chmod 755 output
```

## License

This project is provided as-is for portfolio reporting purposes.

## Contributing

Contributions are welcome! Areas for enhancement:

- Additional chart types (pie charts, performance graphs)
- Multiple currency support
- Sector allocation analysis
- Comparison reports (month-over-month, year-over-year)
- Email delivery integration
- Web interface

## Support

For issues or questions, please check the existing documentation or create an issue in the repository.

---

**Generated reports are for informational purposes only and should not be considered as investment advice.**

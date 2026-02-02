#!/usr/bin/env python3
"""Main script to generate portfolio reports from CSV files."""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from src import parse_csv, PortfolioReportGenerator


def main():
    """Main entry point for the report generator."""
    parser = argparse.ArgumentParser(
        description='Generate professional portfolio reports from CSV files'
    )
    parser.add_argument(
        'input_file',
        help='Path to the CSV file containing portfolio holdings'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (default: output/portfolio_report_YYYYMMDD.pdf)',
        default=None
    )
    parser.add_argument(
        '-c', '--client',
        help='Client name (overrides CSV if provided)',
        default=None
    )
    parser.add_argument(
        '-a', '--account',
        help='Account number (overrides CSV if provided)',
        default=None
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path('output') / f'portfolio_report_{timestamp}.pdf'

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Parse the CSV file
        print(f"Reading holdings from: {input_path}")
        portfolio = parse_csv(str(input_path))

        # Override client info if provided
        if args.client:
            portfolio.client_name = args.client
        if args.account:
            portfolio.account_number = args.account

        # Display portfolio summary
        print(f"\nPortfolio Summary:")
        print(f"  Client: {portfolio.client_name}")
        print(f"  Account: {portfolio.account_number}")
        print(f"  Holdings: {len(portfolio.holdings)}")
        print(f"  Total Market Value: ${portfolio.total_market_value:,.2f}")
        print(f"  Total Cost Basis: ${portfolio.total_cost_basis:,.2f}")
        print(f"  Total Gain/Loss: ${portfolio.total_gain_loss:,.2f} "
              f"({portfolio.total_gain_loss_percent:+.2f}%)")

        # Generate the PDF report
        print(f"\nGenerating PDF report...")
        generator = PortfolioReportGenerator(portfolio)
        generator.generate(str(output_path))

        print(f"\nSuccess! Report saved to: {output_path}")

    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

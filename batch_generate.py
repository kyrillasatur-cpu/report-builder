#!/usr/bin/env python3
"""Batch generate reports for multiple clients.

Reads all CSV files from a folder and generates an HTML report for each one.

Usage:
    # Generate reports for all clients in data/clients/
    python batch_generate.py data/clients/

    # Generate from anonymized data (for testing)
    python batch_generate.py data/anonymized/

    # Specify output folder and quarter
    python batch_generate.py data/clients/ -o reports/Q1_2026/ --quarter "Q1 2026"

    # Generate a single client report
    python batch_generate.py data/clients/smith_family.csv --client "Smith Family"
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Add src to path so we can import the existing modules
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from data_processor import load_branding, process_portfolio
from chart_builder import build_allocation_bar_chart


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CATEGORIES = PROJECT_ROOT / "config" / "categories.json"
DEFAULT_BRANDING = PROJECT_ROOT / "config" / "branding.json"
DEFAULT_TEMPLATE_DIR = PROJECT_ROOT / "templates"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def read_client_name_from_csv(csv_path: str) -> str:
    """Try to read a client name from the CSV metadata header.

    If the CSV starts with 'client_name,...' (metadata format), return the
    client name from row 2. Otherwise return None.
    """
    with open(csv_path, "r") as f:
        first_line = f.readline().strip()
        if first_line.lower().startswith("client_name"):
            second_line = f.readline().strip()
            parts = second_line.split(",")
            if parts:
                return parts[0]
    return None


def build_report_context(portfolio_data, branding, chart_svg, client_name, quarter, report_date):
    """Assemble the template context for a single client report."""
    company = branding["company"]
    colors = branding["colors"]
    fonts = branding["fonts"]

    notable_events = [
        "<strong>Digital Assets:</strong> Bitcoin ETF holdings (IBIT, FBTC) added to Alternative allocation, reflecting growing institutional adoption of digital asset exposure.",
        "<strong>Gold & Silver:</strong> Precious metals allocation maintained as inflation hedge, with GLD and SLV providing commodity diversification.",
        "<strong>Fixed Income:</strong> Bond allocation (BND, AGG, SHV) positioned for rate environment with mix of aggregate and short-duration exposure.",
        "<strong>Real Estate:</strong> REIT positions (VNQ, SCHH) provide real asset exposure and income generation within the Alternative sleeve.",
    ]

    performance_highlights = [
        {"label": "Core Allocation", "value": f"{portfolio_data.core_allocation.weight:.1f}%"},
        {"label": "Alternative Allocation", "value": f"{portfolio_data.alternative_allocation.weight:.1f}%"},
        {"label": "Total Holdings", "value": str(len(portfolio_data.holdings))},
        {"label": "Asset Categories", "value": str(
            len(portfolio_data.core_subcategories) + len(portfolio_data.alternative_subcategories)
        )},
    ]

    return {
        "company": company,
        "colors": colors,
        "fonts": fonts,
        "quarter": quarter,
        "report_date": report_date,
        "client_name": client_name,
        "total_market_value": portfolio_data.total_market_value,
        "core_weight": portfolio_data.core_allocation.weight,
        "alt_weight": portfolio_data.alternative_allocation.weight,
        "num_holdings": len(portfolio_data.holdings),
        "chart_svg": chart_svg,
        "core_subcategories": portfolio_data.core_subcategories,
        "alternative_subcategories": portfolio_data.alternative_subcategories,
        "notable_events": notable_events,
        "performance_highlights": performance_highlights,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def generate_single_report(csv_path, output_path, client_name, quarter, report_date, categories_path, branding_path, template_dir):
    """Generate one HTML report from a single client CSV."""
    portfolio_data = process_portfolio(str(csv_path), str(categories_path))
    branding = load_branding(str(branding_path))

    chart_svg = build_allocation_bar_chart(
        core_subcategories=portfolio_data.core_subcategories,
        alternative_subcategories=portfolio_data.alternative_subcategories,
        core_colors=branding["chart"]["core_gradient"],
        alt_colors=branding["chart"]["alternative_gradient"],
    )

    context = build_report_context(
        portfolio_data, branding, chart_svg, client_name, quarter, report_date
    )

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report_template.html")
    html_output = template.render(**context)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html_output)

    return portfolio_data


def make_safe_filename(name: str) -> str:
    """Turn a client name or CSV filename into a safe string for filenames."""
    safe = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    # Remove anything that isn't alphanumeric, underscore, or hyphen
    safe = "".join(c for c in safe if c.isalnum() or c in ("_", "-"))
    return safe


def main():
    parser = argparse.ArgumentParser(
        description="Batch generate client portfolio reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_generate.py data/clients/
  python batch_generate.py data/anonymized/ -o reports/test/
  python batch_generate.py data/clients/ --quarter "Q1 2026"
  python batch_generate.py data/clients/smith.csv --client "Smith Family"
        """,
    )

    parser.add_argument(
        "input",
        help="Path to a single CSV file or a folder of client CSVs",
    )
    parser.add_argument("-o", "--output-dir", help="Output folder for reports")
    parser.add_argument("-q", "--quarter", help='Report quarter label (e.g., "Q1 2026")')
    parser.add_argument("-d", "--date", help='Report date (e.g., "March 31, 2026")')
    parser.add_argument("-c", "--client", help="Client name (for single-file mode)")
    parser.add_argument(
        "--categories",
        help="Path to categories config JSON",
        default=str(DEFAULT_CATEGORIES),
    )
    parser.add_argument(
        "--branding",
        help="Path to branding config JSON",
        default=str(DEFAULT_BRANDING),
    )
    parser.add_argument(
        "--template-dir",
        help="Path to templates directory",
        default=str(DEFAULT_TEMPLATE_DIR),
    )

    args = parser.parse_args()
    input_path = Path(args.input)

    now = datetime.now()
    quarter = args.quarter or f"Q{(now.month - 1) // 3 + 1} {now.year}"
    report_date = args.date or now.strftime("%B %d, %Y")
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        # Single file mode
        csv_files = [input_path]
    elif input_path.is_dir():
        csv_files = sorted(input_path.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {input_path}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: '{args.input}' is not a valid file or directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {quarter} reports")
    print(f"Report date: {report_date}")
    print(f"Output folder: {output_dir}")
    print(f"Files to process: {len(csv_files)}")
    print()

    results = []
    errors = []

    for csv_file in csv_files:
        # Determine client name: CLI flag > CSV metadata > filename
        if args.client and len(csv_files) == 1:
            client_name = args.client
        else:
            csv_name = read_client_name_from_csv(str(csv_file))
            if csv_name:
                client_name = csv_name
            else:
                # Use filename without extension as client name
                client_name = csv_file.stem.replace("_", " ").title()

        safe_name = make_safe_filename(client_name)
        quarter_label = quarter.replace(" ", "_")
        output_file = output_dir / f"{safe_name}_{quarter_label}.html"

        try:
            portfolio_data = generate_single_report(
                csv_file, output_file, client_name, quarter, report_date,
                args.categories, args.branding, args.template_dir,
            )
            value = portfolio_data.total_market_value
            holdings = len(portfolio_data.holdings)
            print(f"  {client_name}: ${value:,.0f} ({holdings} holdings) → {output_file.name}")
            results.append({"client": client_name, "file": str(output_file)})
        except Exception as e:
            print(f"  ERROR - {csv_file.name}: {e}", file=sys.stderr)
            errors.append({"file": csv_file.name, "error": str(e)})

    print(f"\nDone! Generated {len(results)} report(s).")
    if errors:
        print(f"Errors: {len(errors)} file(s) failed.", file=sys.stderr)
        for err in errors:
            print(f"  - {err['file']}: {err['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()

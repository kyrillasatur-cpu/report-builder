#!/usr/bin/env python3
"""Centerfin Quarterly Portfolio Report Generator.

CLI tool that generates professional HTML reports from holdings CSV files.

Usage:
    python src/generate.py data/input/sample_holdings.csv
    python src/generate.py data/input/sample_holdings.csv -o data/output/Q4_2025.html
    python src/generate.py data/input/sample_holdings.csv --quarter "Q4 2025" --client "Smith Family"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from data_processor import load_branding, process_portfolio
from chart_builder import build_allocation_bar_chart


# Default paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATEGORIES = PROJECT_ROOT / "config" / "categories.json"
DEFAULT_BRANDING = PROJECT_ROOT / "config" / "branding.json"
DEFAULT_TEMPLATE_DIR = PROJECT_ROOT / "templates"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def build_report_context(portfolio_data, branding, chart_svg, args):
    """Assemble the full template context dict."""
    company = branding["company"]
    colors = branding["colors"]
    fonts = branding["fonts"]

    now = datetime.now()
    quarter = args.quarter or f"Q{(now.month - 1) // 3 + 1} {now.year}"
    report_date = args.date or now.strftime("%B %d, %Y")

    # Default notable events (can be overridden via config in the future)
    notable_events = [
        "<strong>Digital Assets:</strong> Bitcoin ETF holdings (IBIT, FBTC) added to Alternative allocation, reflecting growing institutional adoption of digital asset exposure.",
        "<strong>Gold & Silver:</strong> Precious metals allocation maintained as inflation hedge, with GLD and SLV providing commodity diversification.",
        "<strong>Fixed Income:</strong> Bond allocation (BND, AGG, SHV) positioned for rate environment with mix of aggregate and short-duration exposure.",
        "<strong>Real Estate:</strong> REIT positions (VNQ, SCHH) provide real asset exposure and income generation within the Alternative sleeve.",
    ]

    # Default performance highlights
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
        "client_name": args.client or "",
        "total_market_value": portfolio_data.total_market_value,
        "core_weight": portfolio_data.core_allocation.weight,
        "alt_weight": portfolio_data.alternative_allocation.weight,
        "num_holdings": len(portfolio_data.holdings),
        "chart_svg": chart_svg,
        "core_subcategories": portfolio_data.core_subcategories,
        "alternative_subcategories": portfolio_data.alternative_subcategories,
        "notable_events": notable_events,
        "performance_highlights": performance_highlights,
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
    }


def generate_report(args):
    """Main report generation pipeline."""
    csv_path = Path(args.input_file)
    if not csv_path.exists():
        print(f"Error: Input file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    categories_path = Path(args.categories or DEFAULT_CATEGORIES)
    branding_path = Path(args.branding or DEFAULT_BRANDING)
    template_dir = Path(args.template_dir or DEFAULT_TEMPLATE_DIR)

    # Process data
    portfolio_data = process_portfolio(str(csv_path), str(categories_path))
    branding = load_branding(str(branding_path))

    # Build chart
    chart_svg = build_allocation_bar_chart(
        core_subcategories=portfolio_data.core_subcategories,
        alternative_subcategories=portfolio_data.alternative_subcategories,
        core_colors=branding["chart"]["core_gradient"],
        alt_colors=branding["chart"]["alternative_gradient"],
    )

    # Build template context
    context = build_report_context(portfolio_data, branding, chart_svg, args)

    # Render HTML
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report_template.html")
    html_output = template.render(**context)

    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = DEFAULT_OUTPUT_DIR / f"report_{timestamp}.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_output)

    print(f"Report generated: {output_path}")
    print(f"  Portfolio value: ${portfolio_data.total_market_value:,.0f}")
    print(f"  Core allocation: {portfolio_data.core_allocation.weight:.1f}%")
    print(f"  Alternative allocation: {portfolio_data.alternative_allocation.weight:.1f}%")
    print(f"  Holdings: {len(portfolio_data.holdings)}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Centerfin Quarterly Portfolio Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/generate.py data/input/sample_holdings.csv
  python src/generate.py data/input/holdings.csv -o reports/Q4_2025.html
  python src/generate.py data/input/holdings.csv --quarter "Q4 2025" --client "Smith Family"
        """,
    )

    parser.add_argument("input_file", help="Path to holdings CSV file")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("-q", "--quarter", help='Report quarter label (e.g., "Q4 2025")')
    parser.add_argument("-d", "--date", help='Report date (e.g., "December 31, 2025")')
    parser.add_argument("-c", "--client", help="Client name for the report")
    parser.add_argument(
        "--categories", help="Path to categories config JSON (default: config/categories.json)"
    )
    parser.add_argument(
        "--branding", help="Path to branding config JSON (default: config/branding.json)"
    )
    parser.add_argument(
        "--template-dir", help="Path to templates directory (default: templates/)"
    )

    args = parser.parse_args()
    generate_report(args)


if __name__ == "__main__":
    main()

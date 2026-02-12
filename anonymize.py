#!/usr/bin/env python3
"""Anonymize client portfolio CSVs by replacing personally identifiable information.

Takes real client CSV files and produces anonymized copies that are safe to
share, commit to version control, or use for testing.

What gets anonymized:
  - Client names → "Client_001", "Client_002", etc.
  - Account numbers → "ANON-0001", "ANON-0002", etc.

Financial data (holdings, quantities, prices) is kept intact by default so
reports remain realistic. Use --fuzz to slightly randomize dollar amounts.

Usage:
    # Anonymize a single file
    python anonymize.py data/clients/smith_family.csv

    # Anonymize all CSVs in a folder
    python anonymize.py data/clients/

    # Anonymize with financial data fuzzing (±10%)
    python anonymize.py data/clients/ --fuzz

    # Specify output folder
    python anonymize.py data/clients/ -o data/anonymized/
"""

import argparse
import csv
import json
import random
import sys
from pathlib import Path


def detect_format(csv_path: str) -> str:
    """Detect whether the CSV uses the metadata header format or simple format.

    Metadata format (used by generate_report.py / PDF path):
        client_name,account_number,report_date
        John Smith,ACC-2024-1234,2024-01-31
        Symbol,Name,Quantity,Price,Cost Basis
        ...

    Simple format (used by src/generate.py / HTML path):
        Symbol,Name,Quantity,Price,Market Value,Weight
        ...
    """
    with open(csv_path, "r") as f:
        first_line = f.readline().strip()
    if first_line.lower().startswith("client_name"):
        return "metadata"
    return "simple"


def anonymize_file(
    input_path: str,
    output_path: str,
    client_id: int,
    fuzz: bool = False,
    fuzz_range: float = 0.10,
) -> dict:
    """Anonymize a single CSV file.

    Returns a mapping dict: {"original_name": ..., "anonymous_id": ...}
    """
    fmt = detect_format(input_path)
    mapping = {"original_name": None, "anonymous_id": f"Client_{client_id:03d}"}

    with open(input_path, "r") as f:
        lines = f.readlines()

    output_lines = []

    if fmt == "metadata":
        # Line 1: header row (client_name,account_number,report_date)
        output_lines.append(lines[0])

        # Line 2: actual client data — anonymize it
        parts = lines[1].strip().split(",")
        if len(parts) >= 2:
            mapping["original_name"] = parts[0]
            parts[0] = f"Client_{client_id:03d}"
            parts[1] = f"ANON-{client_id:04d}"
        output_lines.append(",".join(parts) + "\n")

        # Line 3: column headers for holdings
        output_lines.append(lines[2])

        # Lines 4+: holdings data
        for line in lines[3:]:
            if fuzz and line.strip():
                output_lines.append(_fuzz_holdings_line(line, fuzz_range, fmt))
            else:
                output_lines.append(line)
    else:
        # Simple format — no PII in the file itself.
        # Line 1: column headers
        output_lines.append(lines[0])

        # Lines 2+: holdings data
        for line in lines[1:]:
            if fuzz and line.strip():
                output_lines.append(_fuzz_holdings_line(line, fuzz_range, fmt))
            else:
                output_lines.append(line)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.writelines(output_lines)

    return mapping


def _fuzz_holdings_line(line: str, fuzz_range: float, fmt: str) -> str:
    """Apply random ±fuzz_range multiplier to numeric financial columns."""
    parts = line.strip().split(",")

    if fmt == "metadata":
        # Columns: Symbol, Name, Quantity, Price, Cost Basis
        # Fuzz columns 2 (Quantity), 3 (Price), 4 (Cost Basis)
        numeric_cols = [2, 3, 4]
    else:
        # Columns: Symbol, Name, Quantity, Price, Market Value, Weight
        # Fuzz columns 2 (Quantity), 3 (Price), 4 (Market Value)
        # Recalculate Market Value from fuzzed Quantity * Price
        numeric_cols = [2, 3]

    for col in numeric_cols:
        if col < len(parts):
            try:
                val = float(parts[col])
                factor = 1 + random.uniform(-fuzz_range, fuzz_range)
                parts[col] = f"{val * factor:.2f}"
            except ValueError:
                pass

    # For simple format, recalculate Market Value if we fuzzed Quantity and Price
    if fmt == "simple" and len(parts) > 4:
        try:
            qty = float(parts[2])
            price = float(parts[3])
            parts[4] = f"{qty * price:.2f}"
        except ValueError:
            pass

    return ",".join(parts) + "\n"


def anonymize_folder(
    input_dir: str, output_dir: str, fuzz: bool = False
) -> list:
    """Anonymize all CSV files in a folder. Returns list of mappings."""
    input_path = Path(input_dir)
    csv_files = sorted(input_path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    mappings = []
    for i, csv_file in enumerate(csv_files, start=1):
        output_file = Path(output_dir) / csv_file.name
        mapping = anonymize_file(str(csv_file), str(output_file), i, fuzz=fuzz)
        mapping["source_file"] = csv_file.name
        mapping["anonymized_file"] = str(output_file)
        mappings.append(mapping)
        print(f"  Anonymized: {csv_file.name} → {output_file}")

    return mappings


def main():
    parser = argparse.ArgumentParser(
        description="Anonymize client portfolio CSVs for safe sharing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python anonymize.py data/clients/smith_family.csv
  python anonymize.py data/clients/
  python anonymize.py data/clients/ --fuzz
  python anonymize.py data/clients/ -o data/anonymized/
        """,
    )

    parser.add_argument(
        "input",
        help="Path to a single CSV file or a folder of CSVs",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file or folder (default: data/anonymized/)",
        default=None,
    )
    parser.add_argument(
        "--fuzz",
        action="store_true",
        help="Slightly randomize financial numbers (±10%%) for extra safety",
    )
    parser.add_argument(
        "--save-mapping",
        action="store_true",
        help="Save a name→ID mapping file (for your internal reference only)",
    )

    args = parser.parse_args()
    input_path = Path(args.input)

    project_root = Path(__file__).resolve().parent
    default_output = project_root / "data" / "anonymized"

    if input_path.is_dir():
        output_dir = args.output or str(default_output)
        print(f"Anonymizing all CSVs in: {input_path}")
        print(f"Output folder: {output_dir}")
        if args.fuzz:
            print("Financial data fuzzing: ENABLED (±10%)")
        print()

        mappings = anonymize_folder(str(input_path), output_dir, fuzz=args.fuzz)

        if args.save_mapping and mappings:
            mapping_path = Path(output_dir) / "_name_mapping.json"
            with open(mapping_path, "w") as f:
                json.dump(mappings, f, indent=2)
            print(f"\nMapping saved to: {mapping_path}")
            print("  (Keep this file private — it links anonymous IDs to real names)")

        print(f"\nDone! Anonymized {len(mappings)} file(s).")

    elif input_path.is_file():
        if args.output:
            output_file = args.output
        else:
            default_output.mkdir(parents=True, exist_ok=True)
            output_file = str(default_output / input_path.name)

        print(f"Anonymizing: {input_path}")
        if args.fuzz:
            print("Financial data fuzzing: ENABLED (±10%)")

        mapping = anonymize_file(str(input_path), output_file, 1, fuzz=args.fuzz)
        print(f"Output: {output_file}")

        if args.save_mapping:
            mapping_path = Path(output_file).parent / "_name_mapping.json"
            mapping["source_file"] = input_path.name
            with open(mapping_path, "w") as f:
                json.dump([mapping], f, indent=2)
            print(f"Mapping saved to: {mapping_path}")

        print("Done!")
    else:
        print(f"Error: '{args.input}' is not a valid file or directory.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

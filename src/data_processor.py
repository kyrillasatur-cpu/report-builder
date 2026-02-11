"""Data processor for parsing holdings CSV and computing category allocations."""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Holding:
    """A single portfolio holding."""
    symbol: str
    name: str
    quantity: float
    price: float
    market_value: float
    weight: float
    category: str = ""
    subcategory: str = ""


@dataclass
class CategoryAllocation:
    """Allocation data for a category or subcategory."""
    name: str
    weight: float
    holdings: list = field(default_factory=list)


@dataclass
class PortfolioData:
    """Processed portfolio data ready for report generation."""
    holdings: list
    total_market_value: float
    core_allocation: CategoryAllocation
    alternative_allocation: CategoryAllocation
    core_subcategories: list
    alternative_subcategories: list


def load_categories(config_path: str) -> dict:
    """Load category mappings from JSON config."""
    with open(config_path, 'r') as f:
        return json.load(f)


def load_branding(config_path: str) -> dict:
    """Load branding config from JSON."""
    with open(config_path, 'r') as f:
        return json.load(f)


def parse_holdings_csv(csv_path: str) -> list:
    """Parse a holdings CSV file into a list of Holding objects."""
    holdings = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                holding = Holding(
                    symbol=row.get('Symbol', '').strip(),
                    name=row.get('Name', '').strip(),
                    quantity=float(row.get('Quantity', 0)),
                    price=float(row.get('Price', 0)),
                    market_value=float(row.get('Market Value', 0)),
                    weight=float(row.get('Weight', 0)),
                )
                if holding.symbol:
                    holdings.append(holding)
            except (ValueError, KeyError):
                continue
    return holdings


def classify_holdings(holdings: list, categories_config: dict) -> list:
    """Assign each holding to its category and subcategory based on config."""
    category_map = categories_config.get('categories', {})

    # Build a reverse lookup: symbol -> (category, subcategory)
    symbol_lookup = {}
    for cat_name, cat_data in category_map.items():
        for subcat_name, symbols in cat_data.get('subcategories', {}).items():
            for symbol in symbols:
                symbol_lookup[symbol] = (cat_name, subcat_name)

    for holding in holdings:
        if holding.symbol in symbol_lookup:
            holding.category, holding.subcategory = symbol_lookup[holding.symbol]
        else:
            holding.category = "Other"
            holding.subcategory = "Uncategorized"

    return holdings


def compute_allocations(holdings: list) -> PortfolioData:
    """Compute category and subcategory allocation breakdowns."""
    total_value = sum(h.market_value for h in holdings)

    core_holdings = [h for h in holdings if h.category == "Core"]
    alt_holdings = [h for h in holdings if h.category == "Alternative"]

    core_weight = sum(h.weight for h in core_holdings)
    alt_weight = sum(h.weight for h in alt_holdings)

    # Build subcategory breakdowns
    def build_subcategories(holding_list):
        subcat_map = {}
        for h in holding_list:
            if h.subcategory not in subcat_map:
                subcat_map[h.subcategory] = CategoryAllocation(
                    name=h.subcategory, weight=0, holdings=[]
                )
            subcat_map[h.subcategory].weight += h.weight
            subcat_map[h.subcategory].holdings.append(h)
        # Sort by weight descending
        return sorted(subcat_map.values(), key=lambda x: x.weight, reverse=True)

    core_subcats = build_subcategories(core_holdings)
    alt_subcats = build_subcategories(alt_holdings)

    return PortfolioData(
        holdings=holdings,
        total_market_value=total_value,
        core_allocation=CategoryAllocation(
            name="Core", weight=core_weight, holdings=core_holdings
        ),
        alternative_allocation=CategoryAllocation(
            name="Alternative", weight=alt_weight, holdings=alt_holdings
        ),
        core_subcategories=core_subcats,
        alternative_subcategories=alt_subcats,
    )


def process_portfolio(csv_path: str, categories_path: str) -> PortfolioData:
    """Full pipeline: parse CSV, classify, compute allocations."""
    categories_config = load_categories(categories_path)
    holdings = parse_holdings_csv(csv_path)
    holdings = classify_holdings(holdings, categories_config)
    return compute_allocations(holdings)

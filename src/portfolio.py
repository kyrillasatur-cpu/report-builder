"""Portfolio data models and CSV parsing."""

from dataclasses import dataclass
from typing import List
from datetime import datetime
import pandas as pd


@dataclass
class Holding:
    """Represents a single portfolio holding."""
    symbol: str
    name: str
    quantity: float
    price: float
    cost_basis: float

    @property
    def market_value(self) -> float:
        """Calculate current market value."""
        return self.quantity * self.price

    @property
    def total_cost(self) -> float:
        """Calculate total cost basis."""
        return self.quantity * self.cost_basis

    @property
    def gain_loss(self) -> float:
        """Calculate gain/loss in dollars."""
        return self.market_value - self.total_cost

    @property
    def gain_loss_percent(self) -> float:
        """Calculate gain/loss as percentage."""
        if self.total_cost == 0:
            return 0.0
        return (self.gain_loss / self.total_cost) * 100


@dataclass
class Portfolio:
    """Represents a complete portfolio."""
    client_name: str
    account_number: str
    report_date: datetime
    holdings: List[Holding]

    @property
    def total_market_value(self) -> float:
        """Calculate total portfolio market value."""
        return sum(h.market_value for h in self.holdings)

    @property
    def total_cost_basis(self) -> float:
        """Calculate total portfolio cost basis."""
        return sum(h.total_cost for h in self.holdings)

    @property
    def total_gain_loss(self) -> float:
        """Calculate total portfolio gain/loss."""
        return self.total_market_value - self.total_cost_basis

    @property
    def total_gain_loss_percent(self) -> float:
        """Calculate total portfolio gain/loss percentage."""
        if self.total_cost_basis == 0:
            return 0.0
        return (self.total_gain_loss / self.total_cost_basis) * 100


def parse_csv(file_path: str) -> Portfolio:
    """
    Parse a CSV file containing portfolio holdings.

    Expected CSV format (Option 1 - with metadata header):
    client_name,account_number,report_date
    John Smith,ACC-123,2024-01-31
    Symbol,Name,Quantity,Price,Cost Basis
    AAPL,Apple Inc.,100,150.00,120.00
    ...

    Or (Option 2 - simple format):
    Symbol,Name,Quantity,Price,Cost Basis
    AAPL,Apple Inc.,100,150.00,120.00
    ...

    Args:
        file_path: Path to the CSV file

    Returns:
        Portfolio object with all holdings
    """
    # Read the file to detect format
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Check if first line contains client metadata
    first_line = lines[0].strip().lower()
    has_metadata = 'client_name' in first_line or 'account_number' in first_line

    if has_metadata and len(lines) >= 3:
        # Parse metadata from first two rows
        metadata_row = lines[1].strip().split(',')
        client_name = metadata_row[0] if len(metadata_row) > 0 else 'Client Name'
        account_number = metadata_row[1] if len(metadata_row) > 1 else 'XXXXXX'
        report_date_str = metadata_row[2] if len(metadata_row) > 2 else datetime.now().strftime('%Y-%m-%d')

        # Parse report date
        try:
            report_date = pd.to_datetime(report_date_str)
        except:
            report_date = datetime.now()

        # Read holdings data starting from row 2 (0-indexed)
        df = pd.read_csv(file_path, skiprows=2)
    else:
        # Simple format without metadata
        client_name = 'Client Name'
        account_number = 'XXXXXX'
        report_date = datetime.now()
        df = pd.read_csv(file_path)

    # Parse holdings
    holdings = []
    for _, row in df.iterrows():
        # Skip rows without required data
        try:
            symbol = str(row['Symbol']).strip()
            quantity = float(row['Quantity'])
            price = float(row['Price'])

            # Handle different column name variations for cost basis
            cost_basis_col = None
            for col in ['Cost Basis', 'CostBasis', 'cost_basis']:
                if col in row and pd.notna(row[col]):
                    cost_basis_col = col
                    break

            cost_basis = float(row[cost_basis_col]) if cost_basis_col else price

            holding = Holding(
                symbol=symbol,
                name=str(row.get('Name', symbol)).strip(),
                quantity=quantity,
                price=price,
                cost_basis=cost_basis
            )
            holdings.append(holding)
        except (ValueError, KeyError) as e:
            # Skip invalid rows
            continue

    return Portfolio(
        client_name=str(client_name),
        account_number=str(account_number),
        report_date=report_date,
        holdings=holdings
    )

"""Professional PDF report generator for portfolio holdings."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import List
from .portfolio import Portfolio, Holding


class PortfolioReportGenerator:
    """Generates professional PDF reports for portfolio holdings."""

    def __init__(self, portfolio: Portfolio):
        """
        Initialize the report generator.

        Args:
            portfolio: Portfolio object containing holdings data
        """
        self.portfolio = portfolio
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER,
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Info text
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
        ))

    def _format_currency(self, value: float) -> str:
        """Format a number as currency."""
        return f"${value:,.2f}"

    def _format_percent(self, value: float) -> str:
        """Format a number as percentage."""
        sign = '+' if value > 0 else ''
        return f"{sign}{value:.2f}%"

    def _create_header(self) -> List:
        """Create the report header section."""
        elements = []

        # Title
        title = Paragraph(
            "Portfolio Holdings Report",
            self.styles['CustomTitle']
        )
        elements.append(title)

        # Client information
        client_info = f"""
        <b>Client:</b> {self.portfolio.client_name}<br/>
        <b>Account Number:</b> {self.portfolio.account_number}<br/>
        <b>Report Date:</b> {self.portfolio.report_date.strftime('%B %d, %Y')}
        """
        elements.append(Paragraph(client_info, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_summary_section(self) -> List:
        """Create the portfolio summary section."""
        elements = []

        # Section header
        elements.append(Paragraph("Portfolio Summary", self.styles['SectionHeader']))

        # Summary data
        summary_data = [
            ['Metric', 'Value'],
            ['Total Market Value', self._format_currency(self.portfolio.total_market_value)],
            ['Total Cost Basis', self._format_currency(self.portfolio.total_cost_basis)],
            ['Total Gain/Loss', self._format_currency(self.portfolio.total_gain_loss)],
            ['Total Return', self._format_percent(self.portfolio.total_gain_loss_percent)],
            ['Number of Holdings', str(len(self.portfolio.holdings))]
        ]

        # Create summary table
        summary_table = Table(summary_data, colWidths=[3 * inch, 2.5 * inch])
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),

            # Highlight gain/loss rows
            ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#f8f9fa')),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.4 * inch))

        return elements

    def _create_holdings_table(self) -> List:
        """Create the detailed holdings table."""
        elements = []

        # Section header
        elements.append(Paragraph("Holdings Detail", self.styles['SectionHeader']))

        # Table headers
        holdings_data = [[
            'Symbol',
            'Name',
            'Quantity',
            'Price',
            'Market Value',
            'Cost Basis',
            'Gain/Loss',
            'Return %'
        ]]

        # Add holdings data
        for holding in self.portfolio.holdings:
            holdings_data.append([
                holding.symbol,
                holding.name,
                f"{holding.quantity:,.2f}",
                self._format_currency(holding.price),
                self._format_currency(holding.market_value),
                self._format_currency(holding.total_cost),
                self._format_currency(holding.gain_loss),
                self._format_percent(holding.gain_loss_percent)
            ])

        # Column widths (adjusted to fit page)
        col_widths = [0.6*inch, 1.5*inch, 0.7*inch, 0.8*inch,
                      1*inch, 0.9*inch, 0.9*inch, 0.8*inch]

        # Create table
        holdings_table = Table(holdings_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Alignment
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),

            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f8f9fa')]),
        ]

        # Highlight positive/negative returns
        for i, holding in enumerate(self.portfolio.holdings, start=1):
            if holding.gain_loss > 0:
                table_style.append(
                    ('TEXTCOLOR', (6, i), (7, i), colors.HexColor('#27ae60'))
                )
            elif holding.gain_loss < 0:
                table_style.append(
                    ('TEXTCOLOR', (6, i), (7, i), colors.HexColor('#e74c3c'))
                )

        holdings_table.setStyle(TableStyle(table_style))
        elements.append(holdings_table)

        return elements

    def _create_footer(self) -> List:
        """Create the report footer."""
        elements = []
        elements.append(Spacer(1, 0.5 * inch))

        footer_text = f"""
        <i>This report is for informational purposes only and should not be considered
        as investment advice. Past performance does not guarantee future results.</i><br/>
        <i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>
        """
        elements.append(Paragraph(footer_text, self.styles['InfoText']))

        return elements

    def generate(self, output_path: str):
        """
        Generate the PDF report.

        Args:
            output_path: Path where the PDF file will be saved
        """
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Build the document content
        elements = []
        elements.extend(self._create_header())
        elements.extend(self._create_summary_section())
        elements.extend(self._create_holdings_table())
        elements.extend(self._create_footer())

        # Build the PDF
        doc.build(elements)
        print(f"Report generated successfully: {output_path}")

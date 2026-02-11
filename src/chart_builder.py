"""Chart builder for generating inline SVG allocation bar charts."""


def _format_weight(weight: float) -> str:
    """Format weight as percentage string."""
    return f"{weight:.1f}%"


def build_allocation_bar_chart(
    core_subcategories: list,
    alternative_subcategories: list,
    core_colors: list,
    alt_colors: list,
    bar_height: int = 56,
    width: int = 100,
) -> str:
    """Build a horizontal stacked bar chart as inline SVG.

    Returns an SVG string showing Core and Alternative allocations
    with individual holdings visible within each segment.
    """
    segments = []

    # Core subcategories
    for i, subcat in enumerate(core_subcategories):
        color = core_colors[i % len(core_colors)]
        segments.append({
            'label': subcat.name,
            'weight': subcat.weight,
            'color': color,
            'type': 'Core',
            'holdings': [
                {'symbol': h.symbol, 'weight': h.weight}
                for h in subcat.holdings
            ],
        })

    # Alternative subcategories
    for i, subcat in enumerate(alternative_subcategories):
        color = alt_colors[i % len(alt_colors)]
        segments.append({
            'label': subcat.name,
            'weight': subcat.weight,
            'color': color,
            'type': 'Alternative',
            'holdings': [
                {'symbol': h.symbol, 'weight': h.weight}
                for h in subcat.holdings
            ],
        })

    total_weight = sum(s['weight'] for s in segments)
    if total_weight == 0:
        return '<p>No allocation data available.</p>'

    chart_height = bar_height + 120  # room for labels below
    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 1000 {chart_height}" '
        f'style="width:100%;max-width:1000px;height:auto;font-family:\'Helvetica Neue\',Arial,sans-serif;">'
    )

    # Draw bar segments
    x = 0
    bar_y = 10
    segment_positions = []

    for seg in segments:
        seg_width = (seg['weight'] / total_weight) * 1000
        if seg_width < 1:
            continue

        svg_parts.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{seg_width:.1f}" '
            f'height="{bar_height}" fill="{seg["color"]}" />'
        )

        # Add holding labels inside the bar if segment is wide enough
        if seg_width > 40:
            label_x = x + seg_width / 2
            label_y = bar_y + bar_height / 2
            # Show subcategory weight
            font_size = 11 if seg_width > 60 else 9
            svg_parts.append(
                f'<text x="{label_x:.1f}" y="{label_y + 1}" '
                f'text-anchor="middle" dominant-baseline="middle" '
                f'fill="white" font-size="{font_size}" font-weight="600" '
                f'opacity="0.95">'
                f'{_format_weight(seg["weight"])}'
                f'</text>'
            )

        segment_positions.append({
            'x': x,
            'width': seg_width,
            **seg,
        })
        x += seg_width

    # Draw legend labels below bar
    label_y = bar_y + bar_height + 22
    for seg in segment_positions:
        mid_x = seg['x'] + seg['width'] / 2
        if seg['width'] > 50:
            svg_parts.append(
                f'<text x="{mid_x:.1f}" y="{label_y}" '
                f'text-anchor="middle" fill="#495057" font-size="10" '
                f'font-weight="600">'
                f'{seg["label"]}'
                f'</text>'
            )
            # Show individual holdings below
            holding_labels = ', '.join(
                f'{h["symbol"]}' for h in seg['holdings']
            )
            if seg['width'] > 70:
                svg_parts.append(
                    f'<text x="{mid_x:.1f}" y="{label_y + 16}" '
                    f'text-anchor="middle" fill="#6c757d" font-size="8.5">'
                    f'{holding_labels}'
                    f'</text>'
                )

    # Core vs Alternative summary labels
    core_segs = [s for s in segment_positions if s['type'] == 'Core']
    alt_segs = [s for s in segment_positions if s['type'] == 'Alternative']

    summary_y = label_y + 42

    if core_segs:
        core_start = core_segs[0]['x']
        core_end = core_segs[-1]['x'] + core_segs[-1]['width']
        core_mid = (core_start + core_end) / 2
        core_total = sum(s['weight'] for s in core_segs)

        # Bracket line
        svg_parts.append(
            f'<line x1="{core_start:.1f}" y1="{summary_y - 6}" '
            f'x2="{core_end:.1f}" y2="{summary_y - 6}" '
            f'stroke="#2d6a4f" stroke-width="2" />'
        )
        svg_parts.append(
            f'<text x="{core_mid:.1f}" y="{summary_y + 10}" '
            f'text-anchor="middle" fill="#2d6a4f" font-size="13" '
            f'font-weight="700">'
            f'Core \u2014 {_format_weight(core_total)}'
            f'</text>'
        )

    if alt_segs:
        alt_start = alt_segs[0]['x']
        alt_end = alt_segs[-1]['x'] + alt_segs[-1]['width']
        alt_mid = (alt_start + alt_end) / 2
        alt_total = sum(s['weight'] for s in alt_segs)

        svg_parts.append(
            f'<line x1="{alt_start:.1f}" y1="{summary_y - 6}" '
            f'x2="{alt_end:.1f}" y2="{summary_y - 6}" '
            f'stroke="#7f5539" stroke-width="2" />'
        )
        svg_parts.append(
            f'<text x="{alt_mid:.1f}" y="{summary_y + 10}" '
            f'text-anchor="middle" fill="#7f5539" font-size="13" '
            f'font-weight="700">'
            f'Alternative \u2014 {_format_weight(alt_total)}'
            f'</text>'
        )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)

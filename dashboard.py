"""Rich CLI dashboard for P46 Defense Budget & Appropriations Tracker.

ASCII-safe output for Windows cp1252 terminal compatibility.
Uses Rich tables but avoids Unicode box-drawing characters.
"""
from __future__ import annotations

from config import (
    TREND_STRONG_GROWTH, TREND_GROWING, TREND_FLAT,
    TREND_CUT, TREND_STRONG_CUT, TREND_NEW_START, TREND_VOLATILE, TREND_UNKNOWN,
    DATA_SOURCE_DEMO, DATA_DISCLAIMER,
)
from models import FundingTrend, BudgetReport, NdaaContext, ProgramFunding

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False


def _get_console() -> "Console":
    if not _RICH_AVAILABLE:
        raise RuntimeError("rich library not installed. Run: pip install rich")
    return Console(highlight=False)


def _trend_marker(trend: str) -> str:
    """ASCII-safe trend indicator."""
    markers = {
        TREND_STRONG_GROWTH: "[++]",
        TREND_GROWING:       "[+] ",
        TREND_FLAT:          "[=] ",
        TREND_CUT:           "[-] ",
        TREND_STRONG_CUT:    "[--]",
        TREND_NEW_START:     "[N] ",
        TREND_VOLATILE:      "[~] ",
        TREND_UNKNOWN:       "[?] ",
    }
    return markers.get(trend, "[?] ")


def _trend_color(trend: str) -> str:
    """Map trend to Rich color string."""
    colors = {
        TREND_STRONG_GROWTH: "bold green",
        TREND_GROWING:       "green",
        TREND_FLAT:          "yellow",
        TREND_CUT:           "red",
        TREND_STRONG_CUT:    "bold red",
        TREND_NEW_START:     "cyan",
        TREND_VOLATILE:      "magenta",
        TREND_UNKNOWN:       "white",
    }
    return colors.get(trend, "white")


def print_funding_table(trend: FundingTrend) -> None:
    """Print a year-by-year funding table to stdout."""
    if not _RICH_AVAILABLE:
        _print_funding_table_plain(trend)
        return

    console = _get_console()
    table = Table(
        title=f"DoD Funding: {trend.tech_area}  ({trend.cagr_display})",
        box=box.ASCII2,
        show_header=True,
        header_style="bold",
    )

    table.add_column("FY", style="bold", width=4)
    table.add_column("RDT&E", width=8, justify="right")
    table.add_column("Procurement", width=12, justify="right")
    table.add_column("O&M", width=8, justify="right")
    table.add_column("TOTAL", width=8, justify="right", style="bold")
    table.add_column("YoY", width=14, justify="right")
    table.add_column("Trend", width=16)

    for fy in trend.fiscal_years:
        f = trend.funding_by_year[fy]
        rdte = f"${f.rdte_billions:.1f}B" if f.rdte_billions is not None else "N/A"
        proc = f"${f.procurement_billions:.1f}B" if f.procurement_billions is not None else "N/A"
        om = f"${f.om_billions:.1f}B" if f.om_billions is not None else "N/A"
        total = f"${f.total_billions:.1f}B"

        yoy_str = "(base)"
        yoy_trend = TREND_UNKNOWN
        for yoy in trend.yoy_changes:
            if yoy.to_year == fy:
                yoy_str = f"{yoy.delta_display} ({yoy.pct_display})"
                yoy_trend = yoy.trend
                break

        color = _trend_color(yoy_trend) if yoy_trend != TREND_UNKNOWN else "white"
        marker = _trend_marker(yoy_trend)

        table.add_row(str(fy), rdte, proc, om, total,
                      f"[{color}]{yoy_str}[/{color}]",
                      f"[{color}]{marker} {yoy_trend}[/{color}]")

    console.print(table)


def _print_funding_table_plain(trend: FundingTrend) -> None:
    print(f"\nDoD Funding: {trend.tech_area}  ({trend.cagr_display})")
    print(f"{'FY':<4}  {'RDT&E':<8}  {'Proc':<10}  {'O&M':<8}  {'TOTAL':<8}  YoY")
    print("-" * 65)
    for fy in trend.fiscal_years:
        f = trend.funding_by_year[fy]
        rdte = f"${f.rdte_billions:.1f}B" if f.rdte_billions is not None else "N/A"
        proc = f"${f.procurement_billions:.1f}B" if f.procurement_billions is not None else "N/A"
        om = f"${f.om_billions:.1f}B" if f.om_billions is not None else "N/A"
        total = f"${f.total_billions:.1f}B"

        yoy_str = "(base)"
        for yoy in trend.yoy_changes:
            if yoy.to_year == fy:
                yoy_str = f"{yoy.delta_display} ({yoy.pct_display})"
                break
        print(f"{fy:<4}  {rdte:<8}  {proc:<10}  {om:<8}  {total:<8}  {yoy_str}")


def print_comparison_table(trends: list[FundingTrend]) -> None:
    """Print a side-by-side comparison of all tech areas."""
    if not _RICH_AVAILABLE:
        _print_comparison_plain(trends)
        return

    console = _get_console()
    table = Table(
        title="DoD Defense Technology Budget Comparison",
        box=box.ASCII2,
        show_header=True,
        header_style="bold",
    )

    table.add_column("Tech Area", width=14)
    table.add_column("CAGR", width=10, justify="right")
    table.add_column("Overall Trend", width=16)
    all_years = sorted(set(fy for t in trends for fy in t.fiscal_years))
    for fy in all_years:
        table.add_column(f"FY{fy}", width=8, justify="right")

    for t in sorted(trends, key=lambda x: x.cagr, reverse=True):
        color = _trend_color(t.overall_trend)
        marker = _trend_marker(t.overall_trend)
        row = [
            t.tech_area,
            f"[{color}]{t.cagr_display}[/{color}]",
            f"[{color}]{marker} {t.overall_trend}[/{color}]",
        ]
        for fy in all_years:
            f = t.funding_by_year.get(fy)
            row.append(f"${f.total_billions:.1f}B" if f else "-")
        table.add_row(*row)

    console.print(table)


def _print_comparison_plain(trends: list[FundingTrend]) -> None:
    print("\nDoD Defense Technology Budget Comparison")
    print("-" * 70)
    all_years = sorted(set(fy for t in trends for fy in t.fiscal_years))
    header = f"{'Area':<14}  {'CAGR':<10}  {'Trend':<16}  " + "  ".join(f"FY{y}" for y in all_years)
    print(header)
    print("-" * 70)
    for t in sorted(trends, key=lambda x: x.cagr, reverse=True):
        totals = "  ".join(
            f"${t.funding_by_year[y].total_billions:.1f}B" if y in t.funding_by_year else "  -  "
            for y in all_years
        )
        print(f"{t.tech_area:<14}  {t.cagr_display:<10}  {t.overall_trend:<16}  {totals}")


def print_ndaa_context(contexts: list[NdaaContext]) -> None:
    """Print NDAA provisions for a tech area."""
    if not _RICH_AVAILABLE:
        for ctx in contexts:
            print(f"\nFY{ctx.fiscal_year}: {ctx.ndaa_title}")
            for prov in ctx.key_provisions:
                print(f"  -- {prov}")
            print(f"  Authorization: {ctx.authorized_amount_note}")
        return

    console = _get_console()
    for ctx in contexts:
        console.print(f"\n[bold]FY{ctx.fiscal_year}[/bold]: {ctx.ndaa_title} [dim]({ctx.data_source})[/dim]")
        for prov in ctx.key_provisions:
            console.print(f"  -- {prov}")
        console.print(f"  [dim]Auth note: {ctx.authorized_amount_note}[/dim]")


def print_report(report_text: str, action_items: list[str]) -> None:
    """Print the full analyst report and action items."""
    if not _RICH_AVAILABLE:
        print(report_text)
        if action_items:
            print("\nACTION ITEMS:")
            for item in action_items:
                print(f"  {item}")
        return

    console = _get_console()
    console.print(report_text)
    if action_items:
        console.print("\n[bold]ACTION ITEMS:[/bold]")
        for item in action_items:
            console.print(f"  {item}")


def print_summary_banner(trend: FundingTrend, data_source: str) -> None:
    """Print a one-line summary banner for a tech area."""
    color = _trend_color(trend.overall_trend)
    marker = _trend_marker(trend.overall_trend)
    first_fy = min(trend.fiscal_years)
    last_fy = max(trend.fiscal_years)
    first_total = trend.funding_by_year[first_fy].total_billions
    last_total = trend.funding_by_year[last_fy].total_billions
    note = "[DEMO]" if data_source == DATA_SOURCE_DEMO else "[LIVE]"

    if _RICH_AVAILABLE:
        console = _get_console()
        console.print(
            f"[{color}]{marker}[/{color}] "
            f"[bold]{trend.tech_area:<14}[/bold] "
            f"[{color}]{trend.overall_trend:<16}[/{color}] "
            f"{trend.cagr_display:<16} "
            f"${first_total:.1f}B (FY{first_fy}) -> ${last_total:.1f}B (FY{last_fy}) "
            f"[dim]{note}[/dim]"
        )
    else:
        print(
            f"{marker} {trend.tech_area:<14} {trend.overall_trend:<16} {trend.cagr_display:<16} "
            f"${first_total:.1f}B (FY{first_fy}) -> ${last_total:.1f}B (FY{last_fy}) {note}"
        )


def print_data_disclaimer() -> None:
    if _RICH_AVAILABLE:
        console = _get_console()
        console.print(f"\n[dim]{DATA_DISCLAIMER[:200]}[/dim]\n")
    else:
        print(f"\n{DATA_DISCLAIMER[:200]}\n")

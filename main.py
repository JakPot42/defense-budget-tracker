"""CLI entrypoint for P46 Defense Budget & Appropriations Tracker.

Usage:
  python main.py demo                    # full demo: all 4 tech areas
  python main.py track "AI/ML"           # track one tech area (demo mode)
  python main.py track "Hypersonics" --live  # live USASpending data
  python main.py compare                 # side-by-side all areas
  python main.py trend "Space"           # year-over-year trend detail
  python main.py report "Cyber"          # analyst report (demo mode)
  python main.py ndaa "AI/ML"            # NDAA provisions for a tech area
  python main.py areas                   # list all tracked tech areas
"""
from __future__ import annotations

import sys
import os
from datetime import date

try:
    import click
except ImportError:
    print("click not installed. Run: pip install click")
    sys.exit(1)

from config import (
    TRACKED_FISCAL_YEARS, TECH_AREAS, DATA_SOURCE_DEMO, DATA_SOURCE_LIVE,
    DATA_DISCLAIMER,
)
from models import BudgetReport
from budget_db import get_demo_funding, all_demo_tech_areas, demo_tech_area_label
from trend_engine import compute_trend, compare_areas, rdte_share_trend
from congress_client import get_ndaa_contexts
from report_generator import generate_report, ReportGeneratorError
from dashboard import (
    print_funding_table, print_comparison_table, print_ndaa_context,
    print_report, print_summary_banner, print_data_disclaimer,
    _print_comparison_plain,
)


def _validate_tech_area(ctx, param, value: str) -> str:
    known = all_demo_tech_areas()
    if value not in known:
        raise click.BadParameter(
            f"{value!r} is not a tracked tech area. Valid: {', '.join(known)}"
        )
    return value


def _parse_years(years_str: str) -> list[int]:
    try:
        return [int(y.strip()) for y in years_str.split(",")]
    except ValueError:
        raise click.BadParameter(f"Invalid years format: {years_str!r}. Use comma-separated: 2022,2023,2024")


def _build_report(tech_area: str, years: list[int], live: bool) -> BudgetReport:
    if live:
        from usaspending_client import build_live_funding, USASpendingError
        try:
            funding_by_year = build_live_funding(tech_area, years)
            data_source = DATA_SOURCE_LIVE
        except USASpendingError as exc:
            click.echo(f"[WARN] USASpending.gov fetch failed: {exc}\nFalling back to demo data.", err=True)
            funding_by_year = get_demo_funding(tech_area, years)
            data_source = DATA_SOURCE_DEMO
    else:
        funding_by_year = get_demo_funding(tech_area, years)
        data_source = DATA_SOURCE_DEMO

    trend = compute_trend(tech_area, funding_by_year, data_source)
    ndaa_contexts = get_ndaa_contexts(tech_area, years, demo_mode=not live)

    return BudgetReport(
        tech_area=tech_area,
        tech_area_label=demo_tech_area_label(tech_area),
        prepared_date=str(date.today()),
        fiscal_years=years,
        trend=trend,
        ndaa_contexts=ndaa_contexts,
        plain_english="",  # filled by generate_report
        data_source=data_source,
    )


@click.group()
@click.option("--live", is_flag=True, default=False,
              help="Query USASpending.gov and congress.gov (live data)")
@click.pass_context
def cli(ctx, live):
    """P46 Defense Budget & Appropriations Tracker.

    Tracks DoD funding for AI/ML, Hypersonics, Space, and Cyber
    across FY2022-FY2026 using USASpending.gov and congress.gov data.

    Default: DEMO MODE (seeded data from public reports).
    Use --live for real-time API data (congress.gov requires CONGRESS_API_KEY).
    """
    ctx.ensure_object(dict)
    ctx.obj["live"] = live
    if live:
        click.echo("[LIVE MODE] Querying USASpending.gov and congress.gov APIs...")


@cli.command()
@click.argument("tech_area", callback=_validate_tech_area)
@click.option("--years", default=",".join(map(str, TRACKED_FISCAL_YEARS)),
              help="Comma-separated fiscal years (default: 2022,2023,2024,2025,2026)")
@click.option("--verbose", is_flag=True, help="Show NDAA context and notes")
@click.pass_context
def track(ctx, tech_area, years, verbose):
    """Track funding for a single defense technology area.

    \b
    TECH_AREA: AI/ML | Hypersonics | Space | Cyber
    """
    live = ctx.obj["live"]
    year_list = _parse_years(years)
    report = _build_report(tech_area, year_list, live)

    print_summary_banner(report.trend, report.data_source)
    print_funding_table(report.trend)

    rdte_note = rdte_share_trend(report.trend)
    click.echo(f"\nRDT&E Share: {rdte_note}")

    if verbose:
        print_ndaa_context(report.ndaa_contexts)

    print_data_disclaimer()


@cli.command()
@click.option("--years", default=",".join(map(str, TRACKED_FISCAL_YEARS)))
@click.pass_context
def compare(ctx, years):
    """Side-by-side comparison of all tracked tech areas."""
    live = ctx.obj["live"]
    year_list = _parse_years(years)
    trends = []

    for area in all_demo_tech_areas():
        report = _build_report(area, year_list, live)
        trends.append(report.trend)

    print_comparison_table(trends)
    click.echo("\nRanked by CAGR (highest first):")
    for area, cagr, trend_label in compare_areas(trends):
        click.echo(f"  {area:<14} {cagr:+.1f}% CAGR  [{trend_label}]")
    print_data_disclaimer()


@cli.command()
@click.argument("tech_area", callback=_validate_tech_area)
@click.option("--years", default=",".join(map(str, TRACKED_FISCAL_YEARS)))
@click.pass_context
def trend(ctx, tech_area, years):
    """Show detailed year-over-year trend breakdown for a tech area."""
    live = ctx.obj["live"]
    year_list = _parse_years(years)
    report = _build_report(tech_area, year_list, live)
    t = report.trend

    click.echo(f"\n{t.tech_area}: {t.overall_trend} ({t.cagr_display})")
    click.echo(f"Peak: FY{t.peak_year} at ${t.peak_total:.1f}B")
    click.echo(f"Trough: FY{t.trough_year} at ${t.trough_total:.1f}B")
    click.echo(f"Range: ${t.trough_total:.1f}B - ${t.peak_total:.1f}B")
    click.echo(f"RDT&E: {rdte_share_trend(t)}")
    click.echo("\nYear-over-year breakdown:")
    for yoy in t.yoy_changes:
        click.echo(
            f"  FY{yoy.from_year} -> FY{yoy.to_year}: "
            f"{yoy.delta_display:>8}  ({yoy.pct_display:>7})  [{yoy.trend}]"
        )
    print_data_disclaimer()


@cli.command()
@click.argument("tech_area", callback=_validate_tech_area)
@click.option("--years", default=",".join(map(str, TRACKED_FISCAL_YEARS)))
@click.pass_context
def report(ctx, tech_area, years):
    """Generate a full analyst report for a tech area.

    Uses pre-built demo report for AI/ML.
    Uses assembled structured brief for other areas.
    Use --live with ANTHROPIC_API_KEY set for Claude-generated narrative.
    """
    live = ctx.obj["live"]
    year_list = _parse_years(years)
    budget_report = _build_report(tech_area, year_list, live)

    try:
        brief, items = generate_report(budget_report, demo_mode=not live)
    except ReportGeneratorError as exc:
        click.echo(f"[ERROR] {exc}", err=True)
        sys.exit(1)

    print_report(brief, items)


@cli.command()
@click.argument("tech_area", callback=_validate_tech_area)
@click.option("--years", default=",".join(map(str, TRACKED_FISCAL_YEARS)))
@click.pass_context
def ndaa(ctx, tech_area, years):
    """Show NDAA appropriations context for a tech area across fiscal years."""
    live = ctx.obj["live"]
    year_list = _parse_years(years)
    contexts = get_ndaa_contexts(tech_area, year_list, demo_mode=not live)

    click.echo(f"\nNDAA / Appropriations Context: {tech_area}")
    click.echo("=" * 60)
    print_ndaa_context(contexts)
    print_data_disclaimer()


@cli.command()
def areas():
    """List all tracked defense technology areas."""
    click.echo("\nTracked Defense Technology Areas:")
    click.echo("-" * 40)
    for area in all_demo_tech_areas():
        info = TECH_AREAS[area]
        click.echo(f"  {area:<14}  {info['label']}")
        click.echo(f"               DoD Component: {info['dod_component']}")
        click.echo()
    click.echo(f"Fiscal years covered: FY{min(TRACKED_FISCAL_YEARS)}-FY{max(TRACKED_FISCAL_YEARS)}")


@cli.command()
def demo():
    """Full demo: show all 4 tech areas with comparison and AI/ML full report."""
    click.echo("\n" + "=" * 60)
    click.echo("P46 Defense Budget & Appropriations Tracker -- DEMO MODE")
    click.echo("=" * 60)
    click.echo("Data: Illustrative estimates from public DoD budget documents")
    click.echo(f"Coverage: FY{min(TRACKED_FISCAL_YEARS)}-FY{max(TRACKED_FISCAL_YEARS)}")
    click.echo()

    # 1. Comparison table
    trends = []
    all_reports = {}
    for area in all_demo_tech_areas():
        r = _build_report(area, list(TRACKED_FISCAL_YEARS), live=False)
        trends.append(r.trend)
        all_reports[area] = r

    print_comparison_table(trends)

    # 2. Per-area summaries
    click.echo("\nSummary by tech area (ranked by CAGR):")
    for area, cagr, trend_label in compare_areas(trends):
        r = all_reports[area]
        print_summary_banner(r.trend, r.data_source)

    # 3. AI/ML full report
    click.echo("\n" + "=" * 60)
    click.echo("FULL REPORT: AI/ML (pre-built analyst memo)")
    click.echo("=" * 60)
    ai_report = all_reports["AI/ML"]
    brief, items = generate_report(ai_report, demo_mode=True)
    print_report(brief, items)

    print_data_disclaimer()
    click.echo("\nRun individual commands:")
    click.echo("  python main.py track Hypersonics --verbose")
    click.echo("  python main.py report Cyber")
    click.echo("  python main.py ndaa Space")
    click.echo("  python main.py track AI/ML --live  (queries USASpending.gov)")


if __name__ == "__main__":
    cli(obj={})

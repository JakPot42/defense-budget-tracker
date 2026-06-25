"""Report generation for P46 Defense Budget & Appropriations Tracker.

DEMO MODE: returns pre-baked report for AI/ML; assembles structured brief
           for other tech areas from seeded data.
LIVE MODE: uses Claude Haiku to synthesize trend data into a plain-language
           analyst report; requires ANTHROPIC_API_KEY env var.
"""
from __future__ import annotations

import os
from datetime import date

from config import (
    DATA_SOURCE_DEMO, DATA_SOURCE_LIVE,
    TREND_STRONG_GROWTH, TREND_GROWING,
    TREND_CUT, TREND_STRONG_CUT, TREND_NEW_START,
    TREND_VOLATILE, TREND_FLAT,
    DATA_DISCLAIMER,
)
from models import BudgetReport, FundingTrend, NdaaContext, ProgramFunding
from seed_data import DEMO_REPORT_TEXT, DEMO_TREND_EXPLANATIONS


class ReportGeneratorError(Exception):
    """Raised when report generation fails."""


# ---------------------------------------------------------------------------
# Demo mode report assembly
# ---------------------------------------------------------------------------

def _format_funding_table(trend: FundingTrend) -> str:
    lines = [
        "  FY     RDT&E    Proc     O&M      TOTAL    YoY Change",
        "  ----   -------  -------  -------  -------  ----------",
    ]
    for fy in trend.fiscal_years:
        f = trend.funding_by_year[fy]
        if f.has_breakdown:
            rdte_str = f"${f.rdte_billions:.1f}B"
            proc_str = f"${f.procurement_billions:.1f}B"
            om_str = f"${f.om_billions:.1f}B"
        else:
            rdte_str = proc_str = om_str = "N/A"
        total_str = f"${f.total_billions:.1f}B"

        # Find YoY for this year
        yoy_str = "(baseline)"
        for yoy in trend.yoy_changes:
            if yoy.to_year == fy:
                yoy_str = f"{yoy.delta_display} ({yoy.pct_display})"
                break

        lines.append(
            f"  {fy}   {rdte_str:<7}  {proc_str:<7}  {om_str:<7}  {total_str:<7}  {yoy_str}"
        )
    return "\n".join(lines)


def _format_ndaa_section(contexts: list[NdaaContext]) -> str:
    if not contexts:
        return "  No NDAA context available."

    parts = []
    for ctx in contexts[-3:]:  # Show last 3 years
        parts.append(f"FY{ctx.fiscal_year} NDAA ({ctx.ndaa_title.split('for')[-1].strip()}):")
        for prov in ctx.key_provisions[:3]:
            parts.append(f"  -- {prov}")
        parts.append(f"  Authorization note: {ctx.authorized_amount_note}")
        parts.append("")
    return "\n".join(parts)


def _assemble_brief(report: BudgetReport) -> str:
    trend = report.trend
    tech = report.tech_area
    label = report.tech_area_label

    first = report.first_funding
    last = report.latest_funding
    first_total = first.total_billions if first else 0.0
    last_total = last.total_billions if last else 0.0

    if first_total > 0:
        pct_growth = (last_total - first_total) / first_total * 100
        growth_str = f"+{pct_growth:.0f}%" if pct_growth >= 0 else f"{pct_growth:.0f}%"
    else:
        growth_str = "N/A"

    table = _format_funding_table(trend)
    ndaa_section = _format_ndaa_section(report.ndaa_contexts)
    extra_explain = DEMO_TREND_EXPLANATIONS.get(tech, "")

    lines = [
        "=" * 77,
        "DEFENSE BUDGET TREND ANALYSIS -- ILLUSTRATIVE DEMO REPORT",
        f"TECHNOLOGY AREA: {label} ({tech})",
        f"FISCAL YEARS: FY{min(report.fiscal_years)}-FY{max(report.fiscal_years)}",
        f"PREPARED: Defense Budget Tracker (P46) -- DEMO MODE  DATE: {report.prepared_date}",
        "=" * 77,
        "NOTICE: DEMO DATA derived from public DoD budget documents and CRS reports.",
        DATA_DISCLAIMER[:120],
        "=" * 77,
        "",
        "I. EXECUTIVE SUMMARY",
        "",
        f"The DoD {label} portfolio grew from ${first_total:.1f}B (FY{min(report.fiscal_years)}) "
        f"to ${last_total:.1f}B (FY{max(report.fiscal_years)}) -- a CAGR of "
        f"approximately {trend.cagr:.1f}% over {len(report.fiscal_years)-1} years.",
        "",
        f"OVERALL TREND: {trend.overall_trend} ({trend.cagr_display})",
        f"FY{min(report.fiscal_years)} TOTAL: ${first_total:.1f}B  |  "
        f"FY{max(report.fiscal_years)} TOTAL: ${last_total:.1f}B  |  GROWTH: {growth_str}",
        "",
        "II. YEAR-OVER-YEAR FUNDING TREND",
        "",
        table,
        "",
        "III. NDAA / APPROPRIATIONS CONTEXT",
        "",
        ndaa_section,
        "IV. PLAIN-LANGUAGE INTERPRETATION",
        "",
        extra_explain if extra_explain else (
            f"No pre-built narrative for {tech}. Run in live mode with "
            "ANTHROPIC_API_KEY set for Claude-generated analysis."
        ),
        "",
        "=" * 77,
        f"DATA SOURCE: DEMO MODE | OVERALL TREND: {trend.overall_trend} | "
        f"CAGR: {trend.cagr_display}",
        "=" * 77,
    ]
    return "\n".join(lines)


def _build_action_items(report: BudgetReport) -> list[str]:
    """Generate analyst action items based on trend and NDAA context."""
    items = []
    trend = report.trend
    tech = report.tech_area

    if trend.overall_trend in (TREND_STRONG_GROWTH, TREND_GROWING):
        items.append(
            f"1. Track {tech} budget request in next President's Budget for "
            f"continuation of {trend.cagr_display} growth trajectory."
        )

    if trend.overall_trend in (TREND_CUT, TREND_STRONG_CUT):
        items.append(
            f"1. Investigate cause of {tech} funding reduction -- program cancellation, "
            "re-prioritization, or continuing resolution constraint?"
        )

    if trend.overall_trend == TREND_VOLATILE:
        items.append(
            f"1. {tech} shows volatile funding (alternating growth/cuts) -- "
            "review program milestone events for correlation with budget swings."
        )

    # Hypersonics-specific: procurement surge signal
    last = report.latest_funding
    if last and last.has_breakdown and last.procurement_billions is not None:
        if last.procurement_billions > (last.total_billions * 0.30):
            items.append(
                f"2. Procurement now {last.procurement_pct:.0f}% of {tech} total -- "
                "program is transitioning from R&D to production. Identify prime contractors."
            )

    # NDAA context signal
    if report.ndaa_contexts:
        latest_ctx = max(report.ndaa_contexts, key=lambda c: c.fiscal_year)
        if latest_ctx.key_provisions:
            items.append(
                f"3. Review NDAA provision: {latest_ctx.key_provisions[0][:80]}..."
            )

    if not items:
        items.append(f"1. Monitor {tech} for changes in next budget cycle.")

    return items


# ---------------------------------------------------------------------------
# Live mode: Claude synthesis
# ---------------------------------------------------------------------------

def _live_synthesis(report: BudgetReport) -> tuple[str, list[str]]:
    """Use Claude Haiku to write a plain-language budget analysis."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ReportGeneratorError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Set it or run without --live flag to use demo mode."
        )

    try:
        import anthropic  # type: ignore
    except ImportError:
        raise ReportGeneratorError(
            "anthropic library not installed. Run: pip install anthropic"
        ) from None

    trend = report.trend
    tech = report.tech_area

    funding_lines = []
    for fy in trend.fiscal_years:
        f = trend.funding_by_year[fy]
        funding_lines.append(
            f"FY{fy}: ${f.total_billions:.1f}B total"
            + (f" (RDT&E ${f.rdte_billions:.1f}B, Proc ${f.procurement_billions:.1f}B, "
               f"O&M ${f.om_billions:.1f}B)" if f.has_breakdown else " (contract obligations)")
        )

    yoy_lines = []
    for yoy in trend.yoy_changes:
        yoy_lines.append(
            f"FY{yoy.from_year}->FY{yoy.to_year}: {yoy.pct_display} ({yoy.trend})"
        )

    ndaa_lines = []
    for ctx in report.ndaa_contexts[-3:]:
        ndaa_lines.append(f"FY{ctx.fiscal_year} NDAA provisions: " + "; ".join(ctx.key_provisions[:2]))

    prompt = f"""You are a defense budget analyst. Write a plain-language analysis of DoD funding
for the following technology area. Do NOT make attribution claims or policy recommendations beyond
what the data supports. Use hedged language: "consistent with", "suggests", "may indicate".
Do NOT use bullet points or markdown -- write in flowing paragraphs.
Keep the total response under 400 words.

TECHNOLOGY AREA: {tech} ({report.tech_area_label})

FUNDING DATA:
{chr(10).join(funding_lines)}

YEAR-OVER-YEAR:
{chr(10).join(yoy_lines)}

OVERALL TREND: {trend.overall_trend} | CAGR: {trend.cagr_display}

NDAA CONTEXT:
{chr(10).join(ndaa_lines)}

Write 3-4 paragraphs explaining:
1. What the funding trend means operationally for this technology area
2. What the RDT-E vs. Procurement composition shift tells us about program maturity
3. What the NDAA provisions signal about Congressional and DoD priorities"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    narrative = message.content[0].text.strip()

    # Build the structured report with the narrative inserted
    brief = _assemble_brief_with_narrative(report, narrative)
    items = _build_action_items(report)
    return brief, items


def _assemble_brief_with_narrative(report: BudgetReport, narrative: str) -> str:
    trend = report.trend
    table = _format_funding_table(trend)
    ndaa_section = _format_ndaa_section(report.ndaa_contexts)

    first = report.first_funding
    last = report.latest_funding
    first_total = first.total_billions if first else 0.0
    last_total = last.total_billions if last else 0.0
    pct_growth = ((last_total - first_total) / first_total * 100) if first_total > 0 else 0.0
    growth_str = f"+{pct_growth:.0f}%" if pct_growth >= 0 else f"{pct_growth:.0f}%"

    lines = [
        "=" * 77,
        "DEFENSE BUDGET TREND ANALYSIS -- LIVE MODE",
        f"TECHNOLOGY AREA: {report.tech_area_label} ({report.tech_area})",
        f"FISCAL YEARS: FY{min(report.fiscal_years)}-FY{max(report.fiscal_years)}",
        f"PREPARED: Defense Budget Tracker (P46)  DATE: {report.prepared_date}",
        "=" * 77,
        "",
        "I. FUNDING TREND",
        "",
        table,
        "",
        f"OVERALL TREND: {trend.overall_trend} ({trend.cagr_display})  |  "
        f"TOTAL CHANGE: ${first_total:.1f}B -> ${last_total:.1f}B ({growth_str})",
        "",
        "II. NDAA / APPROPRIATIONS CONTEXT",
        "",
        ndaa_section,
        "III. ANALYST NARRATIVE (Claude-synthesized)",
        "",
        narrative,
        "",
        "=" * 77,
        "DATA: USASpending.gov contract obligations + congress.gov NDAA summaries",
        "=" * 77,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def generate_report(report: BudgetReport, *, demo_mode: bool = True) -> tuple[str, list[str]]:
    """Generate a budget analysis report.

    Returns (brief_text, action_items_list).
    In demo mode, returns pre-built text for AI/ML and assembles for others.
    In live mode, calls Claude Haiku for narrative synthesis.
    """
    if demo_mode:
        if report.tech_area == "AI/ML":
            items = _build_action_items(report)
            return DEMO_REPORT_TEXT, items
        brief = _assemble_brief(report)
        items = _build_action_items(report)
        return brief, items
    else:
        return _live_synthesis(report)

"""
Seeded demo data for P46 Defense Budget & Appropriations Tracker.

Figures are illustrative estimates derived from public DoD budget documents,
Congressional Research Service (CRS) reports, OUSD(Comptroller) budget
justification documents, and news reporting. All values are in $B USD.

Sources consulted:
  - DoD Fiscal Year 2024 Budget Overview (OUSD Comptroller, March 2023)
  - DoD Fiscal Year 2025 Budget Overview (OUSD Comptroller, March 2024)
  - CRS "Defense Primer: Research, Development, Test, and Evaluation (RDT&E)"
  - CRS "Artificial Intelligence and National Security" (Dec 2023)
  - CRS "Hypersonic Weapons: Background and Issues for Congress" (Mar 2024)
  - CRS "Space Force: Selected Issues for Congress" (Jan 2024)
  - CRS "Defense Cybersecurity: Background and Issues for Congress" (Feb 2024)
  - FY2024 NDAA (P.L. 118-31) Section Index
  - FY2025 NDAA (P.L. 118-159) Section Index
  - FY2026 NDAA (pending, illustrative authorization levels)
"""

from config import (
    DATA_SOURCE_DEMO, TREND_STRONG_GROWTH, TREND_GROWING,
    CAGR_STRONG_GROWTH, CAGR_GROWING,
)

# ---------------------------------------------------------------------------
# FUNDING DATA: 4 tech areas x FY2022-2026 x {rdte, proc, om, total}
# All values in $B USD (billions)
# ---------------------------------------------------------------------------

DEMO_FUNDING: dict[str, dict[int, dict]] = {
    "AI/ML": {
        2022: {"rdte": 1.2, "proc": 0.3, "om": 0.2, "total": 1.7,
               "notes": "JAIC/CDAO stood up; AI R&D ramp begins"},
        2023: {"rdte": 1.5, "proc": 0.4, "om": 0.3, "total": 2.2,
               "notes": "CDAO fully operational; AI-enabled C2 programs started"},
        2024: {"rdte": 1.8, "proc": 0.6, "om": 0.4, "total": 2.8,
               "notes": "NDAA Sec. 225 CoE; AI red-teaming mandate; procurement surge begins"},
        2025: {"rdte": 2.1, "proc": 0.9, "om": 0.6, "total": 3.6,
               "notes": "Expanded CDAO authorities; AI-enabled ISR and logistics scaling"},
        2026: {"rdte": 2.4, "proc": 1.2, "om": 0.8, "total": 4.4,
               "notes": "AI procurement mainstreams; digital twin and autonomous systems grow"},
    },
    "Hypersonics": {
        2022: {"rdte": 2.1, "proc": 0.0, "om": 0.1, "total": 2.2,
               "notes": "All-RDT&E phase; CPS/LRHW/ARRW programs in parallel development"},
        2023: {"rdte": 2.9, "proc": 0.2, "om": 0.1, "total": 3.2,
               "notes": "LRHW moves to limited production; ARRW test failures noted"},
        2024: {"rdte": 3.4, "proc": 0.5, "om": 0.2, "total": 4.1,
               "notes": "HACM funded; ARRW decommissioned; CPS procurement begins"},
        2025: {"rdte": 3.8, "proc": 1.1, "om": 0.3, "total": 5.2,
               "notes": "LRHW Battery #1 procurement; NDAA adds $500M above request"},
        2026: {"rdte": 4.2, "proc": 2.3, "om": 0.4, "total": 6.9,
               "notes": "Procurement overtakes RDT&E growth; HACM scaling"},
    },
    "Space": {
        2022: {"rdte": 6.1, "proc": 8.2, "om": 5.4, "total": 19.7,
               "notes": "Space Force Year 2; SDA Tranche 0 satellites launched"},
        2023: {"rdte": 6.8, "proc": 9.1, "om": 5.8, "total": 21.7,
               "notes": "SDA Tranche 1 contracts awarded; NSSL Phase 2 ongoing"},
        2024: {"rdte": 7.2, "proc": 10.4, "om": 6.2, "total": 23.8,
               "notes": "Space Force $30.3B total; NextGen OPIR; GPS III follow-on"},
        2025: {"rdte": 7.8, "proc": 11.8, "om": 6.8, "total": 26.4,
               "notes": "SDA Tranche 2; commercial space integration; resilient architecture"},
        2026: {"rdte": 8.2, "proc": 13.1, "om": 7.2, "total": 28.5,
               "notes": "Space domain awareness modernization; proliferated LEO constellation"},
    },
    "Cyber": {
        2022: {"rdte": 3.1, "proc": 1.8, "om": 8.4, "total": 13.3,
               "notes": "CYBERCOM CMF full operational capability; Zero Trust planning"},
        2023: {"rdte": 3.4, "proc": 2.1, "om": 8.9, "total": 14.4,
               "notes": "Unified Platform contract awarded; cyber workforce retention"},
        2024: {"rdte": 3.8, "proc": 2.5, "om": 9.3, "total": 15.6,
               "notes": "NDAA expands Title 10 authorities; CMMC 2.0 implementation"},
        2025: {"rdte": 4.1, "proc": 2.8, "om": 9.8, "total": 16.7,
               "notes": "AI-assisted threat detection pilots; quantum-resistant crypto transition"},
        2026: {"rdte": 4.4, "proc": 3.1, "om": 10.2, "total": 17.7,
               "notes": "Cyber operations AI integration; critical infrastructure defense scaling"},
    },
}

# ---------------------------------------------------------------------------
# NDAA CONTEXT: key provisions per tech area per fiscal year
# ---------------------------------------------------------------------------

DEMO_NDAA_CONTEXT: dict[str, dict[int, dict]] = {
    "AI/ML": {
        2022: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2022",
            "public_law": "P.L. 117-81",
            "key_provisions": [
                "Sec. 236: Required DoD AI strategy update and CDAO establishment",
                "Sec. 1521: Established AI ethics principles adoption timeline",
                "Sec. 1506: Required GAO review of JAIC transition to CDAO",
            ],
            "authorized_amount_note": "No single line item; AI spread across program elements",
        },
        2023: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2023",
            "public_law": "P.L. 117-263",
            "key_provisions": [
                "Sec. 1506: CDAO fully authorized; expanded data and AI workforce",
                "Sec. 1522: AI testing and evaluation standards required",
                "Sec. 1545: Autonomous systems safety review board established",
            ],
            "authorized_amount_note": "$1.8B across AI/autonomous systems program elements",
        },
        2024: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2024",
            "public_law": "P.L. 118-31",
            "key_provisions": [
                "Sec. 225: DoD AI/ML Center of Excellence established",
                "Sec. 1082: CDAO expanded authorities for data access and AI deployment",
                "Sec. 1516: AI red-teaming required for critical weapon systems",
                "Sec. 232: AI-enabled ISR integration with combatant commands",
            ],
            "authorized_amount_note": "$2.1B across AI/ML-related program elements (CRS estimate)",
        },
        2025: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2025",
            "public_law": "P.L. 118-159",
            "key_provisions": [
                "Sec. 1521: AI for logistics and predictive maintenance scaling",
                "Sec. 248: Autonomous systems acquisition authorities expanded",
                "Sec. 1093: AI trust and explainability standards for autonomous weapons",
                "Sec. 834: CDAO budget lines ring-fenced from general IT cuts",
            ],
            "authorized_amount_note": "$2.8B+ requested by DoD for AI/autonomous systems",
        },
        2026: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2026",
            "public_law": "P.L. 119-XX (illustrative)",
            "key_provisions": [
                "Sec. 221: AI-enabled autonomous systems full procurement authority",
                "Sec. 1508: Joint AI operations center (JAOC) funding authorized",
                "Sec. 914: Digital engineering mandate extended to all major programs",
                "Sec. 1544: AI adversarial testing for deployed systems required annually",
            ],
            "authorized_amount_note": "$3.5B+ projected for AI/ML across DoD (illustrative)",
        },
    },
    "Hypersonics": {
        2022: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2022",
            "public_law": "P.L. 117-81",
            "key_provisions": [
                "Sec. 247: Conventional Prompt Strike (CPS) program continuation",
                "Sec. 1688: Hypersonic industrial base assessment required",
                "Sec. 219: Long Range Hypersonic Weapon (LRHW) milestone review",
            ],
            "authorized_amount_note": "$2.2B across CPS, LRHW, ARRW program elements",
        },
        2023: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2023",
            "public_law": "P.L. 117-263",
            "key_provisions": [
                "Sec. 219: LRHW limited production authorized following successful tests",
                "Sec. 248: Air-Launched Rapid Response Weapon (ARRW) test failure review",
                "Sec. 1561: Hypersonic test range capacity expansion funded",
            ],
            "authorized_amount_note": "$2.9B hypersonics portfolio; LRHW procurement begins",
        },
        2024: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2024",
            "public_law": "P.L. 118-31",
            "key_provisions": [
                "Sec. 247: ARRW program decommissioned after persistent test failures",
                "Sec. 228: Hypersonic Attack Cruise Missile (HACM) development funded ($700M)",
                "Sec. 219: CPS procurement ramp authorized; Conventional Prompt Strike production",
                "Sec. 1691: Hypersonic defense interceptor RDT&E initiated",
            ],
            "authorized_amount_note": "$3.8B hypersonics; shift from ARRW to HACM accelerates",
        },
        2025: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2025",
            "public_law": "P.L. 118-159",
            "key_provisions": [
                "Sec. 249: LRHW Battery #1 full procurement; Battery #2 authorized",
                "Added $500M above DoD request for hypersonic strike acceleration",
                "Sec. 223: Hypersonic common infrastructure (test, components) established",
                "Sec. 1564: Allied hypersonic cooperation (AUKUS) provisions",
            ],
            "authorized_amount_note": "$5.0B hypersonics; Congress adds $500M above request",
        },
        2026: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2026",
            "public_law": "P.L. 119-XX (illustrative)",
            "key_provisions": [
                "Sec. 215: Hypersonic defense interceptor procurement initiated",
                "Sec. 247: HACM rate production approved; USAF fielding timeline set",
                "Sec. 1688: Hypersonic industrial base sustained sourcing requirements",
                "Sec. 228: Hypersonic strike glide body common component acquisition",
            ],
            "authorized_amount_note": "$6.5B+ projected; procurement overtakes RDT&E in spend (illustrative)",
        },
    },
    "Space": {
        2022: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2022",
            "public_law": "P.L. 117-81",
            "key_provisions": [
                "Sec. 1601: Space Force Year 2 organizational provisions",
                "Sec. 1614: Space Development Agency (SDA) Tranche 0 satellite oversight",
                "Sec. 1611: National Security Space Launch (NSSL) Phase 2 contract oversight",
            ],
            "authorized_amount_note": "$19B+ Space Force; GPS III, SBIRS, NSSL major programs",
        },
        2023: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2023",
            "public_law": "P.L. 117-263",
            "key_provisions": [
                "Sec. 1602: SDA Tranche 1 production contracts authorized",
                "Sec. 1614: Overhead Persistent Infrared (OPIR) program restructure",
                "Sec. 1631: Commercial satellite data integration authorities expanded",
            ],
            "authorized_amount_note": "$21B+ Space Force; SDA scaling; NSSL Phase 2 ongoing",
        },
        2024: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2024",
            "public_law": "P.L. 118-31",
            "key_provisions": [
                "Sec. 1601: Space Force $30.3B total authorized",
                "Sec. 1614: Next-Generation OPIR constellation (FORGE) initial funding",
                "Sec. 1623: Space Warfighting Analysis Center (SWAC) provisions",
                "Sec. 1637: Space domain awareness (SDA) sensor network expansion",
            ],
            "authorized_amount_note": "$30.3B Space Force; NextGen OPIR and GPS III follow-on major adds",
        },
        2025: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2025",
            "public_law": "P.L. 118-159",
            "key_provisions": [
                "Sec. 1601: Space Force $33.1B requested; $32.8B authorized",
                "Sec. 1618: SDA Tranche 2 procurement contracts; proliferated LEO expansion",
                "Sec. 1641: Commercial Space Integration Initiative authorities",
                "Sec. 1632: Resilient GPS architecture (alternative PNT) funded",
            ],
            "authorized_amount_note": "$32.8B Space Force; SDA Tranche 2 proliferated LEO constellation",
        },
        2026: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2026",
            "public_law": "P.L. 119-XX (illustrative)",
            "key_provisions": [
                "Sec. 1601: Space Force $35.2B projected authorization",
                "Sec. 1622: Space domain awareness: Ground-Based Electro-Optical Deep Space Surveillance (GEODSS) modernization",
                "Sec. 1644: Cislunar space awareness provisions (new)",
                "Sec. 1611: NSSL Phase 3 Lane 2 competitive launch services expansion",
            ],
            "authorized_amount_note": "$35B+ projected; cislunar and proliferated LEO drive growth (illustrative)",
        },
    },
    "Cyber": {
        2022: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2022",
            "public_law": "P.L. 117-81",
            "key_provisions": [
                "Sec. 1521: CYBERCOM Cyber Mission Force (CMF) at full operational capability",
                "Sec. 1508: Zero Trust architecture adoption timeline required",
                "Sec. 1502: Cyber posture review and persistent engagement doctrine codified",
            ],
            "authorized_amount_note": "$13.3B cybersecurity across DoD programs",
        },
        2023: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2023",
            "public_law": "P.L. 117-263",
            "key_provisions": [
                "Sec. 1533: CYBERCOM Unified Platform contract oversight",
                "Sec. 1512: Cyber workforce retention bonuses and career pipeline",
                "Sec. 1547: CMMC 2.0 implementation mandate for defense contractors",
            ],
            "authorized_amount_note": "$14B+ cyber; Unified Platform procurement ramp",
        },
        2024: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2024",
            "public_law": "P.L. 118-31",
            "key_provisions": [
                "Sec. 1502: CYBERCOM expanded Title 10 war powers authorities",
                "Sec. 1543: Cyber warfare roadmap required from SecDef within 180 days",
                "Sec. 1521: Zero Trust full deployment mandate across DoD by 2027",
                "Sec. 1538: Critical infrastructure cyber defense cooperation with DHS",
            ],
            "authorized_amount_note": "$15.6B cyber; Title 10 authorities expansion most significant provision",
        },
        2025: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2025",
            "public_law": "P.L. 118-159",
            "key_provisions": [
                "Sec. 1544: AI-assisted threat detection and hunt operations funded",
                "Sec. 1502: Quantum-resistant cryptography transition timeline mandated",
                "Sec. 1516: Cyber resilience for nuclear command-and-control (NC3)",
                "Sec. 1538: Cyber Trust Mark integration with defense supply chain",
            ],
            "authorized_amount_note": "$16.7B cyber; AI and quantum-resistant crypto are new major investments",
        },
        2026: {
            "ndaa_title": "National Defense Authorization Act for Fiscal Year 2026",
            "public_law": "P.L. 119-XX (illustrative)",
            "key_provisions": [
                "Sec. 1521: AI-enabled cyber operations full authority for CYBERCOM",
                "Sec. 1543: Offensive cyber capabilities modernization; hunt-forward expansion",
                "Sec. 1538: Critical infrastructure sector-specific cyber defense scaling",
                "Sec. 1512: Cyber operator retention: expanded bonus structure",
            ],
            "authorized_amount_note": "$17.5B+ projected; AI integration in cyber operations drives RDT&E (illustrative)",
        },
    },
}

# ---------------------------------------------------------------------------
# PRE-BAKED DEMO REPORT: AI/ML tech area (ASCII-safe)
# ---------------------------------------------------------------------------

DEMO_REPORT_TEXT = """\
=============================================================================
DEFENSE BUDGET TREND ANALYSIS -- ILLUSTRATIVE DEMO REPORT
TECHNOLOGY AREA: Artificial Intelligence and Machine Learning (AI/ML)
FISCAL YEARS: FY2022 - FY2026
PREPARED: Defense Budget Tracker (P46) -- DEMO MODE
=============================================================================
NOTICE: This report uses ILLUSTRATIVE DEMO DATA derived from public DoD budget
documents, CRS reports, and NDAA section indexes. Figures are estimates, not
official DoD numbers. Live mode queries USASpending.gov and congress.gov APIs.
All values in $B USD (billions). RDT&E/Procurement/O&M breakdown in demo only.
=============================================================================

I. EXECUTIVE SUMMARY

The DoD AI/ML portfolio has grown from an estimated $1.7B in FY2022 to $4.4B
in FY2026 -- a compound annual growth rate of approximately 26.9%. This is
among the fastest-growing technology investment areas across the defense
budget. The growth reflects a strategic shift: early years (FY2022-2023) were
dominated by RDT&E as CDAO (Chief Digital and AI Office) stood up; by FY2026,
procurement spending has nearly quadrupled from its FY2022 baseline as AI
systems move from prototype to fielded capability.

OVERALL TREND: STRONG GROWTH (26.9% CAGR)
FY2022 TOTAL: $1.7B  |  FY2026 TOTAL: $4.4B  |  GROWTH: +$2.7B (+158%)

II. YEAR-OVER-YEAR FUNDING TREND

  FY     RDT&E    Proc     O&M      TOTAL    YoY Change
  ----   -------  -------  -------  -------  ----------
  2022   $1.2B    $0.3B    $0.2B    $1.7B    (baseline)
  2023   $1.5B    $0.4B    $0.3B    $2.2B    +$0.5B (+29%)
  2024   $1.8B    $0.6B    $0.4B    $2.8B    +$0.6B (+27%)
  2025   $2.1B    $0.9B    $0.6B    $3.6B    +$0.8B (+29%)
  2026   $2.4B    $1.2B    $0.8B    $4.4B    +$0.8B (+22%)

RDT&E has grown steadily but its SHARE of total is declining (71% in FY2022
vs. 55% in FY2026) as procurement scales. This is the classic technology
maturation pattern: heavy R&D first, then procurement as systems are fielded.
O&M is growing at 32% per year, consistent with an expanding fleet of deployed
AI tools requiring maintenance, licensing, and operator support.

III. BUDGET CATEGORY ANALYSIS

  RDT&E (FY22-FY26): +100% -- Basic and applied research through CDAO, DARPA,
  and service labs. Key programs: Project Maven (AI-enabled ISR), AI-enabled C2,
  predictive maintenance algorithms, digital engineering tools.

  Procurement (FY22-FY26): +300% -- Fastest-growing category. AI software
  licenses, AI-enabled sensors, autonomous logistics systems, digital twin
  platforms. The shift from prototype to production is the defining trend.

  O&M (FY22-FY26): +300% -- Growing in lock-step with procurement. Sustaining
  deployed AI systems, training operators, maintaining data pipelines.
  O&M growth is a leading indicator of how many AI systems are actually fielded.

IV. NDAA / APPROPRIATIONS CONTEXT (FY2024-FY2026)

FY2024 NDAA (P.L. 118-31):
  -- Sec. 225: Established DoD AI/ML Center of Excellence under CDAO
  -- Sec. 1082: Expanded CDAO authorities for cross-DoD data access
  -- Sec. 1516: Required AI red-teaming for critical weapon systems before
     milestone reviews -- first formal adversarial AI testing mandate
  -- Sec. 232: AI-enabled ISR integration required with all combatant commands

FY2025 NDAA (P.L. 118-159):
  -- Sec. 1521: AI for logistics and predictive maintenance scaling -- expanded
     beyond pilots to program-of-record status
  -- Sec. 248: Autonomous systems acquisition authorities expanded; removed
     human-in-the-loop requirement for non-lethal autonomous logistics
  -- Sec. 1093: AI trust and explainability standards for autonomous weapons

FY2026 NDAA (illustrative):
  -- Sec. 221: Full procurement authority for AI-enabled autonomous systems
  -- Sec. 1508: Joint AI Operations Center (JAOC) funding authorized
  -- Sec. 914: Digital engineering mandate extended to all major programs

V. PLAIN-LANGUAGE INTERPRETATION

What this funding trend means operationally:

  1. AI/ML is no longer a pilot program -- it is a program of record. The shift
     from RDT&E-dominant (FY2022) to roughly balanced RDT&E/Procurement (FY2026)
     means DoD is buying AI systems, not just researching them. Contractors who
     built prototypes are winning production contracts.

  2. The FY2024 NDAA red-teaming mandate is structurally significant. It means
     every major AI-enabled weapon system must now pass adversarial testing before
     a Milestone B/C decision. This adds cost and schedule but raises the bar for
     system reliability.

  3. O&M growth tracks fielded AI deployments. The $0.8B in FY2026 O&M suggests
     hundreds of deployed AI applications are now in sustainment. This is the
     largest hidden cost of AI adoption: keeping models current, pipelines clean,
     and operators trained as the threat environment evolves.

  4. CDAO's expanded authorities (FY2024 Sec. 1082) resolved a key bottleneck:
     data access. Before this, services controlled their own data and CDAO could
     not build cross-domain AI models. Post-FY2024, DoD has a legal mandate for
     data sharing, which unlocks the most valuable AI use cases.

  5. The FY2025 autonomous logistics provision (no human-in-the-loop for non-lethal
     autonomy) is the first step toward fully autonomous resupply chains. Expect
     procurement for autonomous ground vehicles and drone logistics to accelerate
     in FY2026 and beyond.

VI. PROGRAM-AREA BREAKDOWN (KEY INVESTMENTS)

  CDAO Portfolio (est. $400M/yr by FY2024): Data fabrics, enterprise AI tools,
  Project Thunderstruck (AI-enabled targeting), AI Safety Council.

  Project Maven (DARPA -> Army -> CDAO, est. $150M/yr): AI-enabled ISR for
  object recognition in imagery. Operational in CENTCOM, INDOPACOM.

  AI-Enabled Command and Control (est. $300M/yr by FY2025): Joint AI command
  decision support systems; JADC2 AI layer. Most classified elements.

  Digital Engineering (est. $250M/yr): Model-based systems engineering,
  digital twin platforms for major programs (F-35, B-21, CVN-80).

  Autonomous Systems R&D (est. $500M/yr by FY2025): Collaborative Combat
  Aircraft (CCA), autonomous logistics vehicles, maritime autonomous systems.

VII. RECOMMENDED NEXT STEPS (ANALYST GUIDANCE)

  1. Monitor CDAO FY2027 budget request (to be released March 2026) for
     continuation of AI procurement ramp or signs of plateau.

  2. Track the FY2024 NDAA Sec. 1516 red-teaming results -- if AI systems
     fail adversarial testing, procurement schedules could slip.

  3. Review DoD AI adoption reports (required by NDAA) for which programs
     achieved Milestone B with AI components -- these signal the next
     procurement wave.

  4. Compare O&M growth rate against new AI system fieldings to assess cost
     per-system-sustained -- a metric that will drive future budget trade-offs.

=============================================================================
DATA SOURCE: DEMO MODE -- Illustrative estimates from public sources
LIVE MODE: Set DEMO_MODE=False and optionally CONGRESS_API_KEY env var
USASpending.gov: https://api.usaspending.gov (free, no auth)
congress.gov API: https://api.congress.gov (free API key required)
=============================================================================
"""

# ---------------------------------------------------------------------------
# DEMO AREA ORDERING (for compare / multi-area display)
# ---------------------------------------------------------------------------
DEMO_AREA_ORDER = ["AI/ML", "Hypersonics", "Space", "Cyber"]

# ---------------------------------------------------------------------------
# TREND EXPLANATIONS: plain-language snippets for each tech area
# Used by assembler when demo_mode=True and area != AI/ML
# ---------------------------------------------------------------------------

DEMO_TREND_EXPLANATIONS: dict[str, str] = {
    "Hypersonics": (
        "Hypersonics funding grew at ~33% CAGR from FY2022 to FY2026 -- the fastest "
        "growth rate in this portfolio. Crucially, the budget composition shifted: "
        "FY2022 was entirely RDT&E (no procurement), while FY2026 has procurement "
        "($2.3B) surpassing RDT&E ($4.2B) in absolute growth. This reflects the "
        "transition from parallel development programs (CPS, LRHW, ARRW) to "
        "selective fielding. ARRW's cancellation in FY2024 reallocated funds to "
        "HACM and LRHW, concentrating bets on proven designs. The NDAA's $500M "
        "FY2025 add-above-request signals strong Congressional appetite -- unusual "
        "for a still-maturing technology. The key operational implication: by FY2026, "
        "DoD will have at least one fielded conventional hypersonic capability "
        "(LRHW), with Air Force and Navy variants following."
    ),
    "Space": (
        "Space funding grew at ~9.7% CAGR from FY2022 to FY2026, the slowest of "
        "the four areas but from the largest base (~$20B). Space Force is now the "
        "fastest-growing military service by budget. Procurement dominates at ~46% "
        "of total, driven by large platform programs (GPS III, NSSL launches, SDA "
        "constellation). The RDT&E-to-Procurement ratio is stable, suggesting Space "
        "Force is in sustained production rather than rapid development. The Space "
        "Development Agency (SDA) proliferated LEO constellation is the defining "
        "structural shift: instead of a few expensive exquisite satellites, DoD is "
        "building hundreds of cheaper satellites with rapid reconstitution. This "
        "architecture is harder to hold at risk. The FY2026 cislunar provisions "
        "signal the next frontier: DoD is beginning to budget for space domain "
        "awareness beyond GEO orbit."
    ),
    "Cyber": (
        "Cyber funding grew at ~7.4% CAGR from FY2022 to FY2026 -- steady but not "
        "dramatic. The composition reveals why: O&M dominates at ~57% of total by "
        "FY2026, reflecting the labor-intensive nature of cyber operations. CYBERCOM's "
        "Cyber Mission Force is fully staffed and in sustained operations -- those "
        "operators generate O&M costs annually. RDT&E is growing at ~9.1% CAGR as "
        "DoD invests in AI-assisted threat detection, quantum-resistant cryptography, "
        "and next-generation Unified Platform capabilities. The FY2024 Title 10 "
        "authority expansion is the most strategically significant provision: it "
        "gave CYBERCOM legal authority for more proactive operations without requiring "
        "Title 50 (covert action) authorities. In practical terms, this means faster "
        "hunt-forward operations and a lower approval threshold for defensive actions "
        "outside US networks."
    ),
}

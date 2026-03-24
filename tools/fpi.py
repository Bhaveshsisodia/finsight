"""
FPI NSDL — LangChain Tools
===========================
Wraps each node function as a @tool so any LangGraph agent
can call them directly via tool-calling.

Usage in your agent:
    from fpi_tools import (
        tool_detect_dates,
        tool_fetch_reports,
        tool_parse_tables,
        tool_extract_data,
        tool_generate_insights,
        tool_save_reports,
        tool_run_full_pipeline,   # ← runs everything in one shot
        ALL_FPI_TOOLS,            # ← list to pass to your agent
    )
"""

from __future__ import annotations
from datetime import date
from typing import Optional
from langchain_core.tools import tool

# import your node functions
from tools.fpi_nodes import (
    FPIState,
    detect_dates,
    fetch_reports,
    parse_tables,
    extract_data,
    generate_insights,
    save_reports,
    run,
)


# ── shared in-memory state store ──────────────────────────────────────────────
# Agents call tools one at a time; we persist state between calls here.
_state: FPIState = {}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 1 — detect_dates                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_detect_dates(today_str: Optional[str] = None) -> dict:
    """
    Find the 2 most recent FPI NSDL report dates by scanning backwards from today.
    Performs HTTP HEAD checks on NSDL URLs — no download yet.

    Args:
        today_str: Date in YYYY-MM-DD format to search from.
                   Defaults to today if not provided.

    Returns:
        report_dates  : list of date strings found (newest first)
        date_urls     : dict mapping date_str → full URL
        dates_checked : log of every URL checked and its HTTP status
    """
    global _state
    _state["today"] = (
        date.fromisoformat(today_str) if today_str else date.today()
    )
    result = detect_dates(_state)
    _state.update(result)

    return {
        "report_dates":  [str(d) for d in result.get("report_dates", [])],
        "date_urls":     result.get("date_urls", {}),
        "dates_checked": result.get("dates_checked", []),
        "status":        "found" if result.get("report_dates") else "no_reports_found",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 2 — fetch_reports                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_fetch_reports() -> dict:
    """
    Download the HTML for each report date found by tool_detect_dates.
    Must be called AFTER tool_detect_dates.

    Returns:
        fetched_dates : list of date strings successfully downloaded
        byte_sizes    : dict mapping date_str → file size in bytes
        fetch_errors  : list of any errors encountered
    """
    global _state
    result = fetch_reports(_state)
    _state.update(result)

    raw_html = result.get("raw_html", {})
    return {
        "fetched_dates": list(raw_html.keys()),
        "byte_sizes":    {ds: len(html) for ds, html in raw_html.items()},
        "fetch_errors":  result.get("fetch_errors", []),
        "status":        "ok" if raw_html else "failed",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 3 — parse_tables                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_parse_tables() -> dict:
    """
    Parse the 98-column NSDL HTML table, skipping 4 merged header rows.
    Must be called AFTER tool_fetch_reports.

    Returns:
        parsed_dates : list of date strings successfully parsed
        row_counts   : dict mapping date_str → number of data rows
        parse_errors : list of any errors
    """
    global _state
    result = parse_tables(_state)
    _state.update(result)

    raw_dfs = result.get("raw_dataframes", {})
    return {
        "parsed_dates": list(raw_dfs.keys()),
        "row_counts":   {ds: len(rows) for ds, rows in raw_dfs.items()},
        "parse_errors": result.get("parse_errors", []),
        "status":       "ok" if raw_dfs else "failed",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 4 — extract_data                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_extract_data() -> dict:
    """
    Map the raw 98-column rows to semantic fields:
    F1/F2 Net Investment, Equity, Debt, Hybrid, MF, AIF, AUC for every sector.
    Must be called AFTER tool_parse_tables.

    Returns:
        dates          : dates processed
        sector_counts  : dict mapping date_str → number of sectors
        grand_totals   : dict mapping date_str → {F1_Total, F2_Total, Month_Total, ...}
        extract_errors : list of any errors
    """
    global _state
    result = extract_data(_state)
    _state.update(result)

    sector_data   = result.get("sector_data", {})
    sector_totals = result.get("sector_totals", {})
    return {
        "dates":          list(sector_data.keys()),
        "sector_counts":  {ds: len(recs) for ds, recs in sector_data.items()},
        "grand_totals":   sector_totals,
        "extract_errors": result.get("extract_errors", []),
        "status":         "ok" if sector_data else "failed",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 5 — generate_insights                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_generate_insights() -> dict:
    """
    Generate sector-level FPI insights:
    - Buy / Sell signals per sector
    - Momentum (accelerating vs decelerating)
    - Asset dominance (Equity-led vs Debt-led)
    - Change vs previous report
    - Top movers
    Must be called AFTER tool_extract_data.

    Returns:
        summary         : overall market summary (signal, totals, counts)
        buying_sectors  : list of sectors with net positive FPI investment
        selling_sectors : list of sectors with net negative FPI investment
        top_movers      : top 5 sectors by change vs previous report
        total_insights  : total number of sectors analysed
    """
    global _state
    result = generate_insights(_state)
    _state.update(result)

    summary  = result.get("summary", {})
    buying   = result.get("buying_sectors", [])
    selling  = result.get("selling_sectors", [])
    movers   = result.get("top_movers", [])

    return {
        "summary": summary,
        "buying_sectors": [
            {"sector": r["sector"],
             "month_net_inr": r["month_net_inr"],
             "signal": r["signal_month"],
             "momentum": r["momentum"]}
            for r in buying
        ],
        "selling_sectors": [
            {"sector": r["sector"],
             "month_net_inr": r["month_net_inr"],
             "signal": r["signal_month"],
             "momentum": r["momentum"]}
            for r in selling
        ],
        "top_movers": [
            {"sector": r["sector"],
             "change_vs_prev": r["change_vs_prev"],
             "signal": r["signal_month"]}
            for r in movers
        ],
        "total_insights": len(result.get("insights", [])),
        "status": "ok" if result.get("insights") else "failed",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 6 — save_reports                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
@tool
def tool_save_reports(output_dir: Optional[str] = "fpi_data") -> dict:
    """
    Save all FPI data to disk:
    - Colour-coded Excel with 6 sheets (Insights, Buying, Selling, Movers, Summary, Raw)
    - Individual CSVs per date + insights/buying/selling CSVs

    Args:
        output_dir: Folder to save files into. Defaults to 'fpi_data'.

    Returns:
        saved_files : list of absolute file paths written
        excel_path  : path to the main Excel report
        save_errors : list of any errors
    """
    global _state
    _state["output_dir"] = output_dir or "fpi_data"
    result = save_reports(_state)
    _state.update(result)

    return {
        "saved_files": result.get("saved_files", []),
        "excel_path":  result.get("excel_path", ""),
        "save_errors": result.get("save_errors", []),
        "file_count":  len(result.get("saved_files", [])),
        "status":      "ok" if result.get("saved_files") else "failed",
    }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  TOOL 7 — run full pipeline in one shot                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
# @tool
def tool_run_full_pipeline(
    today_str:  Optional[str] = None,
    output_dir: Optional[str] = "fpi_data",
) -> dict:
    """
    Run the COMPLETE FPI data pipeline in one call:
    detect dates → fetch HTML → parse tables → extract data
    → generate insights → save reports

    Args:
        today_str  : Date in YYYY-MM-DD format to search from (default: today).
        output_dir : Folder to save output files (default: 'fpi_data').

    Returns:
        summary         : overall FPI market summary
        buying_sectors  : sectors with net FPI buying
        selling_sectors : sectors with net FPI selling
        top_movers      : biggest changes vs previous report
        saved_files     : all files written to disk
        excel_path      : path to colour-coded Excel report
    """
    global _state
    _state = {}   # reset for fresh run

    today = date.fromisoformat(today_str) if today_str else date.today()
    final = run(today=today, output_dir=output_dir or "fpi_data")
    _state.update(final)

    summary  = final.get("summary", {})
    buying   = final.get("buying_sectors", [])
    selling  = final.get("selling_sectors", [])
    movers   = final.get("top_movers", [])

    return {
        "summary": summary,
        "buying_sectors": [
            {"sector": r["sector"],
             "month_net_inr": r["month_net_inr"],
             "signal": r["signal_month"],
             "momentum": r["momentum"]}
            for r in buying
        ],
        "selling_sectors": [
            {"sector": r["sector"],
             "month_net_inr": r["month_net_inr"],
             "signal": r["signal_month"],
             "momentum": r["momentum"]}
            for r in selling
        ],
        "top_movers": [
            {"sector": r["sector"],
             "change_vs_prev": r["change_vs_prev"],
             "signal": r["signal_month"]}
            for r in movers
        ],
        "report_dates": [str(d) for d in final.get("report_dates", [])],
        "saved_files":  final.get("saved_files", []),
        "excel_path":   final.get("excel_path", ""),
        "status":       "ok" if summary else "failed",
    }


# ── export list ───────────────────────────────────────────────────────────────
ALL_FPI_TOOLS = [
    tool_detect_dates,
    tool_fetch_reports,
    tool_parse_tables,
    tool_extract_data,
    tool_generate_insights,
    tool_save_reports,
    tool_run_full_pipeline,
]


# # ── quick test (no agent needed) ──────────────────────────────────────────────
# if __name__ == "__main__":
#     # Option A: one-shot tool
#     result = tool_run_full_pipeline.invoke({})
#     print("\nSummary:", result["summary"])
#     print("Buying :", [s["sector"] for s in result["buying_sectors"]])
#     print("Selling:", [s["sector"] for s in result["selling_sectors"]])

    # Option B: step-by-step tools (same as calling nodes manually)
    # tool_detect_dates.invoke({})
    # tool_fetch_reports.invoke({})
    # tool_parse_tables.invoke({})
    # tool_extract_data.invoke({})
    # tool_generate_insights.invoke({})
    # tool_save_reports.invoke({"output_dir": "fpi_data"})
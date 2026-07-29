#!/usr/bin/env python3
"""Deterministic calculator for quantitative value screens.

Computes per-criterion results for four published, mechanical screens:

  - graham_defensive : Benjamin Graham's Defensive Investor criteria (7 tests)
  - ncav             : Graham's Net Current Asset Value ("net-net") test
  - fscore           : Piotroski F-Score (9 binary tests, summed 0-9)
  - magic_formula    : Greenblatt Magic Formula (rank a peer set on
                       earnings yield + return on capital)

The script performs arithmetic only. It does not source data, judge
data quality, or interpret results. Any criterion whose required inputs
are missing is reported as "insufficient_data" rather than guessed.

Usage:
    python screen_calculator.py input.json
    python screen_calculator.py input.json --pretty

Input schema: see references/*.md in this skill for the field list each
screen requires. Top-level structure:

{
  "screens": ["graham_defensive", "ncav", "fscore"],
  "company": { ... single-company fields ... },
  "universe": [ { ... }, ... ]        # required only for magic_formula
  "options": {
    "size_threshold": 800000000,      # graham_defensive criterion 1
    "dividend_years_required": 10     # graham_defensive criterion 5
  }
}

All monetary values must be in the same currency and unit (e.g. all in
USD, all absolute — not "millions" for one field and absolute for
another). Histories are ordered OLDEST FIRST.

Output: JSON to stdout with per-criterion detail and a summary per
screen. Exit code 0 on success, 1 on malformed input.
"""

import argparse
import json
import sys

MISSING = "insufficient_data"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _get(d, key):
    """Return d[key] if present and not None, else None."""
    v = d.get(key)
    return v if v is not None else None


def _num(d, key):
    """Return d[key] as float if present and numeric, else None."""
    v = d.get(key)
    if isinstance(v, bool) or v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _criterion(name, passed, value=None, threshold=None, note=None):
    """Build a criterion result dict. passed may be True/False/MISSING."""
    result = {
        "criterion": name,
        "result": "pass" if passed is True else ("fail" if passed is False else MISSING),
    }
    if value is not None:
        result["value"] = value
    if threshold is not None:
        result["threshold"] = threshold
    if note:
        result["note"] = note
    return result


def _round(x, places=4):
    return None if x is None else round(x, places)


# ---------------------------------------------------------------------------
# Graham Defensive Investor (7 criteria)
# ---------------------------------------------------------------------------

def graham_defensive(company, options):
    criteria = []
    size_threshold = float(options.get("size_threshold", 800_000_000))
    div_years = int(options.get("dividend_years_required", 10))
    sector = (_get(company, "sector_type") or "industrial").lower()

    # 1. Adequate size
    revenue = _num(company, "revenue")
    if revenue is None:
        criteria.append(_criterion("adequate_size", MISSING,
                                   note="'revenue' not provided"))
    else:
        criteria.append(_criterion(
            "adequate_size", revenue >= size_threshold,
            value=revenue, threshold=f">= {size_threshold:,.0f}",
            note="Threshold is Graham's $100M (1970) inflation-adjusted; "
                 "configurable via options.size_threshold"))

    # 2. Current ratio >= 2.0
    ca = _num(company, "current_assets")
    cl = _num(company, "current_liabilities")
    if ca is None or cl is None or cl == 0:
        criteria.append(_criterion("current_ratio", MISSING,
                                   note="'current_assets'/'current_liabilities' "
                                        "missing or current_liabilities is 0"))
    elif sector in ("utility", "financial"):
        criteria.append(_criterion(
            "current_ratio", MISSING, value=_round(ca / cl, 2),
            note=f"Graham's current-ratio test is not applied to {sector} "
                 "companies; use the sector-specific balance-sheet test in "
                 "references/graham-defensive.md"))
    else:
        cr = ca / cl
        criteria.append(_criterion("current_ratio", cr >= 2.0,
                                   value=_round(cr, 2), threshold=">= 2.0"))

    # 3. Long-term debt <= net current assets (working capital)
    ltd = _num(company, "long_term_debt")
    if ltd is None or ca is None or cl is None:
        criteria.append(_criterion("debt_vs_working_capital", MISSING,
                                   note="'long_term_debt', 'current_assets' or "
                                        "'current_liabilities' not provided"))
    elif sector in ("utility", "financial"):
        criteria.append(_criterion(
            "debt_vs_working_capital", MISSING,
            note=f"Not applied to {sector} companies; Graham used an "
                 "equity-to-debt test for utilities instead"))
    else:
        nca = ca - cl
        criteria.append(_criterion(
            "debt_vs_working_capital", ltd <= nca,
            value={"long_term_debt": ltd, "net_current_assets": nca},
            threshold="long_term_debt <= net_current_assets"))

    # 4. Positive EPS every year for 10 years
    eps = _get(company, "eps_history")
    if not isinstance(eps, list) or len(eps) < 10:
        criteria.append(_criterion(
            "earnings_stability", MISSING,
            note="'eps_history' must contain at least 10 annual values, "
                 "oldest first"))
        eps10 = None
    else:
        eps10 = [float(x) for x in eps[-10:]]
        criteria.append(_criterion(
            "earnings_stability", all(x > 0 for x in eps10),
            value={"years": 10, "negative_years": sum(1 for x in eps10 if x <= 0)},
            threshold="EPS > 0 in each of the last 10 years"))

    # 5. Uninterrupted dividends
    divs = _get(company, "dividend_history")
    if not isinstance(divs, list) or len(divs) < div_years:
        criteria.append(_criterion(
            "dividend_record", MISSING,
            note=f"'dividend_history' must contain at least {div_years} annual "
                 "per-share amounts (or booleans), oldest first"))
    else:
        recent = divs[-div_years:]
        paid_all = all(
            (bool(x) if isinstance(x, bool) else float(x) > 0) for x in recent)
        criteria.append(_criterion(
            "dividend_record", paid_all,
            value={"years_checked": div_years},
            threshold=f"dividend paid in each of the last {div_years} years",
            note="Graham's original test used 20 years; 10 is the common "
                 "modern relaxation (configurable via "
                 "options.dividend_years_required)"))

    # 6. EPS growth >= 33% over the decade (3-yr average endpoints)
    if eps10 is None:
        criteria.append(_criterion("earnings_growth", MISSING,
                                   note="requires the same 10-year 'eps_history'"))
    else:
        start_avg = sum(eps10[0:3]) / 3.0
        end_avg = sum(eps10[7:10]) / 3.0
        if start_avg <= 0:
            criteria.append(_criterion(
                "earnings_growth", False,
                value={"start_3yr_avg_eps": _round(start_avg),
                       "end_3yr_avg_eps": _round(end_avg)},
                threshold="end/start >= 1.33",
                note="Starting 3-year average EPS is not positive; growth "
                     "ratio undefined, treated as fail"))
        else:
            growth = end_avg / start_avg
            criteria.append(_criterion(
                "earnings_growth", growth >= 1.33,
                value={"start_3yr_avg_eps": _round(start_avg),
                       "end_3yr_avg_eps": _round(end_avg),
                       "growth_ratio": _round(growth, 3)},
                threshold=">= 1.33 (i.e. >= 33% growth)"))

    # 7. Moderate valuation: P/E <= 15 on 3-yr avg EPS AND P/E * P/B <= 22.5
    price = _num(company, "price")
    bvps = _num(company, "book_value_per_share")
    if bvps is None:
        equity = _num(company, "total_equity")
        shares = _num(company, "shares_outstanding")
        if equity is not None and shares:
            bvps = equity / shares
    if price is None or eps10 is None or bvps is None or bvps <= 0:
        criteria.append(_criterion(
            "moderate_valuation", MISSING,
            note="requires 'price', 10-year 'eps_history', and "
                 "'book_value_per_share' (or 'total_equity' + "
                 "'shares_outstanding'); book value must be positive"))
    else:
        avg_eps_3 = sum(eps10[-3:]) / 3.0
        if avg_eps_3 <= 0:
            criteria.append(_criterion(
                "moderate_valuation", False,
                value={"avg_eps_3yr": _round(avg_eps_3)},
                note="3-year average EPS not positive; P/E undefined, "
                     "treated as fail"))
        else:
            pe = price / avg_eps_3
            pb = price / bvps
            product = pe * pb
            passed = pe <= 15.0 and product <= 22.5
            criteria.append(_criterion(
                "moderate_valuation", passed,
                value={"pe_on_3yr_avg_eps": _round(pe, 2),
                       "pb": _round(pb, 2),
                       "pe_times_pb": _round(product, 2)},
                threshold="P/E <= 15 AND P/E x P/B <= 22.5"))

    passed_n = sum(1 for c in criteria if c["result"] == "pass")
    failed_n = sum(1 for c in criteria if c["result"] == "fail")
    missing_n = sum(1 for c in criteria if c["result"] == MISSING)
    return {
        "screen": "graham_defensive",
        "criteria": criteria,
        "summary": {
            "passed": passed_n, "failed": failed_n,
            "insufficient_data": missing_n, "total": len(criteria),
            "verdict": ("pass" if passed_n == len(criteria)
                        else ("fail" if failed_n > 0 else "incomplete")),
        },
    }


# ---------------------------------------------------------------------------
# Graham NCAV / net-net
# ---------------------------------------------------------------------------

def ncav(company, options):
    criteria = []
    ca = _num(company, "current_assets")
    tl = _num(company, "total_liabilities")
    pref = _num(company, "preferred_stock") or 0.0
    shares = _num(company, "shares_outstanding")
    price = _num(company, "price")

    ncav_ps = None
    if ca is None or tl is None or not shares:
        criteria.append(_criterion(
            "ncav_discount", MISSING,
            note="requires 'current_assets', 'total_liabilities', "
                 "'shares_outstanding' (and optional 'preferred_stock')"))
    elif price is None:
        criteria.append(_criterion("ncav_discount", MISSING,
                                   note="'price' not provided"))
    else:
        ncav_total = ca - tl - pref
        ncav_ps = ncav_total / shares
        if ncav_ps <= 0:
            criteria.append(_criterion(
                "ncav_discount", False,
                value={"ncav_per_share": _round(ncav_ps, 2), "price": price},
                threshold="price <= 0.67 x NCAV per share",
                note="NCAV is not positive; company cannot qualify as a "
                     "net-net"))
        else:
            limit = ncav_ps * 2.0 / 3.0
            criteria.append(_criterion(
                "ncav_discount", price <= limit,
                value={"ncav_per_share": _round(ncav_ps, 2),
                       "two_thirds_ncav": _round(limit, 2),
                       "price": price,
                       "price_to_ncav": _round(price / ncav_ps, 3)},
                threshold="price <= 0.67 x NCAV per share"))

    # Cash-burn flag (advisory, not part of the pass/fail verdict)
    cfo_hist = _get(company, "cfo_history")
    if isinstance(cfo_hist, list) and len(cfo_hist) >= 2:
        recent = [float(x) for x in cfo_hist[-3:]]
        burning = all(x < 0 for x in recent)
        criteria.append(_criterion(
            "cash_burn_flag", (not burning),
            value={"recent_cfo": recent},
            threshold="operating cash flow not negative in every recent year",
            note="Advisory only: a net-net that burns cash every year is "
                 "consuming the asset value the screen is based on"))
    else:
        criteria.append(_criterion(
            "cash_burn_flag", MISSING,
            note="Advisory check skipped: provide 'cfo_history' (>= 2 annual "
                 "values, oldest first) to enable it"))

    main = criteria[0]["result"]
    return {
        "screen": "ncav",
        "criteria": criteria,
        "summary": {
            "verdict": ("pass" if main == "pass"
                        else ("fail" if main == "fail" else "incomplete")),
            "note": "Verdict is determined by ncav_discount alone; "
                    "cash_burn_flag is advisory",
        },
    }


# ---------------------------------------------------------------------------
# Piotroski F-Score
# ---------------------------------------------------------------------------

def fscore(company, options):
    """Expects company["years"]: list of >= 3 annual dicts, OLDEST FIRST.

    Each year dict may contain: net_income, cfo, total_assets,
    long_term_debt, current_assets, current_liabilities, gross_profit,
    revenue, shares_outstanding.

    Three years are needed because Piotroski's ROA and asset-turnover
    definitions use beginning-of-year total assets, so year t and t-1
    ratios require assets at t-1 and t-2.
    """
    years = _get(company, "years")
    if not isinstance(years, list) or len(years) < 3:
        return {
            "screen": "fscore",
            "criteria": [],
            "summary": {"verdict": MISSING,
                        "note": "'years' must contain at least 3 annual "
                                "dicts, oldest first (t-2, t-1, t)"},
        }

    t2, t1, t = years[-3], years[-2], years[-1]
    criteria = []

    def need(*vals):
        return any(v is None for v in vals)

    ni_t, ni_t1 = _num(t, "net_income"), _num(t1, "net_income")
    at_t, at_t1, at_t2 = (_num(t, "total_assets"), _num(t1, "total_assets"),
                          _num(t2, "total_assets"))
    cfo_t = _num(t, "cfo")

    # --- Profitability ---
    # 1. ROA > 0  (ROA_t = NI_t / Assets_{t-1})
    if need(ni_t, at_t1) or at_t1 == 0:
        criteria.append(_criterion("roa_positive", MISSING,
                                   note="needs net_income(t), total_assets(t-1)"))
        roa_t = None
    else:
        roa_t = ni_t / at_t1
        criteria.append(_criterion("roa_positive", roa_t > 0,
                                   value=_round(roa_t), threshold="> 0"))

    # 2. CFO > 0
    if cfo_t is None:
        criteria.append(_criterion("cfo_positive", MISSING,
                                   note="needs cfo(t)"))
    else:
        criteria.append(_criterion("cfo_positive", cfo_t > 0,
                                   value=cfo_t, threshold="> 0"))

    # 3. Delta ROA > 0
    if roa_t is None or need(ni_t1, at_t2) or at_t2 == 0:
        criteria.append(_criterion("roa_improving", MISSING,
                                   note="needs net_income(t-1), total_assets(t-2)"))
    else:
        roa_t1 = ni_t1 / at_t2
        criteria.append(_criterion(
            "roa_improving", roa_t > roa_t1,
            value={"roa_t": _round(roa_t), "roa_t1": _round(roa_t1)},
            threshold="roa_t > roa_t-1"))

    # 4. Accruals: CFO > net income
    if need(cfo_t, ni_t):
        criteria.append(_criterion("accrual_quality", MISSING,
                                   note="needs cfo(t), net_income(t)"))
    else:
        criteria.append(_criterion(
            "accrual_quality", cfo_t > ni_t,
            value={"cfo": cfo_t, "net_income": ni_t},
            threshold="cfo > net_income"))

    # --- Leverage / liquidity / dilution ---
    # 5. Leverage decreasing (LTD / avg assets)
    ltd_t, ltd_t1 = _num(t, "long_term_debt"), _num(t1, "long_term_debt")
    if need(ltd_t, ltd_t1, at_t, at_t1, at_t2):
        criteria.append(_criterion(
            "leverage_decreasing", MISSING,
            note="needs long_term_debt(t, t-1) and total_assets(t, t-1, t-2)"))
    else:
        avg_t = (at_t + at_t1) / 2.0
        avg_t1 = (at_t1 + at_t2) / 2.0
        if avg_t == 0 or avg_t1 == 0:
            criteria.append(_criterion("leverage_decreasing", MISSING,
                                       note="average assets is zero"))
        else:
            lev_t, lev_t1 = ltd_t / avg_t, ltd_t1 / avg_t1
            criteria.append(_criterion(
                "leverage_decreasing", lev_t <= lev_t1,
                value={"leverage_t": _round(lev_t), "leverage_t1": _round(lev_t1)},
                threshold="leverage_t <= leverage_t-1"))

    # 6. Current ratio improving
    ca_t, cl_t = _num(t, "current_assets"), _num(t, "current_liabilities")
    ca_t1, cl_t1 = _num(t1, "current_assets"), _num(t1, "current_liabilities")
    if need(ca_t, cl_t, ca_t1, cl_t1) or cl_t == 0 or cl_t1 == 0:
        criteria.append(_criterion(
            "liquidity_improving", MISSING,
            note="needs current_assets and current_liabilities for t and t-1"))
    else:
        cr_t, cr_t1 = ca_t / cl_t, ca_t1 / cl_t1
        criteria.append(_criterion(
            "liquidity_improving", cr_t > cr_t1,
            value={"current_ratio_t": _round(cr_t, 2),
                   "current_ratio_t1": _round(cr_t1, 2)},
            threshold="current_ratio_t > current_ratio_t-1"))

    # 7. No new shares issued
    sh_t, sh_t1 = _num(t, "shares_outstanding"), _num(t1, "shares_outstanding")
    if need(sh_t, sh_t1):
        criteria.append(_criterion("no_dilution", MISSING,
                                   note="needs shares_outstanding(t, t-1)"))
    else:
        criteria.append(_criterion(
            "no_dilution", sh_t <= sh_t1,
            value={"shares_t": sh_t, "shares_t1": sh_t1},
            threshold="shares_t <= shares_t-1"))

    # --- Operating efficiency ---
    # 8. Gross margin improving
    def gross_margin(y):
        gp, rev = _num(y, "gross_profit"), _num(y, "revenue")
        if gp is None or rev is None or rev == 0:
            return None
        return gp / rev

    gm_t, gm_t1 = gross_margin(t), gross_margin(t1)
    if gm_t is None or gm_t1 is None:
        criteria.append(_criterion(
            "gross_margin_improving", MISSING,
            note="needs gross_profit and revenue for t and t-1"))
    else:
        criteria.append(_criterion(
            "gross_margin_improving", gm_t > gm_t1,
            value={"gross_margin_t": _round(gm_t), "gross_margin_t1": _round(gm_t1)},
            threshold="gm_t > gm_t-1"))

    # 9. Asset turnover improving (Revenue_t / Assets_{t-1})
    rev_t, rev_t1 = _num(t, "revenue"), _num(t1, "revenue")
    if need(rev_t, rev_t1, at_t1, at_t2) or at_t1 == 0 or at_t2 == 0:
        criteria.append(_criterion(
            "asset_turnover_improving", MISSING,
            note="needs revenue(t, t-1), total_assets(t-1, t-2)"))
    else:
        to_t, to_t1 = rev_t / at_t1, rev_t1 / at_t2
        criteria.append(_criterion(
            "asset_turnover_improving", to_t > to_t1,
            value={"turnover_t": _round(to_t), "turnover_t1": _round(to_t1)},
            threshold="turnover_t > turnover_t-1"))

    score = sum(1 for c in criteria if c["result"] == "pass")
    missing_n = sum(1 for c in criteria if c["result"] == MISSING)
    band = ("strong (>=8)" if score >= 8
            else ("weak (<=2)" if score <= 2 and missing_n == 0 else "middle"))
    return {
        "screen": "fscore",
        "criteria": criteria,
        "summary": {
            "score": score,
            "max_score": 9,
            "insufficient_data": missing_n,
            "band": band if missing_n == 0 else f"{band} — incomplete: "
                    f"{missing_n} of 9 tests lack data; true score is between "
                    f"{score} and {score + missing_n}",
        },
    }


# ---------------------------------------------------------------------------
# Greenblatt Magic Formula (peer-set ranking)
# ---------------------------------------------------------------------------

def magic_formula(universe, options):
    if not isinstance(universe, list) or len(universe) < 2:
        return {
            "screen": "magic_formula",
            "companies": [],
            "summary": {"verdict": MISSING,
                        "note": "'universe' must contain at least 2 companies; "
                                "the Magic Formula is a relative ranking and "
                                "is meaningless for a single ticker"},
        }

    rows = []
    for c in universe:
        ticker = _get(c, "ticker") or "?"
        ebit = _num(c, "ebit")
        mcap = _num(c, "market_cap")
        if mcap is None:
            price, shares = _num(c, "price"), _num(c, "shares_outstanding")
            if price is not None and shares is not None:
                mcap = price * shares
        debt = _num(c, "total_debt")
        cash = _num(c, "cash")
        nfa = _num(c, "net_fixed_assets")
        nwc = _num(c, "net_working_capital")
        if nwc is None:
            ca, cl = _num(c, "current_assets"), _num(c, "current_liabilities")
            if ca is not None and cl is not None:
                nwc = ca - cl

        row = {"ticker": ticker}
        problems = []

        # Earnings yield = EBIT / EV
        if None in (ebit, mcap, debt, cash):
            problems.append("earnings_yield needs ebit, market_cap (or "
                            "price+shares_outstanding), total_debt, cash")
            row["earnings_yield"] = None
        else:
            ev = mcap + debt - cash
            if ev <= 0:
                problems.append("enterprise value <= 0; earnings yield "
                                "undefined")
                row["earnings_yield"] = None
                row["enterprise_value"] = _round(ev, 0)
            else:
                row["enterprise_value"] = _round(ev, 0)
                row["earnings_yield"] = _round(ebit / ev)

        # Return on capital = EBIT / (max(NWC, 0) + NFA)
        if None in (ebit, nwc, nfa):
            problems.append("return_on_capital needs ebit, net_working_capital "
                            "(or current_assets+current_liabilities), "
                            "net_fixed_assets")
            row["return_on_capital"] = None
        else:
            capital = max(nwc, 0.0) + nfa
            if capital <= 0:
                problems.append("tangible capital <= 0; return on capital "
                                "undefined")
                row["return_on_capital"] = None
            else:
                row["return_on_capital"] = _round(ebit / capital)
                row["tangible_capital"] = _round(capital, 0)

        if problems:
            row["insufficient_data"] = problems
        rows.append(row)

    rankable = [r for r in rows
                if r.get("earnings_yield") is not None
                and r.get("return_on_capital") is not None]
    excluded = [r["ticker"] for r in rows if r not in rankable]

    # Rank descending on each metric (1 = best), sum ranks
    by_ey = sorted(rankable, key=lambda r: r["earnings_yield"], reverse=True)
    by_roc = sorted(rankable, key=lambda r: r["return_on_capital"], reverse=True)
    for i, r in enumerate(by_ey):
        r["ey_rank"] = i + 1
    for i, r in enumerate(by_roc):
        r["roc_rank"] = i + 1
    for r in rankable:
        r["combined_rank_score"] = r["ey_rank"] + r["roc_rank"]

    # Ties on combined score break deterministically toward the cheaper
    # name (higher earnings yield), then alphabetically by ticker.
    ranked = sorted(rankable,
                    key=lambda r: (r["combined_rank_score"],
                                   -r["earnings_yield"], r["ticker"]))
    for i, r in enumerate(ranked):
        r["final_rank"] = i + 1

    return {
        "screen": "magic_formula",
        "companies": rows,
        "summary": {
            "ranked": [r["ticker"] for r in ranked],
            "excluded_for_missing_data": excluded,
            "note": "Lower combined_rank_score is better. Ranking is only "
                    "meaningful relative to this specific universe.",
        },
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

SCREENS = {
    "graham_defensive": graham_defensive,
    "ncav": ncav,
    "fscore": fscore,
}


def main():
    parser = argparse.ArgumentParser(
        description="Compute quantitative value screens from structured "
                    "financial data")
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument("--pretty", action="store_true",
                        help="Indent the JSON output")
    args = parser.parse_args()

    try:
        with open(args.input) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Could not read input: {e}"}))
        sys.exit(1)

    requested = data.get("screens")
    if not isinstance(requested, list) or not requested:
        print(json.dumps({"error": "'screens' must be a non-empty list drawn "
                                   "from: graham_defensive, ncav, fscore, "
                                   "magic_formula"}))
        sys.exit(1)

    options = data.get("options", {})
    company = data.get("company", {})
    universe = data.get("universe")
    results = []

    for name in requested:
        if name == "magic_formula":
            results.append(magic_formula(universe, options))
        elif name in SCREENS:
            if not company:
                results.append({"screen": name,
                                "summary": {"verdict": MISSING,
                                            "note": "'company' object missing"}})
            else:
                results.append(SCREENS[name](company, options))
        else:
            results.append({"screen": name,
                            "summary": {"verdict": "error",
                                        "note": f"Unknown screen '{name}'"}})

    out = {"results": results}
    print(json.dumps(out, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
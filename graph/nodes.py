from tools.nse_tools import (
    get_stock_info,
    get_nifty_data,
    get_stock_news,
    get_technical_analysis,
    get_fii_dii_data,
    get_relative_strength,

)
from tools import fpi
from graph.llm import get_llm
from langchain_core.messages import HumanMessage , SystemMessage

from graph.workflow import StockAnalysisState

import json


def fundamental_node(state: StockAnalysisState) -> dict:
    try:
        # -------------------------
        # 1. Call tool
        # -------------------------
        result = get_stock_info.invoke({"symbol": state["symbol"]})

        # -------------------------
        # 2. LLM Analysis + Score
        # -------------------------
        llm = get_llm()

        prompt = f"""
            You are a senior equity research analyst.

            Analyze the following fundamental data and:

            1. Give a score (0–100)
            - 100 = very strong fundamentals
            - 50 = average
            - 0 = very weak

            2. Provide structured analysis

            IMPORTANT:
            - Return ONLY valid JSON
            - No extra text

            Format:
            {{
            "score": <number>,
            "profitability": "Strong / Moderate / Weak",
            "growth": "High / Moderate / Low",
            "valuation": "Undervalued / Fair / Overvalued",
            "risk": "Low / Medium / High",
            "summary": "2-3 line explanation"
            }}

            Data:
            {result}
            """

        response = llm.invoke([HumanMessage(content=prompt)])

        # -------------------------
        # 3. Parse response safely
        # -------------------------
        try:
            parsed = json.loads(response.content)
            score = int(parsed.get("score", 50))
            analysis = parsed

            print('fundamental score',score)
            print('fundamental analysis',analysis)
        except Exception:
            score = 50
            analysis = {
                "score": 50,
                "profitability": "Unknown",
                "growth": "Unknown",
                "valuation": "Unknown",
                "risk": "Unknown",
                "summary": response.content
            }

        # -------------------------
        # 4. Return final output
        # -------------------------
        return {
            "fundamental_data": result,
            "fundamental_score": score,
            "fundamental_analysis": analysis
        }

    except Exception as e:
        return {
            "fundamental_data": f"Error: {str(e)}",
            "fundamental_score": 50,
            "fundamental_analysis": {
                "score": 50,
                "summary": "Fundamental analysis failed"
            }
        }


def technical_node(state: StockAnalysisState) -> dict:
    try:
        result = get_technical_analysis.invoke({"symbol": state["symbol"]})

        llm = get_llm()

        prompt = f"""
        You are a professional technical analyst with 15+ years of experience.

        Analyze the following technical data and provide:

        1. A score between 0-100
        - 100 = extremely bullish
        - 50 = neutral
        - 0 = extremely bearish

        2. A structured analysis

        IMPORTANT:
        - Return output in STRICT JSON format
        - Do NOT add extra text

        Format:
        {{
            "score": <number>,
            "trend": "Bullish / Bearish / Sideways",
            "signals": [
                "signal 1",
                "signal 2"
            ],
            "summary": "2-3 line professional explanation"
        }}

        Technical Data:
        {result}
        """

        response = llm.invoke([HumanMessage(content=prompt)])

        # -------------------------
        # Safe Parsing
        # -------------------------
        import json

        try:
            parsed = json.loads(response.content)
            score = int(parsed.get("score", 50))
            analysis = parsed
            print('technical score',score)
            print('technical analysis',analysis)


        except Exception:
            # fallback if LLM breaks format
            score = 50
            analysis = {
                "score": 50,
                "trend": "Unknown",
                "signals": [],
                "summary": response.content
            }



        return {
            "technical_data": result,
            "technical_score": score,
            "technical_analysis": analysis
        }

    except Exception as e:
        return {
            "technical_data": f"Error: {str(e)}",
            "technical_score": 50,
            "technical_analysis": {
                "score": 50,
                "trend": "Error",
                "signals": [],
                "summary": "Technical analysis failed"
            }
        }





def news_node(state: StockAnalysisState) -> dict:
    try:
        # -------------------------
        # 1. Fetch news
        # -------------------------
        result = get_stock_news.invoke({"symbol": state["symbol"]})





        llm = get_llm()

        # -------------------------
        # 3. BETTER PROMPT
        # -------------------------
        prompt = f"""
            You are a professional financial news sentiment analyst.

            Analyze the structured news data below.

            IMPORTANT THINKING STEPS:
            - Focus on earnings, results, deals, regulations
            - Ignore generic market noise
            - Give higher weight to repeated themes

            TASK:
            1. Determine overall sentiment
            2. Score (0–100)
            3. Extract key signals

            STRICT OUTPUT: JSON ONLY

            Format:
            {{
                "score": <number>,
                "sentiment": "Bullish / Neutral / Bearish",
                "key_points": [
                    "concise insight 1",
                    "concise insight 2"
                ],
                "summary": "2-3 line professional explanation",
                "confidence": "High / Medium / Low"
            }}

            Structured News:
            {result}
            """

        response = llm.invoke([HumanMessage(content=prompt)])
        # print(response)

        # -------------------------
        # 4. Safe parsing
        # -------------------------

        content = response.content.strip()
        try:
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(content)

            score = int(parsed.get("score", 50))
            analysis = parsed

            print("news score", score)
            print("news analysis", analysis)

        except Exception:
            score = 50
            analysis = {
                "score": 50,
                "sentiment": "Neutral",
                "key_points": [],
                "summary": response.content,
                "confidence": "Low"
            }

        # -------------------------
        # 5. Return
        # -------------------------
        return {
            "news_data": result,
            "news_score": score,
            "news_analysis": analysis
        }

    except Exception as e:
        return {
            "news_data": f"Error: {str(e)}",
            "news_score": 50,
            "news_analysis": {
                "score": 50,
                "sentiment": "Error",
                "key_points": [],
                "summary": "News analysis failed",
                "confidence": "Low"
            }
        }
"""
FPI / FII-DII Node
==================
Combines TWO data sources:
  1. get_fii_dii_data()        — daily NSE FII/DII net buy/sell (today's trading)
  2. fpi.tool_run_full_pipeline — fortnightly NSDL sector-wise FPI flow
"""

# from your_llm import get_llm



# ── the node ──────────────────────────────────────────────────────────────────
def fii_dii_node(state: StockAnalysisState) -> dict:
    try:
        symbol = state.get("symbol", "the stock")

        # ─────────────────────────────────────────────────
        # 1. Daily FII/DII  (today's trading session)
        # ─────────────────────────────────────────────────
        daily = get_fii_dii_data.invoke({})
        print(f"  [fpi_node] daily → {daily.get('market_signal')}  "
              f"FII ₹{daily.get('fii',{}).get('net_cr',0):,.0f}  "
              f"DII ₹{daily.get('dii',{}).get('net_cr',0):,.0f}")

        # ─────────────────────────────────────────────────
        # 2. Fortnightly FPI sector data  (NSDL)
        # ─────────────────────────────────────────────────
        fii_sector      = fpi.tool_run_full_pipeline()
        summary         = fii_sector.get("summary", {})
        buying_sectors  = fii_sector.get("buying_sectors", [])
        selling_sectors = fii_sector.get("selling_sectors", [])
        top_movers      = fii_sector.get("top_movers", [])

        sector_context = {
            "period":           f"{summary.get('date_old','')} → {summary.get('date_new','')}",
            "overall_signal":   summary.get("overall_signal", ""),
            "total_month_inr":  summary.get("total_month_inr", 0),
            "total_equity_inr": summary.get("total_equity_inr", 0),
            "total_debt_inr":   summary.get("total_debt_inr", 0),
            "change_vs_prev":   summary.get("change_vs_prev", 0),
            "n_buying":         summary.get("n_buying", 0),
            "n_selling":        summary.get("n_selling", 0),
            "buying_sectors": [
                {"sector": s["sector"], "net_inr": s["month_net_inr"],
                 "signal": s["signal"], "momentum": s["momentum"]}
                for s in buying_sectors[:8]
            ],
            "selling_sectors": [
                {"sector": s["sector"], "net_inr": s["month_net_inr"],
                 "signal": s["signal"], "momentum": s["momentum"]}
                for s in selling_sectors[:5]
            ],
            "top_movers": [
                {"sector": m["sector"], "change_vs_prev": m["change_vs_prev"],
                 "signal": m["signal"]}
                for m in top_movers
            ],
        }

        llm = get_llm()

        # ─────────────────────────────────────────────────
        # 3. Prompt  — both sources combined
        # ─────────────────────────────────────────────────
        prompt = f"""
        You are a professional FII/DII flow analyst specializing in Indian equity markets.

        You have TWO data sources. Analyze both together:

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        SOURCE 1 — DAILY FII/DII  (today's trading)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Date           : {daily.get('date', 'N/A')}
        Market Signal  : {daily.get('market_signal', 'N/A')} — {daily.get('market_reason', '')}

        FII : {daily.get('fii', {}).get('signal', '')}
            Net  ₹{daily.get('fii', {}).get('net_cr',  0):>12,.2f} Cr
            Buy  ₹{daily.get('fii', {}).get('buy_cr',  0):>12,.2f} Cr
            Sell ₹{daily.get('fii', {}).get('sell_cr', 0):>12,.2f} Cr

        DII : {daily.get('dii', {}).get('signal', '')}
            Net  ₹{daily.get('dii', {}).get('net_cr',  0):>12,.2f} Cr
            Buy  ₹{daily.get('dii', {}).get('buy_cr',  0):>12,.2f} Cr
            Sell ₹{daily.get('dii', {}).get('sell_cr', 0):>12,.2f} Cr

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        SOURCE 2 — FORTNIGHTLY FPI SECTOR DATA  (NSDL)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        {json.dumps(sector_context, indent=2)}

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        STOCK UNDER ANALYSIS: {symbol}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        THINKING STEPS:
        - Daily FII/DII = today's institutional mood (short-term signal)
        - Fortnightly sector data = structural FPI positioning (medium-term signal)
        - Check if {symbol}'s sector appears in buying or selling list
        - FII net buyer today + sector in buying list = strong bullish confluence
        - FII net seller today + sector in buying list = short-term dip, medium-term ok
        - DII buying while FII selling = domestic support, mixed signal

        TASK:
        1. Combine both signals into one overall score (0–100)
        2. Identify whether daily and fortnightly signals are aligned or divergent
        3. Assess specific impact on {symbol} based on its sector

        STRICT OUTPUT: JSON ONLY

        {{
            "score": <0-100>,
            "sentiment": "Bullish / Neutral / Bearish",
            "fii_daily_signal":  "Net Buyer / Net Seller",
            "dii_daily_signal":  "Net Buyer / Net Seller",
            "fpi_sector_signal": "Buying / Selling / Mixed",
            "confluence": "Aligned / Divergent",
            "key_points": [
                "daily FII/DII insight",
                "fortnightly sector trend insight",
                "confluence or divergence insight"
            ],
            "sector_impact": {{
                "sector_name":    "<{symbol}'s sector>",
                "sector_signal":  "Buying / Selling / Neutral",
                "sector_net_inr": <number>,
                "implication":    "1-line implication for {symbol}"
            }},
            "summary": "2-3 line professional explanation combining both data sources",
            "confidence": "High / Medium / Low"
        }}
        """

        response = llm.invoke([HumanMessage(content=prompt)])

        # ─────────────────────────────────────────────────
        # 4. Safe parsing  (same pattern as news_node)
        # ─────────────────────────────────────────────────
        content = response.content.strip()
        try:
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            parsed   = json.loads(content)
            score    = int(parsed.get("score", 50))
            analysis = parsed

            # print("fpi score   :", score)
            # print("fpi analysis:", analysis)

        except Exception:
            score = 50
            analysis = {
                "score":             50,
                "sentiment":         "Neutral",
                "fii_daily_signal":  daily.get("fii", {}).get("signal", "Unknown"),
                "dii_daily_signal":  daily.get("dii", {}).get("signal", "Unknown"),
                "fpi_sector_signal": summary.get("overall_signal", "Unknown"),
                "confluence":        "Unknown",
                "key_points":        [],
                "sector_impact":     {},
                "summary":           response.content,
                "confidence":        "Low",
            }

        # ─────────────────────────────────────────────────
        # 5. Return — all data available for downstream nodes
        # ─────────────────────────────────────────────────
        return {
            "fpi_score":    score,
            "fpi_analysis": analysis,
            "fpi_raw": {
                "daily":  daily,          # today's FII/DII numbers
                "sector": sector_context, # fortnightly sector breakdown
            },
        }

    except Exception as e:
        print(f"fpi_node error: {e}")
        return {
            "fpi_score":    50,
            "fpi_analysis": {
                "score":      50,
                "sentiment":  "Neutral",
                "key_points": [],
                "summary":    f"FPI/FII data unavailable: {e}",
                "confidence": "Low",
            },
            "fpi_raw": {},
        }

def relative_strength_node(state: StockAnalysisState) -> dict:
    try:
        # -------------------------
        # 1. Call tool
        # -------------------------
        result = get_relative_strength.invoke({"symbol": state["symbol"]})
        print(result)

        llm = get_llm()

        # -------------------------
        # 2. Prompt (VERY IMPORTANT)
        # -------------------------
        prompt = f"""
        You are a quantitative equity analyst.

        The following data represents 6-month relative performance of a stock compared against:
        - NIFTY 50 (broad market benchmark)
        - Sector index (relevant industry benchmark)
        - Market cap index (Large Cap / Mid Cap / Small Cap category)

        This comparison shows whether the stock is outperforming or underperforming each benchmark over the last 6 months.

        Interpretation Rules:
        - Outperformance vs benchmarks = bullish signal
        - Underperformance vs benchmarks = bearish signal
        - Consistent outperformance across all = very strong momentum
        - Mixed signals = neutral
        - Consistent underperformance = weak momentum

        TASK:
        1. Give a score (0–100)
        - 100 = strong outperformance across all benchmarks
        - 50 = mixed performance
        - 0 = strong underperformance

        2. Determine:
        - overall momentum strength
        - consistency of performance across benchmarks
        - leadership vs market and sector

        IMPORTANT:
        - Return ONLY raw JSON
        - Do NOT use markdown formatting

        Format:
        {{
            "score": <number>,
            "momentum": "Strong / Moderate / Weak",
            "market_view": "Outperforming / Neutral / Underperforming",
            "signals": [
                "insight 1",
                "insight 2"
            ],
            "summary": "2-3 line explanation based on 6-month performance comparison",
            "confidence": "High / Medium / Low"
        }}

        Data:
        {result}
        """

        response = llm.invoke([HumanMessage(content=prompt)])

        # -------------------------
        # 3. Safe parsing
        # -------------------------
        try:
            content = response.content.strip()

            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(content)

            score = int(parsed.get("score", 50))
            analysis = parsed

            print("relative score", score)
            print("relative analysis", analysis)

        except Exception as e:
            print("Parsing Error:", e)
            print("Raw:", response.content)

            score = 50
            analysis = {
                "score": 50,
                "momentum": "Unknown",
                "market_view": "Unknown",
                "signals": [],
                "summary": response.content,
                "confidence": "Low"
            }

        # -------------------------
        # 4. Return
        # -------------------------
        return {
            "relative_data": result,
            "relative_score": score,
            "relative_analysis": analysis
        }

    except Exception as e:
        return {
            "relative_data": f"Error: {str(e)}",
            "relative_score": 50,
            "relative_analysis": {
                "score": 50,
                "momentum": "Error",
                "market_view": "Error",
                "signals": [],
                "summary": "Relative strength analysis failed",
                "confidence": "Low"
            }
        }

def probability_node(state: StockAnalysisState) -> dict:
    try:
        # 1. Get all scores from state
        scores = {
            "Fundamental": state.get("fundamental_score", 50),
            "Technical": state.get("technical_score", 50),
            "News": state.get("news_score", 50),
            "FPI/FII": state.get("fpi_score", 50),
            "Relative Strength": state.get("relative_score", 50),



        }

        SYSTEM_MESSAGE = """
            You are an expert stock market analyst AI.

            Your task is to generate a clear, professional, and data-driven stock evaluation report.

            You will be given multiple scores (0–100) and a final weighted score with a signal.

            Interpretation rules:
            - 0–40 → Weak / Bearish
            - 40–60 → Neutral
            - 60–100 → Strong / Bullish

            Instructions:

            1. Write a structured report with:
            A. Overall Summary
            B. Score Breakdown
            C. Key Insights
            D. Risk Factors
            E. Final Recommendation

            2. Be concise, professional, and logical.
            3. Do NOT hallucinate or add external data.
            4. Base reasoning strictly on provided scores.
            5. Output should be clean and readable.

            Also return a short JSON summary at the end:
            {
            "signal": "...",
            "confidence": "...",
            "final_score": ...
            }

            """

                # 2. Weighted average — decide weights yourself
        # Should all be equal? Or fundamental more important?
        weights = {
            "Fundamental": 0.1,
            "Technical": 0.25,
            "News": 0.2,
            "FPI/FII": 0.2,
            "Relative Strength": 0.25,
        }
        final_score = sum(scores[k] * v for k, v in weights.items())


        # 3. Calculate final score
        if final_score >= 60:
            signal = "BUY"
        elif final_score <= 40:
            signal = "SELL"
        else:
            signal = "HOLD"


        confidence = abs(final_score - 50) * 2  # 0–100 scale
        confidence = round(min(confidence, 100), 2)
         # 6. Build prompt
        prompt = f"""
            Stock Analysis Data:

            Fundamental Score: {scores['Fundamental']}
            Technical Score: {scores['Technical']}
            News Sentiment Score: {scores['News']}
            FPI/FII Activity Score: {scores['FPI/FII']}
            Relative Strength Score: {scores['Relative Strength']}

            Final Weighted Score: {final_score}
            Suggested Signal: {signal}
            Confidence: {confidence}%

            Generate a detailed report.
            """


        # 5. Ask LLM to write final report using all analyses
        # 7. Call LLM
        llm = get_llm()

        response = llm.invoke([
            SystemMessage(content=SYSTEM_MESSAGE),
            HumanMessage(content=prompt)
        ])

        return {
            "final_score": final_score,
            "signal": signal,
            "confidence": confidence,
            "report": response.content
        }

    except Exception as e:
        return {
            "error": str(e)
        }

    except Exception as e:
        return {"probability_score": f"Error: {str(e)}"}
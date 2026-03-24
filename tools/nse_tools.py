import feedparser
import yfinance as yf
from langchain.tools import tool
import time
import requests
from tools import config
import yfinance as yf
import time
from dotenv import load_dotenv
import os
load_dotenv()

from urllib.parse import quote
from tavily import TavilyClient
import feedparser


## get stock price, P/E, market cap, sector and 6-month return for an NSE-listed Indian stock. Input: symbol like TCS, RELIANCE, INFY


# -------------------------------
# Helper: Safe extractor
# -------------------------------
def safe_get(df, keys):
    try:
        for key in keys:
            if key in df.index:
                return df.loc[key].iloc[0]
    except Exception:
        pass
    return None


# -------------------------------
# Updated Function
# -------------------------------
@tool
def get_stock_info(symbol: str):
    """
    Fetch stock fundamentals + 6-month return
    for NSE stocks (e.g., TCS, RELIANCE, INFY)
    """

    try:
        time.sleep(2)

        ticker_input = symbol + ".NS"
        time.sleep(2)
        ticker = yf.Ticker(ticker_input)

        # -------------------------
        # Data
        # -------------------------
        hist = ticker.history(period="6mo")
        info = ticker.info
        income = ticker.financials
        balance = ticker.balance_sheet

        # -------------------------
        # Safe extraction
        # -------------------------
        net_income = safe_get(income, ["Net Income", "NetIncome"])
        equity = safe_get(balance, ["Total Stockholder Equity", "Stockholders Equity"])
        total_assets = safe_get(balance, ["Total Assets"])
        debt = safe_get(balance, ["Total Debt", "Long Term Debt"])
        ebit = safe_get(income, ["Ebit", "EBIT"])
        interest_expense = safe_get(income, ["Interest Expense"])
        revenue = safe_get(income, ["Total Revenue"])

        # -------------------------
        # Ratios (with fallback)
        # -------------------------
        roe = (net_income / equity) if net_income and equity else info.get("returnOnEquity")
        roa = (net_income / total_assets) if net_income and total_assets else info.get("returnOnAssets")
        debt_to_equity = (debt / equity) if debt and equity else info.get("debtToEquity")

        asset_turnover = (revenue / total_assets) if revenue and total_assets else None

        interest_coverage = (
            ebit / abs(interest_expense)
            if ebit and interest_expense and interest_expense != 0
            else None
        )

        # -------------------------
        # 6-Month Return
        # -------------------------
        if not hist.empty:
            first_close = hist["Close"].iloc[0]
            last_close = hist["Close"].iloc[-1]
            return_percent = ((last_close - first_close) / first_close) * 100
        else:
            return_percent = None

        # -------------------------
        # Output Formatting
        # -------------------------
        lines = []

        lines.append(f"Ticker: {ticker_input}")
        lines.append(f"Price: ₹{info.get('currentPrice', 'N/A')}")
        lines.append(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
        lines.append(f"Forward P/E: {info.get('forwardPE', 'N/A')}")
        lines.append(f"Market Cap: ₹{info.get('marketCap', 0):,}")
        lines.append(f"Sector: {info.get('sector', 'N/A')}")

        lines.append(f"ROE: {roe}")
        lines.append(f"ROA: {roa}")
        lines.append(f"Debt to Equity: {debt_to_equity}")
        lines.append(f"Interest Coverage: {interest_coverage}")
        lines.append(f"Asset Turnover: {asset_turnover}")

        lines.append(f"Profit Margin: {info.get('profitMargins', 'N/A')}")
        lines.append(f"Operating Margin: {info.get('operatingMargins', 'N/A')}")

        lines.append(f"Revenue Growth: {info.get('revenueGrowth', 'N/A')}")
        lines.append(f"Earnings Growth: {info.get('earningsGrowth', 'N/A')}")

        if return_percent is not None:
            lines.append(f"6-Month Return: {return_percent:.2f}%")
        else:
            lines.append("6-Month Return: N/A")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

# get nifty 50 index info
@tool
def get_nifty_data():
    """

    Fetch Current Nifty 50 index level and 1-month return.
    Use this to understand broader Indian Market Direction.
    """
    try:

        index = {
        "^NSEI": "NIFTY 50",
        "^NSEBANK": "NIFTY Bank"
        }

        lines =[]
        for i in index:
            time.sleep(2)
            ticker = yf.Ticker(i)

        # Historical prices
            hist = ticker.history(period="1mo")

            first_close = float(hist["Close"].iloc[0] )  # first row
            last_close = round(float(hist["Close"].iloc[-1]), 2)
            return_percent = round(((last_close - first_close) / first_close * 100), 2)

            lines.append(f"{index[i]}: ₹{last_close} | 1M Return: {return_percent}%")
    except Exception as e:
        return f"Error fetching Nifty data: {str(e)}"
    return "\n".join(lines)

# get_nifty_data()


# You know this


# You know this pattern
@tool
def get_stock_news(symbol: str) -> str:
    """
    Hybrid News Fetcher:
    - Tavily (semantic search)
    - Google News (broad coverage)
    - Indian RSS sources (trusted)
    """



    # -------------------------
    # Setup
    # -------------------------
    tavily = TavilyClient(api_key="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")

    ticker_input = symbol + ".NS"
    ticker = yf.Ticker(ticker_input)

    long_name = ticker.info.get("longName", symbol)

    # Clean company name
    remove_words = ["Limited", "Ltd", "Ltd.", "Company", "Corporation"]
    for word in remove_words:
        long_name = long_name.replace(word, "").strip()

    short_name = " ".join(long_name.split()[:2])

    lines = []

    # =========================================================
    # 1️⃣ Tavily (HIGH QUALITY SEARCH)
    # =========================================================
    try:
        tavily_results = tavily.search(
            query=f"{long_name} stock news India latest",
            search_depth="advanced",
            max_results=5
        )

        for res in tavily_results.get("results", []):
            lines.append(f"[Tavily] {res.get('content')}")

    except Exception as e:
        lines.append(f"[Tavily Error] {str(e)}\n")

    # =========================================================
    # 2️⃣ Google News RSS (REAL-TIME)
    # =========================================================
    try:
        encoded_query = quote(long_name + " stock india")
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            lines.append(f"[Google] {entry.title}")


    except Exception as e:
        lines.append(f"[Google Error] {str(e)}\n")

    # =========================================================
    # 3️⃣ YOUR RSS SOURCES (TRUSTED INDIAN NEWS)
    # =========================================================
    urls = [
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/markets/expert-view/rssfeeds/50649960.cms",
        "https://economictimes.indiatimes.com/news/company/rssfeeds/2143429.cms",
        "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
        "https://www.business-standard.com/rss/markets-106.rss",
        "https://www.livemint.com/rss/markets",
        "https://www.moneycontrol.com/rss/business.xml"
    ]

    try:
        for url in urls:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.title.lower()

                if (
                    symbol.lower() in title
                    or short_name.lower() in title
                    or long_name.lower() in title
                ):
                    lines.append(f"[RSS] {entry.title}")

    except Exception as e:
        lines.append(f"[RSS Error] {str(e)}\n")

    # =========================================================
    # 4️⃣ REMOVE DUPLICATES (IMPORTANT)
    # =========================================================
    unique_lines = list(dict.fromkeys(lines))

    return "\n".join(unique_lines)  # limit output


@tool
def get_technical_analysis(symbol: str) -> str:
    """Fetch technical analysis for an Indian stock using yfinance. Input: stock name like TCS, Reliance, Infosys or any listed stock on NSE or BSE."""
    try:
        ticker_input = symbol + ".NS"
        ticker = yf.Ticker(ticker_input)

        hist = ticker.history(period="14mo", interval="1d")
        # rsi calculation
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # macd calculation
        ema12 = hist["Close"].ewm(span=12).mean()
        ema26 = hist["Close"].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        hist["MACD"] = macd
        hist["Signal"] = signal

        # Calculate moving averages
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()
        hist["MA100"] = hist["Close"].rolling(window=100).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        hist['RSI'] = rsi


        latest_data = hist.iloc[-1]
        lines = []


        # if MACD > Signal → Bullish

        # if MACD < Signal → Bearish
        macd_val = latest_data['MACD']
        signal_val = latest_data['Signal']
        if macd_val > signal_val:
            macd_signal = "Bullish"
        elif macd_val < signal_val:
            macd_signal = "Bearish"
        else:
            macd_signal = "Neutral"
        lines.append(f"MACD: {macd_val:.2f} ({macd_signal})")
        lines.append(f"Signal: {signal_val:.2f}")

        # if close > MA20 → "Price above 20 DMA (Bullish)"
        # if close < MA20 → "Price below 20 DMA (Bearish)"
        # do same for MA50, MA100, MA200
        close_price = latest_data['Close']
        ma20 = latest_data['MA20']
        if close_price > ma20:
            ma20_signal = "Price above 20 DMA (Bullish)"
        elif close_price < ma20:
            ma20_signal = "Price below 20 DMA (Bearish)"
        else:
            ma20_signal = "Price at 20 DMA (Neutral)"
        lines.append(f"MA20: {ma20:.2f} ({ma20_signal})")

        ma50 = latest_data['MA50']
        if close_price > ma50:
            ma50_signal = "Price above 50 DMA (Bullish)"
        elif close_price < ma50:
            ma50_signal = "Price below 50 DMA (Bearish)"
        else:
            ma50_signal = "Price at 50 DMA (Neutral)"
        lines.append(f"MA50: {ma50:.2f} ({ma50_signal})")

        ma100 = latest_data['MA100']
        if close_price > ma100:
            ma100_signal = "Price above 100 DMA (Bullish)"
        elif close_price < ma100:
            ma100_signal = "Price below 100 DMA (Bearish)"
        else:
            ma100_signal = "Price at 100 DMA (Neutral)"
        lines.append(f"MA100: {ma100:.2f} ({ma100_signal})")

        ma200 = latest_data['MA200']
        if close_price > ma200:
            ma200_signal = "Price above 200 DMA (Bullish)"
        elif close_price < ma200:
            ma200_signal = "Price below 200 DMA (Bearish)"
        else:
            ma200_signal = "Price at 200 DMA (Neutral)"
        lines.append(f"MA200: {ma200:.2f} ({ma200_signal})")



        # Do this:
        rsi_val = latest_data['RSI']
        if rsi_val > 70:
            rsi_signal = "Overbought"
        elif rsi_val < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"
        lines.append(f"RSI: {rsi_val:.2f} ({rsi_signal})")

    except Exception as e:
        return f"Error fetching technical analysis: {str(e)}"
    return "\n".join(lines)

@tool
def get_fii_dii_data() -> dict:
    """
    Fetch latest daily FII and DII net buy/sell from NSE.
    Returns a structured dict for easy LLM consumption.
    """
    try:
        url     = "https://www.nseindia.com/api/fiidiiTradeReact"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept":     "application/json",
            "Referer":    "https://www.nseindia.com/",
        }
        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com", timeout=10)   # seed cookies
        data = session.get(url, timeout=15).json()

        fii_net = dii_net = 0.0
        fii_buy = fii_sell = dii_buy = dii_sell = 0.0
        fii_signal = dii_signal = fii_date = dii_date = ""

        for record in data:
            if record["category"] == "FII/FPI":
                fii_net    = float(record["netValue"])
                fii_buy    = float(record.get("buyValue",  0))
                fii_sell   = float(record.get("sellValue", 0))
                fii_signal = "Net Buyer" if fii_net > 0 else "Net Seller"
                fii_date   = record["date"]
            elif record["category"] == "DII":
                dii_net    = float(record["netValue"])
                dii_buy    = float(record.get("buyValue",  0))
                dii_sell   = float(record.get("sellValue", 0))
                dii_signal = "Net Buyer" if dii_net > 0 else "Net Seller"
                dii_date   = record["date"]

        if fii_net > 0:
            market_signal = "BULLISH"
            market_reason = "Foreign investors buying"
        elif fii_net < 0 and dii_net > 0:
            market_signal = "MIXED"
            market_reason = "FII selling but DII supporting"
        else:
            market_signal = "BEARISH"
            market_reason = "Both FII and DII selling"

        return {
            "status":        "ok",
            "date":          fii_date,
            "market_signal": market_signal,
            "market_reason": market_reason,
            "fii": {
                "signal":  fii_signal,
                "net_cr":  fii_net,
                "buy_cr":  fii_buy,
                "sell_cr": fii_sell,
                "date":    fii_date,
            },
            "dii": {
                "signal":  dii_signal,
                "net_cr":  dii_net,
                "buy_cr":  dii_buy,
                "sell_cr": dii_sell,
                "date":    dii_date,
            },
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}



## helper function to calculate return
def calculate_return(symbol: str, period: str = "6mo") -> float:
    if "^" in symbol:
        ticker_input = symbol
    else:
        ticker_input = symbol + ".NS"
    ticker = yf.Ticker(ticker_input)
    hist = ticker.history(period=period)
    first_close = hist["Close"].iloc[0]
    last_close = hist["Close"].iloc[-1]
    return round(((last_close - first_close) / first_close) * 100, 2)

# @tool
# def get_relative_strength(symbol: str) -> str:
#     """
#     Fetch 6-month return of an NSE stock and compare it against:
#     - NIFTY 50 (broad market benchmark)
#     - Sector index (e.g. Nifty IT for Technology stocks)
#     - Market cap index (Large/Mid/Small cap)
#     Use this to find if the stock is outperforming or underperforming the market.
#     Input: NSE stock symbol like TCS, INFY, HDFCBANK
#     """

#     try:
#         ticker = yf.Ticker(symbol + ".NS")

#         sector = ticker.info['sector']

#         market_cap = ticker.info['marketCap']

#         if market_cap > 20000_00_00000:  # 20,000 Cr in rupees
#             cap_category = "Large Cap"
#             cap_index = "^CNX100"
#         elif market_cap > 5000_00_00000:  # 5,000 Cr
#             cap_category = "Mid Cap"
#             cap_index = "^NSEMDCP50"
#         else:
#             cap_category = "Small Cap"
#             cap_index = "^CNXSC"





#         stock_return= calculate_return(symbol)

#         nifty_return = calculate_return(config.INDEX_SYMBOLS["Nifty 50"])

#         sector_return = calculate_return(config.INDEX_SYMBOLS[config.SECTOR_TO_INDEX[sector]])
#         cap_return = calculate_return(config.INDEX_SYMBOLS[config.CAP_TO_INDEX[cap_category]])


#         diff = stock_return - nifty_return
#         if diff > 0:
#             nifty_signal = f"Outperformed NIFTY 50 by {diff:.2f}%"
#         else:
#             nifty_signal = f"Underperformed NIFTY 50 by {abs(diff):.2f}%"

#         diff = stock_return - sector_return
#         if diff > 0:
#             sector_signal = f"Outperformed {config.SECTOR_TO_INDEX[sector]} sector index by {diff:.2f}%"
#         else:
#             sector_signal = f"Underperformed {config.SECTOR_TO_INDEX[sector]} sector index by {abs(diff):.2f}%"

#         diff = stock_return - cap_return
#         if diff > 0:
#             cap_signal = f"Outperformed {cap_category} index by {diff:.2f}%"
#         else:
#             cap_signal = f"Underperformed {cap_category} index by {abs(diff):.2f}%"

#         return f"{nifty_signal}\n{sector_signal}\n{cap_signal}"

#     except Exception as e:
#         return f"Error calculating relative strength: {str(e)}"





@tool
def get_relative_strength(symbol: str) -> dict:
    """
    Hybrid Relative Strength:
    - Return difference (cross-sectional)
    - RS ratio growth (time-series)
    """

    try:
        import yfinance as yf
        import pandas as pd

        ticker = yf.Ticker(symbol + ".NS")

        sector = ticker.info['sector']
        market_cap = ticker.info['marketCap']

        # -------------------------
        # Market Cap Classification
        # -------------------------
        if market_cap > 20000_00_00000:
            cap_category = "Large Cap"
            cap_index = "^CNX100"
        elif market_cap > 5000_00_00000:
            cap_category = "Mid Cap"
            cap_index = "^NSEMDCP50"
        else:
            cap_category = "Small Cap"
            cap_index = "^CNXSC"

        # -------------------------
        # Helper: RS Ratio Growth
        # -------------------------
        def rs_ratio_growth(stock_symbol, index_symbol):
            import yfinance as yf
            import pandas as pd

            stock_df = yf.download(stock_symbol, period="6mo")
            index_df = yf.download(index_symbol, period="6mo")

            # 🔥 Check if data exists
            if stock_df.empty or index_df.empty:
                return None

            if "Close" not in stock_df or "Close" not in index_df:
                return None

            stock = stock_df["Close"]
            index = index_df["Close"]

            # 🔥 Align index (IMPORTANT)
            df = pd.concat([stock, index], axis=1)
            df.columns = ["stock", "index"]
            df = df.dropna()

            if df.empty:
                return None

            rs = df["stock"] / df["index"]

            return ((rs.iloc[-1] / rs.iloc[0]) - 1) * 100
        # -------------------------
        # Returns (your logic)
        # -------------------------
        stock_return = calculate_return(symbol)
        nifty_return = calculate_return(config.INDEX_SYMBOLS["Nifty 50"])
        sector_return = calculate_return(config.INDEX_SYMBOLS[config.SECTOR_TO_INDEX[sector]])
        cap_return = calculate_return(config.INDEX_SYMBOLS[config.CAP_TO_INDEX[cap_category]])

        # -------------------------
        # RS Growth (NEW)
        # -------------------------
        nifty_rs_growth = rs_ratio_growth(symbol+".NS" , "^NSEI")
        sector_rs_growth = rs_ratio_growth(symbol + ".NS", config.INDEX_SYMBOLS[config.SECTOR_TO_INDEX[sector]])
        cap_rs_growth = rs_ratio_growth(symbol + ".NS", cap_index)

        # -------------------------
        # Combine logic
        # -------------------------
        def build_signal(rs_return, rs_growth):
            if rs_return > 0 and rs_growth > 0:
                return "Strong Outperformance"
            elif rs_return > 0:
                return "Outperformance"
            elif rs_growth > 0:
                return "Improving Strength"
            else:
                return "Underperformance"

        # -------------------------
        # Final Output
        # -------------------------
        return {
            "symbol": symbol,
            "period": "6 months",

            "nifty_50": {
                "return_diff": round(stock_return - nifty_return, 2),
                "rs_growth": round(nifty_rs_growth, 2),
                "signal": build_signal(stock_return - nifty_return, nifty_rs_growth)
            },

            "sector": {
                "return_diff": round(stock_return - sector_return, 2),
                "rs_growth": round(sector_rs_growth, 2),
                "signal": build_signal(stock_return - sector_return, sector_rs_growth)
            },

            "market_cap": {
                "return_diff": round(stock_return - cap_return, 2),
                "rs_growth": round(cap_rs_growth, 2),
                "signal": build_signal(stock_return - cap_return, cap_rs_growth)
            }
        }

    except Exception as e:
        return {"error": str(e)}
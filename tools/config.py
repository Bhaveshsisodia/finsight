INDEX_SYMBOLS = {
    # Broad Market
    "Nifty 50": "^NSEI",
    "Nifty 100": "^CNX100",
    "Nifty 200": "^CNX200",
    "Nifty 500": "^CRSLDX",
    "Nifty Next 50": "^NSMIDCP",
    "BSE Sensex": "^BSESN",

    # Market Cap
    "Nifty Midcap 50": "^NSEMDCP50",
    "NIFTY Midcap 100": "^CRSMID",
    "Nifty Midcap 150": "NIFTY_MID_SELECT.NS",
    "NIFTY Smallcap 100": "^CNXSC",


    # Sectoral
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto": "^CNXAUTO",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Infrastructure": "^CNXINFRA",
    "Nifty Media": "^CNXMEDIA",
    "Nifty Financial Services": "^CNXFIN",
    "Nifty PSU Bank": "^CNXPSUBANK",
    "Nifty Commodities": "^CNXCMDT",
    "Nifty Services Sector": "^CNXSERVICE",
    "Nifty MNC": "^CNXMNC",
}

# Sector from yfinance → best matching index
SECTOR_TO_INDEX = {
    "Technology": "Nifty IT",
    "Information Technology": "Nifty IT",
    "Financial Services": "Nifty Financial Services",
    "Banking": "Nifty Bank",
    "Healthcare": "Nifty Pharma",
    "Consumer Cyclical": "Nifty Auto",
    "Energy": "Nifty Energy",
    "Basic Materials": "Nifty Metal",
    "Consumer Defensive": "Nifty FMCG",
    "Real Estate": "Nifty Realty",
    "Industrials": "Nifty Infrastructure",
    "Communication Services": "Nifty Media",
    "Utilities": "Nifty Energy",
}

# Market Cap category → index
CAP_TO_INDEX = {
    "Large Cap": "Nifty 100",
    "Mid Cap": "NIFTY Midcap 100",
    "Small Cap": "NIFTY Smallcap 100",
}
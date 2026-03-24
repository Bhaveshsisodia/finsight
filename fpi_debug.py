"""
DIAGNOSTIC — Run this locally to print the EXACT raw HTML table structure.
Copy-paste the output here so we can fix the column names precisely.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.fpi.nsdl.co.in/",
}

URL = ("https://www.fpi.nsdl.co.in/web/StaticReports/"
       "Fortnightly_Sector_wise_FII_Investment_Data/"
       "FIIInvestSector_Feb282026.html")

r = requests.get(URL, headers=HEADERS, timeout=30)
print(f"HTTP Status: {r.status_code}\n")
html = r.text

soup = BeautifulSoup(html, "html.parser")

print("=" * 80)
print("ALL TABLE ROWS (first 10 rows of each table)")
print("=" * 80)
for ti, table in enumerate(soup.find_all("table")):
    rows = table.find_all("tr")
    print(f"\n--- TABLE {ti} ({len(rows)} rows) ---")
    for ri, row in enumerate(rows[:10]):
        cells = row.find_all(["th", "td"])
        texts = [c.get_text(" ", strip=True) for c in cells]
        spans = [c.get("colspan", "1") for c in cells]
        print(f"  Row {ri:2d} | colspan={spans} | {texts}")

print("\n\n" + "=" * 80)
print("pandas read_html — ALL tables (raw columns)")
print("=" * 80)
try:
    all_tables = pd.read_html(StringIO(html))
    for ti, df in enumerate(all_tables):
        print(f"\n--- pandas Table {ti} ({df.shape[0]} rows × {df.shape[1]} cols) ---")
        print(f"  Columns : {list(df.columns)}")
        print(f"  Row 0   : {list(df.iloc[0]) if len(df) > 0 else 'empty'}")
        print(f"  Row 1   : {list(df.iloc[1]) if len(df) > 1 else 'empty'}")
        print(f"  Row 2   : {list(df.iloc[2]) if len(df) > 2 else 'empty'}")
except Exception as e:
    print(f"read_html error: {e}")

# Also try with different header rows
print("\n\n" + "=" * 80)
print("pandas read_html with header=1 (skip first merged row)")
print("=" * 80)
try:
    all_tables = pd.read_html(StringIO(html), header=1)
    for ti, df in enumerate(all_tables):
        print(f"\n--- pandas Table {ti} (header=1) ({df.shape[0]} rows × {df.shape[1]} cols) ---")
        print(f"  Columns : {list(df.columns)}")
        print(f"  Row 0   : {list(df.iloc[0]) if len(df) > 0 else 'empty'}")
        print(f"  Row 1   : {list(df.iloc[1]) if len(df) > 1 else 'empty'}")
except Exception as e:
    print(f"read_html header=1 error: {e}")

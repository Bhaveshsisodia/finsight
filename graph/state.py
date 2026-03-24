# graph/workflow.py
from typing import TypedDict, Optional, Dict, Any

class StockAnalysisState(TypedDict):
    symbol: str
    fundamental_data: str
    technical_data: str
    news_data: str
    fii_dii_data: str
    relative_strength: str


    # score fields — new!
    fundamental_score: int
    technical_score: int
    news_score: int
    fii_dii_score: int
    relative_strength_score: int
    fundamental_analysis: Optional[Dict[str, Any]]

    technical_analysis: Optional[Dict[str, Any]]
    news_analysis : Optional[Dict[str, Any]]


    # final output
    probability_score: str

    fpi_score: int
    fpi_analysis: Optional[Dict[str, Any]]
    fpi_raw: Optional[Dict[str, Any]]
    relative_data: str
    relative_score: int
    relative_analysis: Optional[Dict[str, Any]]

    final_score: float
    signal: str
    confidence: float
    report: str

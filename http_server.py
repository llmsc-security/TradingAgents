"""
HTTP Server for TradingAgents CLI Tool

This module provides a FastAPI HTTP server that wraps the TradingAgentsGraph
class to provide REST API endpoints for trading analysis.
"""

import os
import json
from datetime import date
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}

# Initialize the TradingAgentsGraph
# Note: The graph will be initialized on first request to avoid blocking startup
trading_graph_instance: Optional[TradingAgentsGraph] = None


def get_trading_graph() -> TradingAgentsGraph:
    """Lazy initialization of TradingAgentsGraph."""
    global trading_graph_instance
    if trading_graph_instance is None:
        trading_graph_instance = TradingAgentsGraph(debug=False, config=config)
    return trading_graph_instance


# Create FastAPI app
app = FastAPI(
    title="TradingAgents API",
    description="Multi-Agents LLM Financial Trading Framework API",
    version="1.0.0",
)


class DecisionRequest(BaseModel):
    """Request model for decision endpoint."""
    symbol: str = Field(..., description="Stock ticker symbol (e.g., NVDA, AAPL)")
    date: str = Field(..., description="Analysis date in YYYY-MM-DD format")


class StockInfo(BaseModel):
    """Response model for stock info."""
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    market_cap: Optional[str] = None
    volume: Optional[str] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    timestamp: str


class DecisionResponse(BaseModel):
    """Response model for decision endpoint."""
    success: bool
    symbol: str
    date: str
    decision: Optional[Dict[str, Any]] = None
    full_state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current status of the TradingAgents service.
    """
    return {
        "status": "healthy",
        "service": "TradingAgents API",
        "version": "1.0.0",
        "timestamp": date.today().isoformat()
    }


@app.post("/api/decision", tags=["Trading"], response_model=DecisionResponse)
async def get_trading_decision(request: DecisionRequest):
    """
    Get a trading decision for a stock symbol on a specific date.

    This endpoint runs the full TradingAgents analysis including:
    - Analyst Team Reports (Market, Social, News, Fundamentals)
    - Research Team Decision (Bull/Bear Debate)
    - Trading Team Plan
    - Risk Management Team Decision
    - Portfolio Manager Final Decision

    Args:
        request: DecisionRequest with symbol and date

    Returns:
        DecisionResponse with the trading decision and analysis
    """
    try:
        symbol = request.symbol.upper()
        trade_date = request.date

        # Validate date format
        try:
            year, month, day = map(int, trade_date.split('-'))
            date(year, month, day)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Please use YYYY-MM-DD format."
            )

        # Get trading graph instance
        graph = get_trading_graph()

        # Run the analysis
        final_state, decision = graph.propagate(symbol, trade_date)

        return DecisionResponse(
            success=True,
            symbol=symbol,
            date=trade_date,
            decision=decision,
            full_state=final_state
        )

    except HTTPException:
        raise
    except Exception as e:
        return DecisionResponse(
            success=False,
            symbol=request.symbol.upper() if hasattr(request, 'symbol') else "",
            date=request.date if hasattr(request, 'date') else "",
            decision=None,
            error=str(e)
        )


@app.get("/api/stock", tags=["Stock Data"], response_model=StockInfo)
async def get_stock_info(
    symbol: str = Query(..., description="Stock ticker symbol (e.g., NVDA, AAPL)")
):
    """
    Get basic stock information for a symbol.

    This endpoint provides quick access to stock data without running
    the full analysis pipeline.

    Args:
        symbol: Stock ticker symbol

    Returns:
        StockInfo with basic stock data
    """
    try:
        symbol = symbol.upper()

        # Try to import get_stock_data from the agents
        try:
            from tradingagents.agents.utils.agent_utils import get_stock_data
            from tradingagents.dataflows.config import set_config
            from tradingagents.default_config import DEFAULT_CONFIG

            # Set up config for the tool
            set_config(DEFAULT_CONFIG)

            # Get stock data using the same tool the agents use
            stock_data = get_stock_data(symbol)

            # Parse the stock data
            info = StockInfo(symbol=symbol)

            if isinstance(stock_data, dict):
                info.price = stock_data.get('current_price')
                info.change = stock_data.get('change')
                info.change_percent = stock_data.get('change_percent')
                info.market_cap = stock_data.get('market_cap')
                info.volume = stock_data.get('volume')
                info.pe_ratio = stock_data.get('pe_ratio')
                info.dividend_yield = stock_data.get('dividend_yield')
                info.fifty_two_week_high = stock_data.get('fifty_two_week_high')
                info.fifty_two_week_low = stock_data.get('fifty_two_week_low')
                info.name = stock_data.get('company_name') or stock_data.get('name')

            return info

        except Exception as e:
            # If the tool is not available, return minimal info
            return StockInfo(
                symbol=symbol,
                error=f"Could not fetch stock data: {str(e)}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "TradingAgents API",
        "version": "1.0.0",
        "description": "Multi-Agents LLM Financial Trading Framework",
        "endpoints": {
            "health": "/health",
            "decision": "/api/decision (POST)",
            "stock": "/api/stock (GET)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=11360,
        reload=False
    )

"""
Application constants and configuration
"""

# Application Information
APP_NAME = "SUDNAXI"
APP_FULL_NAME = "SUDNAXI Trading Intelligence Platform"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Stock Trading Analysis Platform"

# Market Configuration
SUPPORTED_MARKETS = {
    "US": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"],
    "India": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HINDUNILVR.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS"],
    "UK": ["VOD.L", "BP.L", "SHEL.L", "AZN.L", "ULVR.L", "HSBA.L", "LLOY.L", "BARC.L", "BT-A.L", "GSK.L"],
    "Germany": ["SAP.DE", "ASML.AS", "ADYEN.AS", "ASME.AS", "PHIA.AS", "HEIA.AS", "INGA.AS", "RDSA.AS", "UNA.AS", "NESN.SW"],
    "Japan": ["7203.T", "6758.T", "6861.T", "9984.T", "8306.T", "6098.T", "4519.T", "8411.T", "6367.T", "4063.T"],
    "China": ["BABA", "TCEHY", "JD", "BIDU", "NTES", "PDD", "TME", "BILI", "WB", "VIPS"],
    "Canada": ["SHOP.TO", "CNR.TO", "TD.TO", "RY.TO", "BNS.TO", "BMO.TO", "CM.TO", "CNQ.TO", "CP.TO", "ABX.TO"],
    "Australia": ["CBA.AX", "BHP.AX", "ANZ.AX", "WBC.AX", "NAB.AX", "CSL.AX", "WES.AX", "MQG.AX", "TLS.AX", "RIO.AX"],
    "Brazil": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "BBAS3.SA", "SUZB3.SA", "WEGE3.SA", "MGLU3.SA", "LREN3.SA"]
}

# Time Periods
TIME_PERIODS = {
    "1 Day": "1d",
    "5 Days": "5d", 
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

# Technical Analysis Settings
TECHNICAL_INDICATORS = {
    "RSI_PERIOD": 14,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BB_PERIOD": 20,
    "BB_STD": 2,
    "SMA_SHORT": 20,
    "SMA_LONG": 50
}

# Trading Simulation
SIMULATION_SETTINGS = {
    "INITIAL_BALANCE": 10000.0,
    "COMMISSION_RATE": 0.001,  # 0.1%
    "MIN_TRADE_SIZE": 100.0,
    "MAX_POSITION_SIZE": 0.35  # 35% of portfolio
}

# UI Colors
UI_COLORS = {
    "PRIMARY": "#00FF88",
    "SECONDARY": "#00D97F", 
    "SUCCESS": "#10B981",
    "WARNING": "#F59E0B",
    "ERROR": "#EF4444",
    "INFO": "#3B82F6",
    "BACKGROUND": "#0a0e27",
    "SURFACE": "#1e293b",
    "TEXT": "#f8fafc"
}

# Chart Settings
CHART_CONFIG = {
    "THEME": "plotly_dark",
    "HEIGHT": 600,
    "MARGIN": {"l": 40, "r": 40, "t": 40, "b": 40},
    "FONT_SIZE": 12,
    "COLORS": ["#00FF88", "#00D97F", "#10B981", "#F59E0B", "#EF4444", "#3B82F6"]
}
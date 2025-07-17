import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import time
from utils.data_fetcher import StockDataFetcher
from utils.chart_generator import ChartGenerator
from utils.news_sentiment import NewsSentimentAnalyzer
from utils.enhanced_backtesting import EnhancedBacktestingEngine
from utils.help_system import help_system
from ml.adaptive_strategy import AdaptiveStrategyEngine
from database.models import init_database, get_db_session

# Configure page
st.set_page_config(
    page_title="SUDNAXI - Professional Trading Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional UI Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.main .block-container {
    padding: 1rem 2rem;
    max-width: 100%;
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 25%, #16213e 50%, #0a0e27 100%);
    background-attachment: fixed;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(0, 255, 136, 0.15);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif;
    color: #f8fafc;
    font-weight: 600;
    letter-spacing: -0.025em;
}

.stButton > button {
    background: linear-gradient(135deg, #00FF88 0%, #00D97F 50%, #00C777 100%);
    color: #000;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #00D97F 0%, #00C777 50%, #00B570 100%);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 255, 136, 0.4);
}

.stButton > button:active {
    transform: translateY(-1px) scale(0.98);
}

/* Sophisticated form controls */
.stSelectbox > div > div {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    color: #f8fafc;
}

.stTextInput > div > div > input {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    color: #f8fafc;
    padding: 0.75rem 1rem;
}

/* Premium notification styling */
.stSuccess {
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 217, 127, 0.05) 100%);
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    backdrop-filter: blur(10px);
}

.stInfo {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    backdrop-filter: blur(10px);
}

.stWarning {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    backdrop-filter: blur(10px);
}

/* Advanced expander styling */
.streamlit-expanderHeader {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    border-color: #00FF88;
    box-shadow: 0 4px 16px rgba(0, 255, 136, 0.2);
}

/* Premium chart containers */
.stPlotlyChart {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
}

/* Elegant section dividers */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #00FF88 20%, #00D97F 50%, #00FF88 80%, transparent 100%);
    margin: 3rem 0;
    opacity: 0.6;
}

/* Premium card containers */
.metric-card {
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00FF88 0%, #00D97F 50%, #00FF88 100%);
    opacity: 0.8;
}

/* Sidebar enhancements */
.css-1d391kg {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
    border-radius: 12px;
    padding: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #94a3b8;
    border: none;
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00FF88 0%, #00D97F 100%);
    color: #000;
    box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
}

/* Loading animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 2s infinite;
}

/* Professional scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1e293b;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00FF88, #00D97F);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #00D97F, #00C777);
}

/* Responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
}

/* Header glow effect */
.header-glow {
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = ""

def main():
    # Initialize database
    try:
        init_database()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
    
    # Market-Ready Professional Header
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); border-radius: 20px; margin-bottom: 2rem; border: 1px solid #475569; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00FF88 0%, #00D97F 50%, #00FF88 100%);"></div>
        <h1 class="header-glow" style="color: #00FF88; font-size: 3.5rem; margin: 0; font-weight: 700; letter-spacing: -0.02em;">🚀 SUDNAXI</h1>
        <h2 style="color: #f8fafc; font-size: 1.8rem; margin: 1rem 0; font-weight: 400; opacity: 0.9;">AI-Powered Trading Intelligence Platform</h2>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap;">
            <span style="color: #00FF88; font-weight: 600;">📊 ML Backtesting</span>
            <span style="color: #00D97F; font-weight: 600;">🤖 Adaptive AI</span>
            <span style="color: #22c55e; font-weight: 600;">📈 Real-time Analysis</span>
            <span style="color: #10b981; font-weight: 600;">📰 News Sentiment</span>
        </div>
        <p style="color: #94a3b8; margin: 1.5rem 0 0 0; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto;">Professional-grade trading platform with machine learning, adaptive strategies, and comprehensive market intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Important disclaimer
    with st.expander("⚠️ Important Disclaimer - READ BEFORE USING", expanded=False):
        st.warning("""
        **EDUCATIONAL PURPOSE ONLY - NOT INVESTMENT ADVICE**
        
        This application is designed for educational purposes and trading simulation only. Please note:
        
        🚨 **Trading Simulation Only**: This app provides a paper trading simulator, not real trading capabilities
        
        📊 **No Real Money**: All trades are simulated with virtual money for learning purposes
        
        ⚡ **Data Limitations**: Yahoo Finance free API has limitations - real trading requires premium data feeds
        
        🎯 **Educational Tool**: Use this to learn technical analysis and practice trading strategies risk-free
        
        💼 **Investment Advice**: This is NOT professional investment advice. Always consult qualified financial advisors
        
        🔒 **Risk Warning**: Real trading involves significant financial risk. Never invest more than you can afford to lose
        
        **For Real Trading**: Use licensed brokers with proper risk management, real-time data, and professional tools
        """)
    
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Stock Selection")
        
        # Global stock symbols organized by region
        stock_regions = {
            "🇺🇸 US Stocks": {
                "Apple Inc. (AAPL)": "AAPL",
                "Microsoft Corp. (MSFT)": "MSFT", 
                "Amazon.com Inc. (AMZN)": "AMZN",
                "Tesla Inc. (TSLA)": "TSLA",
                "Alphabet Inc. (GOOGL)": "GOOGL",
                "Meta Platforms (META)": "META",
                "NVIDIA Corp. (NVDA)": "NVDA",
                "Netflix Inc. (NFLX)": "NFLX",
                "Berkshire Hathaway (BRK-B)": "BRK-B",
                "Johnson & Johnson (JNJ)": "JNJ",
                "JPMorgan Chase (JPM)": "JPM",
                "Visa Inc. (V)": "V"
            },
            "🇮🇳 Indian Stocks": {
                "Reliance Industries (RELIANCE.NS)": "RELIANCE.NS",
                "Tata Consultancy Services (TCS.NS)": "TCS.NS",
                "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS",
                "Infosys (INFY.NS)": "INFY.NS",
                "ICICI Bank (ICICIBANK.NS)": "ICICIBANK.NS",
                "State Bank of India (SBIN.NS)": "SBIN.NS",
                "Bharti Airtel (BHARTIARTL.NS)": "BHARTIARTL.NS",
                "ITC Ltd (ITC.NS)": "ITC.NS",
                "Hindustan Unilever (HINDUNILVR.NS)": "HINDUNILVR.NS",
                "Larsen & Toubro (LT.NS)": "LT.NS"
            },
            "🇬🇧 UK Stocks": {
                "Royal Dutch Shell (SHEL.L)": "SHEL.L",
                "AstraZeneca (AZN.L)": "AZN.L",
                "British Petroleum (BP.L)": "BP.L",
                "HSBC Holdings (HSBA.L)": "HSBA.L",
                "Vodafone Group (VOD.L)": "VOD.L",
                "Rio Tinto (RIO.L)": "RIO.L",
                "Unilever (ULVR.L)": "ULVR.L",
                "BT Group (BT-A.L)": "BT-A.L"
            },
            "🇩🇪 German Stocks": {
                "SAP SE (SAP.DE)": "SAP.DE",
                "Siemens AG (SIE.DE)": "SIE.DE",
                "ASML Holding (ASML.AS)": "ASML.AS",
                "Allianz SE (ALV.DE)": "ALV.DE",
                "Deutsche Bank (DBK.DE)": "DBK.DE",
                "BMW AG (BMW.DE)": "BMW.DE",
                "Volkswagen (VOW3.DE)": "VOW3.DE"
            },
            "🇯🇵 Japanese Stocks": {
                "Toyota Motor (7203.T)": "7203.T",
                "Sony Group (6758.T)": "6758.T",
                "SoftBank Group (9984.T)": "9984.T",
                "Nintendo (7974.T)": "7974.T",
                "Honda Motor (7267.T)": "7267.T",
                "Mitsubishi UFJ (8306.T)": "8306.T"
            },
            "🇨🇳 Chinese Stocks": {
                "Alibaba Group (BABA)": "BABA",
                "Tencent Holdings (0700.HK)": "0700.HK",
                "Taiwan Semiconductor (TSM)": "TSM",
                "JD.com (JD)": "JD",
                "Baidu Inc (BIDU)": "BIDU",
                "NetEase Inc (NTES)": "NTES"
            },
            "🇨🇦 Canadian Stocks": {
                "Shopify Inc (SHOP.TO)": "SHOP.TO",
                "Royal Bank of Canada (RY.TO)": "RY.TO",
                "Canadian National Railway (CNR.TO)": "CNR.TO",
                "Brookfield Asset Management (BAM.TO)": "BAM.TO"
            },
            "🇦🇺 Australian Stocks": {
                "BHP Group (BHP.AX)": "BHP.AX",
                "Commonwealth Bank (CBA.AX)": "CBA.AX",
                "CSL Limited (CSL.AX)": "CSL.AX",
                "Westpac Banking (WBC.AX)": "WBC.AX"
            },
            "🇧🇷 Brazilian Stocks": {
                "Petrobras (PETR4.SA)": "PETR4.SA",
                "Vale SA (VALE3.SA)": "VALE3.SA",
                "Itau Unibanco (ITUB4.SA)": "ITUB4.SA",
                "Banco do Brasil (BBAS3.SA)": "BBAS3.SA"
            }
        }
        
        # Region selection
        selected_region = st.selectbox(
            "Select Market Region",
            options=list(stock_regions.keys()),
            index=0
        )
        
        popular_stocks = stock_regions[selected_region]
        
        # Stock selection dropdown
        selected_stock_display = st.selectbox(
            "Select a Stock",
            options=list(popular_stocks.keys()),
            index=0,
            help="Choose from popular, reliable stock symbols"
        )
        stock_symbol = popular_stocks[selected_stock_display]
        
        # Manual input option
        st.subheader("Or Enter Custom Symbol")
        custom_symbol = st.text_input(
            "Custom Stock Symbol",
            placeholder="e.g., AAPL, MSFT",
            help="Enter any valid stock ticker symbol"
        ).upper()
        
        if custom_symbol:
            stock_symbol = custom_symbol
        
        # Time period selection
        time_periods = {
            "1 Week": "1wk",
            "1 Month": "1mo", 
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        
        selected_period = st.selectbox(
            "Time Period",
            options=list(time_periods.keys()),
            index=4  # Default to 1 Year
        )
        
        # Chart type selection
        chart_types = ["Candlestick", "Line", "OHLC", "Bollinger Bands", "MACD Analysis"]
        chart_type = st.selectbox("Chart Type", chart_types)
        
        # Advanced Features Section
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #00FF88; margin: 0 0 1rem 0;">🚀 Advanced Features</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature toggles with enhanced styling
        col1, col2 = st.columns(2)
        
        with col1:
            auto_refresh = st.checkbox("🔄 Real-time Auto-refresh", value=False, 
                                     help="Enable automatic data refresh for live trading")
            show_news = st.checkbox("📰 News Sentiment Analysis", value=True,
                                  help="AI-powered news sentiment analysis for market insights")
            use_ml_backtest = st.checkbox("🤖 ML-Enhanced Backtesting", value=True,
                                        help="Use machine learning for adaptive strategy backtesting")
            
        with col2:
            show_backtest = st.checkbox("📊 Advanced Backtesting", value=True,
                                      help="Comprehensive backtesting with detailed analytics")
            save_results = st.checkbox("💾 Save to Database", value=True,
                                     help="Store analysis results in database for historical tracking")
            enable_alerts = st.checkbox("🔔 Trading Alerts", value=False,
                                      help="Enable trading signal alerts and notifications")
        
        # Trading simulator toggle
        trading_mode = st.checkbox("Enable Trading Simulator", value=False)
        
        # Add comprehensive help system to sidebar
        help_system.add_help_sidebar()
        
        if trading_mode:
            st.subheader("💰 Trading Simulator")
            if 'portfolio_balance' not in st.session_state:
                st.session_state.portfolio_balance = 1000.0  # Starting with $1000
            if 'portfolio_holdings' not in st.session_state:
                st.session_state.portfolio_holdings = {}
            
            st.metric("Portfolio Balance", f"${st.session_state.portfolio_balance:.2f}")
            
            # Investment amount
            investment_amount = st.number_input(
                "Investment Amount ($)", 
                min_value=1.0, 
                max_value=float(st.session_state.portfolio_balance),
                value=min(100.0, st.session_state.portfolio_balance),
                step=1.0
            )
        
        # Fetch data button
        fetch_button = st.button("Fetch Stock Data", type="primary")
        
        # Real-time refresh interval selector
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh Interval",
                options=[5, 10, 15, 30, 60],
                index=2,
                format_func=lambda x: f"{x} seconds"
            )
    
    # Main content area
    if fetch_button or (stock_symbol and stock_symbol != st.session_state.current_symbol):
        if stock_symbol:
            with st.spinner(f"Fetching data for {stock_symbol}..."):
                try:
                    # Initialize data fetcher
                    fetcher = StockDataFetcher()
                    
                    # Fetch stock data
                    stock_info = fetcher.get_stock_info(stock_symbol)
                    historical_data = fetcher.get_historical_data(
                        stock_symbol, 
                        time_periods[selected_period]
                    )
                    
                    if stock_info and historical_data is not None and not historical_data.empty:
                        # Calculate technical indicators
                        historical_data_with_indicators = fetcher.calculate_technical_indicators(historical_data.copy())
                        
                        # Generate buy/sell signals with market sentiment
                        trading_signal = fetcher.generate_buy_sell_signal(historical_data_with_indicators, stock_symbol)
                        
                        # Fetch news sentiment if enabled
                        news_data = None
                        sentiment_summary = None
                        if show_news:
                            try:
                                with st.spinner("🔄 Analyzing news sentiment..."):
                                    news_analyzer = NewsSentimentAnalyzer()
                                    news_data = news_analyzer.get_stock_news(stock_symbol, limit=15)
                                    
                                    if news_data:
                                        sentiment_summary = news_analyzer.get_overall_sentiment(news_data)
                                        st.success(f"✅ Analyzed {len(news_data)} news articles for sentiment")
                                    else:
                                        st.info("📰 No recent news articles found for this stock")
                                        news_data = None
                                        sentiment_summary = None
                            except Exception as e:
                                st.warning(f"News analysis temporarily unavailable: {e}")
                                news_data = None
                                sentiment_summary = None
                        
                        # Run enhanced backtesting if enabled
                        backtest_results = None
                        if show_backtest:
                            try:
                                with st.spinner("🤖 Running ML-enhanced backtesting..."):
                                    enhanced_engine = EnhancedBacktestingEngine(initial_capital=10000)
                                    backtest_results = enhanced_engine.run_comprehensive_backtest(
                                        stock_symbol, 
                                        historical_data_with_indicators, 
                                        use_ml=use_ml_backtest,
                                        adaptation_frequency=20
                                    )
                                    if backtest_results.get('error'):
                                        st.warning(f"Enhanced backtesting: {backtest_results['error']}")
                                    else:
                                        st.success(f"✅ Completed ML backtesting with {backtest_results['performance_metrics'].get('total_trades', 0)} trades")
                            except Exception as e:
                                st.warning(f"Enhanced backtesting error: {e}")
                                # Fallback to basic backtesting
                                try:
                                    from utils.backtesting_engine import BacktestingEngine
                                    basic_engine = BacktestingEngine()
                                    backtest_results = basic_engine.run_backtest(stock_symbol, "1y", 10000)
                                except Exception as e2:
                                    st.error(f"All backtesting failed: {e2}")
                        
                        st.session_state.stock_data = {
                            'info': stock_info,
                            'historical': historical_data_with_indicators,
                            'symbol': stock_symbol,
                            'period': selected_period,
                            'trading_signal': trading_signal,
                            'news_data': news_data,
                            'sentiment_summary': sentiment_summary,
                            'backtest_results': backtest_results,
                            'last_updated': datetime.now()
                        }
                        st.session_state.current_symbol = stock_symbol
                        st.success(f"✅ Successfully loaded comprehensive data for {stock_symbol}")
                    else:
                        st.error(f"No data found for symbol '{stock_symbol}'. Please check the symbol and try again.")
                        st.session_state.stock_data = None
                        
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")
                    st.session_state.stock_data = None
        else:
            st.warning("Please enter a stock symbol")
    
    # Auto-refresh logic
    if auto_refresh and 'stock_data' in st.session_state and st.session_state.stock_data:
        # Create a placeholder for countdown
        countdown_placeholder = st.empty()
        
        # Countdown timer
        for remaining in range(refresh_interval, 0, -1):
            countdown_placeholder.info(f"🔄 Auto-refresh in {remaining} seconds...")
            time.sleep(1)
        
        countdown_placeholder.empty()
        st.rerun()
    
    # Display data if available
    if st.session_state.stock_data:
        display_stock_analysis(chart_type)
    else:
        # Welcome message
        st.info("👆 Enter a stock symbol in the sidebar to get started!")
        
        # Sample symbols
        st.subheader("Popular Stock Symbols")
        col1, col2, col3, col4 = st.columns(4)
        
        sample_symbols = [
            ("AAPL", "Apple Inc."),
            ("GOOGL", "Alphabet Inc."),
            ("MSFT", "Microsoft Corp."),
            ("TSLA", "Tesla Inc."),
            ("AMZN", "Amazon.com Inc."),
            ("META", "Meta Platforms"),
            ("NVDA", "NVIDIA Corp."),
            ("NFLX", "Netflix Inc.")
        ]
        
        for i, (symbol, name) in enumerate(sample_symbols):
            col = [col1, col2, col3, col4][i % 4]
            with col:
                if st.button(f"{symbol}\n{name}", key=f"sample_{symbol}"):
                    st.session_state.current_symbol = symbol
                    st.rerun()

def display_stock_analysis(chart_type):
    """Display the complete stock analysis"""
    data = st.session_state.stock_data
    stock_info = data['info']
    historical_data = data['historical']
    symbol = data['symbol']
    
    # Trading Signal Section (prominently displayed)
    trading_signal = data.get('trading_signal', {})
    signal_color_map = {
        'green': '#00FF88',
        'lightgreen': '#90EE90', 
        'yellow': '#FFD700',
        'orange': '#FFA500',
        'red': '#FF4444',
        'gray': '#888888'
    }
    
    st.markdown("---")
    col_signal, col_strength = st.columns([2, 1])
    
    with col_signal:
        signal_color = signal_color_map.get(trading_signal.get('color', 'gray'), '#888888')
        st.markdown(
            f"<div style='padding: 20px; background-color: {signal_color}20; border-left: 5px solid {signal_color}; border-radius: 5px;'>"
            f"<h2 style='color: {signal_color}; margin: 0;'>🚨 TRADING SIGNAL: {trading_signal.get('signal', 'UNKNOWN')}</h2>"
            f"<p style='margin: 5px 0; color: #FAFAFA;'>Signal Strength: {trading_signal.get('strength', 0):.1f}</p>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    with col_strength:
        if trading_signal.get('rsi') is not None:
            st.metric(
                label="RSI", 
                value=f"{trading_signal['rsi']:.1f}",
                help="RSI below 30 = oversold, above 70 = overbought"
            )
    
    # Signal reasons
    if trading_signal.get('reasons'):
        st.subheader("📋 Signal Analysis")
        for reason in trading_signal['reasons']:
            st.write(f"• {reason}")
    
    # Buy/Sell Ratio and Market Sentiment Section
    if trading_signal.get('buy_sell_data'):
        st.markdown("---")
        
        # Professional section header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #262730 0%, #1a1a2e 100%); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #404040;">
            <h2 style="color: #00FF88; margin: 0; display: flex; align-items: center;">
                📊 Market Sentiment & Analyst Consensus
                <span style="margin-left: auto; font-size: 0.8rem; color: #CCCCCC;">Professional Analysis</span>
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        buy_sell_data = trading_signal['buy_sell_data']
        
        # Buy/Sell Ratio display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            buy_color = "#00FF88" if buy_sell_data['buy_ratio'] > 50 else "#FFA500"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {buy_color}20 0%, {buy_color}10 100%);">
                    <h3 style="color: {buy_color}; margin: 0; font-size: 2rem;">{buy_sell_data['buy_ratio']}%</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Buy Ratio</p>
                    <small style="color: #CCCCCC;">Bullish sentiment</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            sell_color = "#FF4444" if buy_sell_data['sell_ratio'] > 50 else "#FFA500"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {sell_color}20 0%, {sell_color}10 100%);">
                    <h3 style="color: {sell_color}; margin: 0; font-size: 2rem;">{buy_sell_data['sell_ratio']}%</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Sell Ratio</p>
                    <small style="color: #CCCCCC;">Bearish sentiment</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            sentiment_color = "#00FF88" if buy_sell_data['sentiment_color'] == 'green' else "#FF4444" if buy_sell_data['sentiment_color'] == 'red' else "#FFD700"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {sentiment_color}20 0%, {sentiment_color}10 100%);">
                    <h3 style="color: {sentiment_color}; margin: 0; font-size: 1.5rem;">{buy_sell_data['market_sentiment']}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Market Sentiment</p>
                    <small style="color: #CCCCCC;">Overall direction</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            upside_color = "#00FF88" if buy_sell_data['upside_potential'] > 0 else "#FF4444"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {upside_color}20 0%, {upside_color}10 100%);">
                    <h3 style="color: {upside_color}; margin: 0; font-size: 1.5rem;">{buy_sell_data['upside_potential']:+.1f}%</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Price Target</p>
                    <small style="color: #CCCCCC;">Analyst consensus</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Analyst recommendations breakdown
        if buy_sell_data['analyst_recommendations']:
            st.subheader("📈 Analyst Recommendations")
            rec_data = buy_sell_data['analyst_recommendations']
            
            rec_col1, rec_col2, rec_col3, rec_col4, rec_col5 = st.columns(5)
            
            with rec_col1:
                st.metric("Strong Buy", rec_data['strong_buy'])
            with rec_col2:
                st.metric("Buy", rec_data['buy'])
            with rec_col3:
                st.metric("Hold", rec_data['hold'])
            with rec_col4:
                st.metric("Sell", rec_data['sell'])
            with rec_col5:
                st.metric("Strong Sell", rec_data['strong_sell'])
    
    # News Sentiment Analysis Section
    if data.get('news_data') and data.get('sentiment_summary'):
        st.markdown("---")
        
        # Professional section header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #262730 0%, #1a1a2e 100%); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #404040;">
            <h2 style="color: #00FF88; margin: 0; display: flex; align-items: center;">
                📰 News Sentiment Analysis
                <span style="margin-left: auto; font-size: 0.8rem; color: #CCCCCC;">Real-time Market Intelligence</span>
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        sentiment_summary = data['sentiment_summary']
        news_data = data['news_data']
        
        # Overall sentiment display with enhanced cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sentiment_color = "#00FF88" if sentiment_summary['overall_score'] > 0 else "#FF4444" if sentiment_summary['overall_score'] < 0 else "#FFD700"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {sentiment_color}20 0%, {sentiment_color}10 100%);">
                    <h3 style="color: {sentiment_color}; margin: 0; font-size: 1.5rem;">{sentiment_summary['overall_label']}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA; font-size: 1.2rem;">Score: {sentiment_summary['overall_score']:.3f}</p>
                    <small style="color: #CCCCCC;">Overall Market Sentiment</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: #00FF88; margin: 0; font-size: 2rem;">{sentiment_summary['positive_count']}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Positive News</p>
                    <small style="color: #CCCCCC;">Bullish sentiment articles</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: #FF4444; margin: 0; font-size: 2rem;">{sentiment_summary['negative_count']}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Negative News</p>
                    <small style="color: #CCCCCC;">Bearish sentiment articles</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: #00FF88; margin: 0; font-size: 2rem;">{sentiment_summary['total_articles']}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA;">Total Articles</p>
                    <small style="color: #CCCCCC;">News sources analyzed</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # News impact assessment with enhanced styling
        if sentiment_summary['overall_score'] != 0:
            from utils.news_sentiment import NewsSentimentAnalyzer
            analyzer = NewsSentimentAnalyzer()
            impact_assessment = analyzer.get_sentiment_impact_on_price(sentiment_summary['overall_score'])
            
            impact_color = impact_assessment['color']
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, {impact_color}20 0%, {impact_color}10 100%); border-left: 4px solid {impact_color}; border-radius: 10px; padding: 1.5rem; margin: 1rem 0;">
                    <h4 style="color: {impact_color}; margin: 0;">📊 Market Impact Assessment</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #FAFAFA; font-size: 1.1rem;">{impact_assessment['expected_movement']}</p>
                    <small style="color: #CCCCCC;">Confidence Level: {impact_assessment['confidence']:.0f}%</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Recent news articles with enhanced display
        st.markdown("""
        <div style="background: linear-gradient(135deg, #262730 0%, #1a1a2e 100%); border-radius: 12px; padding: 1rem; margin: 1rem 0; border: 1px solid #404040;">
            <h3 style="color: #00FF88; margin: 0;">📄 Recent News Articles</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if news_data:
            for i, article in enumerate(news_data[:5]):  # Show top 5 articles
                # Enhanced expander with professional styling
                title_display = f"{article['title'][:80]}..." if len(article['title']) > 80 else article['title']
                
                with st.expander(f"📰 {title_display}", expanded=False):
                    col_content, col_sentiment = st.columns([3, 1])
                    
                    with col_content:
                        st.markdown(f"""
                        <div style="background: #262730; border-radius: 8px; padding: 1rem; border: 1px solid #404040;">
                            <p style="margin: 0; color: #CCCCCC;"><strong style="color: #00FF88;">Source:</strong> {article['source']}</p>
                            <p style="margin: 0.5rem 0; color: #CCCCCC;"><strong style="color: #00FF88;">Published:</strong> {article['published']}</p>
                        """, unsafe_allow_html=True)
                        
                        if article['summary']:
                            summary_text = article['summary'][:300] + "..." if len(article['summary']) > 300 else article['summary']
                            st.markdown(f"<p style='margin: 0.5rem 0; color: #FAFAFA;'><strong style='color: #00FF88;'>Summary:</strong> {summary_text}</p>", unsafe_allow_html=True)
                        
                        if article['link']:
                            st.markdown(f"<a href='{article['link']}' target='_blank' style='color: #00FF88; text-decoration: none;'>🔗 Read Full Article</a>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_sentiment:
                        sentiment_color = "#00FF88" if article['sentiment_score'] > 0 else "#FF4444" if article['sentiment_score'] < 0 else "#FFD700"
                        st.markdown(
                            f"""
                            <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {sentiment_color}20 0%, {sentiment_color}10 100%);">
                                <h4 style="color: {sentiment_color}; margin: 0;">{article['sentiment_label']}</h4>
                                <p style="margin: 0.5rem 0; color: #FAFAFA;">Score: {article['sentiment_score']:.3f}</p>
                                <p style="margin: 0; color: #CCCCCC;">Relevance: {article['relevance']:.2f}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
        else:
            st.info("📰 No recent news articles available for this symbol. News sentiment analysis requires active news coverage.")
    else:
        # Show message when news sentiment is disabled
        if not data.get('news_data') and data.get('symbol'):
            st.markdown("""
            <div style="background: #262730; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #404040;">
                <h3 style="color: #FFD700; margin: 0;">📰 News Sentiment Analysis</h3>
                <p style="margin: 0.5rem 0 0 0; color: #CCCCCC;">Enable "Show News Sentiment" in the sidebar to view real-time news analysis for market insights.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Trading simulator actions
    if 'trading_mode' in locals() and trading_mode and trading_signal.get('signal') != 'UNKNOWN':
        col_buy, col_sell = st.columns(2)
        
        current_price = stock_info.get('currentPrice', 0)
        symbol = data['symbol']
        
        with col_buy:
            if st.button(f"🟢 BUY {symbol}", type="primary"):
                if investment_amount <= st.session_state.portfolio_balance:
                    shares = investment_amount / current_price
                    
                    if symbol in st.session_state.portfolio_holdings:
                        st.session_state.portfolio_holdings[symbol]['shares'] += shares
                        st.session_state.portfolio_holdings[symbol]['avg_price'] = (
                            (st.session_state.portfolio_holdings[symbol]['avg_price'] * 
                             (st.session_state.portfolio_holdings[symbol]['shares'] - shares) + 
                             current_price * shares) / st.session_state.portfolio_holdings[symbol]['shares']
                        )
                    else:
                        st.session_state.portfolio_holdings[symbol] = {
                            'shares': shares,
                            'avg_price': current_price
                        }
                    
                    st.session_state.portfolio_balance -= investment_amount
                    st.success(f"Bought {shares:.4f} shares of {symbol} at ${current_price:.2f}")
                    st.rerun()
                else:
                    st.error("Insufficient balance!")
        
        with col_sell:
            if symbol in st.session_state.portfolio_holdings and st.session_state.portfolio_holdings[symbol]['shares'] > 0:
                if st.button(f"🔴 SELL {symbol}", type="secondary"):
                    shares_to_sell = min(
                        investment_amount / current_price,
                        st.session_state.portfolio_holdings[symbol]['shares']
                    )
                    
                    proceeds = shares_to_sell * current_price
                    st.session_state.portfolio_balance += proceeds
                    st.session_state.portfolio_holdings[symbol]['shares'] -= shares_to_sell
                    
                    profit_loss = (current_price - st.session_state.portfolio_holdings[symbol]['avg_price']) * shares_to_sell
                    
                    if st.session_state.portfolio_holdings[symbol]['shares'] <= 0:
                        del st.session_state.portfolio_holdings[symbol]
                    
                    st.success(f"Sold {shares_to_sell:.4f} shares of {symbol} at ${current_price:.2f}")
                    if profit_loss > 0:
                        st.success(f"Profit: ${profit_loss:.2f}")
                    else:
                        st.error(f"Loss: ${abs(profit_loss):.2f}")
                    st.rerun()
    
    st.markdown("---")
    
    # Real-time update indicator
    last_updated = data.get('last_updated', datetime.now())
    st.info(f"🕐 Last Updated: {last_updated.strftime('%Y-%m-%d %H:%M:%S')} | Next update in real-time mode")
    
    # Header with basic info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current Price",
            value=f"${stock_info.get('currentPrice', 0):.2f}",
            delta=f"{stock_info.get('regularMarketChangePercent', 0):.2f}%"
        )
    
    with col2:
        st.metric(
            label="Market Cap",
            value=format_large_number(stock_info.get('marketCap', 0))
        )
    
    with col3:
        st.metric(
            label="P/E Ratio",
            value=f"{stock_info.get('trailingPE', 'N/A')}"
        )
    
    with col4:
        st.metric(
            label="52W High/Low",
            value=f"${stock_info.get('fiftyTwoWeekHigh', 0):.2f}",
            delta=f"Low: ${stock_info.get('fiftyTwoWeekLow', 0):.2f}"
        )
    
    # Charts section
    st.subheader(f"📊 {symbol} Price Chart")
    
    chart_generator = ChartGenerator()
    
    if chart_type == "Candlestick":
        fig = chart_generator.create_candlestick_chart(historical_data, symbol, trading_signal)
    elif chart_type == "Line":
        fig = chart_generator.create_line_chart(historical_data, symbol, trading_signal)
    elif chart_type == "OHLC":
        fig = chart_generator.create_ohlc_chart(historical_data, symbol)
    elif chart_type == "Bollinger Bands":
        fig = chart_generator.create_bollinger_bands_chart(historical_data, symbol)
    else:  # MACD Analysis
        fig = chart_generator.create_macd_chart(historical_data, symbol)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data tables section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Historical Data")
        
        # Prepare data for display
        display_data = historical_data.copy()
        display_data = display_data.round(2)
        display_data.index = display_data.index.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_data,
            use_container_width=True,
            height=400
        )
        
        # CSV download
        csv_buffer = io.StringIO()
        display_data.to_csv(csv_buffer)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Historical Data (CSV)",
            data=csv_data,
            file_name=f"{symbol}_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.subheader("💼 Company Information")
        
        # Company info table
        info_data = {
            "Company Name": stock_info.get('longName', 'N/A'),
            "Sector": stock_info.get('sector', 'N/A'),
            "Industry": stock_info.get('industry', 'N/A'),
            "Country": stock_info.get('country', 'N/A'),
            "Website": stock_info.get('website', 'N/A'),
            "Full Time Employees": format_large_number(stock_info.get('fullTimeEmployees', 0)),
            "Market Cap": format_large_number(stock_info.get('marketCap', 0)),
            "Enterprise Value": format_large_number(stock_info.get('enterpriseValue', 0)),
            "Revenue": format_large_number(stock_info.get('totalRevenue', 0)),
            "Profit Margin": f"{stock_info.get('profitMargins', 0)*100:.2f}%" if stock_info.get('profitMargins') else 'N/A',
            "Beta": f"{stock_info.get('beta', 'N/A')}",
            "Dividend Yield": f"{stock_info.get('dividendYield', 0)*100:.2f}%" if stock_info.get('dividendYield') else 'N/A'
        }
        
        info_df = pd.DataFrame(list(info_data.items()), columns=['Metric', 'Value'])
        st.dataframe(info_df, use_container_width=True, height=400)
        
        # Company info CSV download
        csv_buffer_info = io.StringIO()
        info_df.to_csv(csv_buffer_info, index=False)
        csv_info_data = csv_buffer_info.getvalue()
        
        st.download_button(
            label="📥 Download Company Info (CSV)",
            data=csv_info_data,
            file_name=f"{symbol}_company_info_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Technical indicators section
    st.subheader("📈 Technical Analysis")
    
    # Technical indicators chart (data already has indicators calculated)
    tech_fig = chart_generator.create_technical_chart(historical_data, symbol)
    st.plotly_chart(tech_fig, use_container_width=True)
    
    # Additional technical metrics
    col1, col2, col3, col4 = st.columns(4)
    
    latest_data = historical_data.iloc[-1]
    
    with col1:
        if 'MACD' in historical_data.columns:
            st.metric(
                label="MACD",
                value=f"{latest_data['MACD']:.3f}",
                delta=f"Signal: {latest_data['MACD_Signal']:.3f}",
                help="MACD above signal line = bullish momentum"
            )
    
    with col2:
        if 'BB_Upper' in historical_data.columns:
            bb_position = ((latest_data['Close'] - latest_data['BB_Lower']) / 
                          (latest_data['BB_Upper'] - latest_data['BB_Lower'])) * 100
            st.metric(
                label="Bollinger Band %",
                value=f"{bb_position:.1f}%",
                help="Position within Bollinger Bands (0-100%)"
            )
    
    with col3:
        if 'Volume_Ratio' in historical_data.columns:
            st.metric(
                label="Volume Ratio",
                value=f"{latest_data['Volume_Ratio']:.2f}",
                help="Current volume vs 20-day average"
            )
    
    with col4:
        if 'SMA_20' in historical_data.columns:
            price_vs_sma = ((latest_data['Close'] - latest_data['SMA_20']) / latest_data['SMA_20']) * 100
            st.metric(
                label="Price vs SMA20",
                value=f"{price_vs_sma:.2f}%",
                help="Price position relative to 20-day moving average"
            )
    
    # Portfolio Display Section
    if 'portfolio_holdings' in st.session_state and st.session_state.portfolio_holdings:
        st.subheader("📊 Portfolio Holdings")
        
        portfolio_data = []
        total_portfolio_value = st.session_state.portfolio_balance
        
        for symbol, holding in st.session_state.portfolio_holdings.items():
            if holding['shares'] > 0:
                # Get current price (simplified - using last known price)
                current_price = stock_info.get('currentPrice', holding['avg_price']) if data['symbol'] == symbol else holding['avg_price']
                current_value = holding['shares'] * current_price
                profit_loss = (current_price - holding['avg_price']) * holding['shares']
                profit_loss_pct = ((current_price - holding['avg_price']) / holding['avg_price']) * 100
                
                portfolio_data.append({
                    'Symbol': symbol,
                    'Shares': f"{holding['shares']:.4f}",
                    'Avg Price': f"${holding['avg_price']:.2f}",
                    'Current Price': f"${current_price:.2f}",
                    'Current Value': f"${current_value:.2f}",
                    'P&L': f"${profit_loss:.2f}",
                    'P&L %': f"{profit_loss_pct:.2f}%"
                })
                
                total_portfolio_value += current_value
        
        if portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            st.dataframe(portfolio_df, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cash Balance", f"${st.session_state.portfolio_balance:.2f}")
            with col2:
                st.metric("Total Portfolio Value", f"${total_portfolio_value:.2f}")
            with col3:
                total_return = total_portfolio_value - 1000.0  # Starting amount was $1000
                st.metric("Total Return", f"${total_return:.2f}", f"{(total_return/1000.0)*100:.2f}%")
    

    # Enhanced Backtesting Results Section
    if data.get('backtest_results') and not data['backtest_results'].get('error'):
        st.markdown("---")
        
        # Professional backtesting header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 16px; padding: 2rem; margin: 1rem 0; border: 1px solid #475569; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
            <h2 style="color: #00FF88; margin: 0; display: flex; align-items: center;">
                🤖 ML-Enhanced Backtesting Results
                <span style="margin-left: auto; font-size: 0.8rem; color: #94a3b8;">Advanced Strategy Analysis</span>
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        backtest = data['backtest_results']
        metrics = backtest.get('performance_metrics', {})
        
        # Strategy rating display
        if 'detailed_analysis' in backtest and 'strategy_rating' in backtest['detailed_analysis']:
            rating = backtest['detailed_analysis']['strategy_rating']
            st.markdown(
                f"""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {rating['color']}20 0%, {rating['color']}10 100%); border-radius: 16px; margin: 1rem 0; border: 1px solid {rating['color']}40;">
                    <h1 style="color: {rating['color']}; margin: 0; font-size: 3rem;">{rating['score']}/100</h1>
                    <h3 style="color: {rating['color']}; margin: 0.5rem 0;">{rating['rating']} Strategy</h3>
                    <p style="color: #94a3b8; margin: 0;">Performance Score: {rating['percentage']:.1f}%</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Key performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            return_color = "#00FF88" if backtest.get('total_return_pct', 0) > 0 else "#FF4444"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; background: linear-gradient(135deg, {return_color}20 0%, {return_color}10 100%);">
                    <h3 style="color: {return_color}; margin: 0; font-size: 2.5rem;">{backtest.get('total_return_pct', 0):.2f}%{help_system.show_tooltip('total_return')}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc; font-weight: 600;">Total Return</p>
                    <small style="color: #94a3b8;">vs {backtest.get('initial_capital', 10000):,.0f} initial</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('total_return')
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: #22c55e; margin: 0; font-size: 2rem;">{metrics.get('annualized_return_pct', 0):.2f}%{help_system.show_tooltip('annualized_return')}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc; font-weight: 600;">Annualized Return</p>
                    <small style="color: #94a3b8;">Expected yearly performance</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('annualized_return')
        
        with col3:
            sharpe_color = "#00FF88" if metrics.get('sharpe_ratio', 0) > 1 else "#FFD700" if metrics.get('sharpe_ratio', 0) > 0.5 else "#FF4444"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: {sharpe_color}; margin: 0; font-size: 2rem;">{metrics.get('sharpe_ratio', 0):.2f}{help_system.show_tooltip('sharpe_ratio')}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc; font-weight: 600;">Sharpe Ratio</p>
                    <small style="color: #94a3b8;">Risk-adjusted returns</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('sharpe_ratio')
        
        with col4:
            drawdown_color = "#00FF88" if metrics.get('max_drawdown_pct', 0) < 10 else "#FFD700" if metrics.get('max_drawdown_pct', 0) < 20 else "#FF4444"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h3 style="color: {drawdown_color}; margin: 0; font-size: 2rem;">{metrics.get('max_drawdown_pct', 0):.2f}%{help_system.show_tooltip('max_drawdown')}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc; font-weight: 600;">Max Drawdown</p>
                    <small style="color: #94a3b8;">Largest decline</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('max_drawdown')
        
        # Advanced metrics row
        st.markdown("### 📊 Advanced Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            win_rate_color = "#00FF88" if metrics.get('win_rate_pct', 0) > 60 else "#FFD700" if metrics.get('win_rate_pct', 0) > 50 else "#FF4444"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h4 style="color: {win_rate_color}; margin: 0;">{metrics.get('win_rate_pct', 0):.1f}%{help_system.show_tooltip('win_rate')}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc;">Win Rate</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('win_rate')
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h4 style="color: #00D97F; margin: 0;">{metrics.get('profit_factor', 0):.2f}{help_system.show_tooltip('profit_factor')}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc;">Profit Factor</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('profit_factor')
        
        with col3:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h4 style="color: #22c55e; margin: 0;">{metrics.get('total_trades', 0)}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc;">Total Trades</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            adaptations = len(backtest.get('adaptation_events', []))
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center;">
                    <h4 style="color: #00FF88; margin: 0;">{adaptations}{help_system.show_tooltip('ml_adaptations')}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #f8fafc;">ML Adaptations</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            help_system.show_detailed_help('ml_adaptations')
        
        # Detailed analysis
        if 'detailed_analysis' in backtest:
            analysis = backtest['detailed_analysis']
            
            # Insights and recommendations
            col1, col2 = st.columns(2)
            
            with col1:
                if analysis.get('strengths'):
                    st.markdown("#### ✅ Strategy Strengths")
                    for strength in analysis['strengths']:
                        st.success(f"✓ {strength}")
            
            with col2:
                if analysis.get('recommendations'):
                    st.markdown("#### 💡 Optimization Recommendations")
                    for rec in analysis['recommendations']:
                        st.info(f"→ {rec}")
        
        # ML Adaptation timeline
        if backtest.get('adaptation_events'):
            st.markdown("#### 🤖 Machine Learning Adaptations")
            
            adaptation_df = pd.DataFrame([
                {
                    'Day': event.get('day', 0),
                    'Event': event.get('event', 'Unknown'),
                    'Details': len(event.get('adaptations', [])) if event.get('adaptations') else 'Initial Training'
                }
                for event in backtest['adaptation_events']
            ])
            
            if not adaptation_df.empty:
                st.dataframe(adaptation_df, use_container_width=True)
                
                # Educational insights about ML performance
                st.markdown("#### 🎓 Educational Insights")
                insights = help_system.get_educational_insights(backtest)
                for insight in insights:
                    st.info(insight)
            
            # Real-time learning status
            st.markdown("#### 🧠 Continuous Learning Status")
            learning_status = "AI continuously adapts trading strategies based on real-time market performance"
            st.success(f"✅ {learning_status}")
            
            if len(backtest.get('adaptation_events', [])) > 0:
                last_adaptation = backtest['adaptation_events'][-1]
                st.info(f"🔄 Last adaptation: Day {last_adaptation.get('day', 0)} - {last_adaptation.get('event', 'Unknown')}")
        
        # Portfolio performance visualization
        if 'charts' in backtest and backtest['charts']:
            st.markdown("#### 📈 Portfolio Performance Visualization")
            try:
                import json
                portfolio_chart_data = json.loads(backtest['charts']['portfolio_chart'])
                st.plotly_chart(portfolio_chart_data, use_container_width=True)
            except Exception as e:
                st.warning(f"Chart visualization will be available after completing backtesting analysis")
    
    elif data.get('backtest_results') and data['backtest_results'].get('error'):
        st.warning(f"Backtesting Error: {data['backtest_results']['error']}")
        
        # Simple trading statistics fallback
        st.subheader("📈 Trading Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        if data.get('backtest_results'):
            backtest = data['backtest_results']
            
            with col1:
                st.metric("Total Trades", backtest.get('total_trades', 0))
            
            with col2:
                win_rate = backtest.get('win_rate', 0)
                win_rate_color = "green" if win_rate > 50 else "red"
                st.markdown(
                    f"<div style='text-align: center; padding: 10px; background-color: {win_rate_color}20; border-radius: 5px;'>"
                    f"<strong style='color: {win_rate_color};'>{win_rate:.1f}%</strong><br>"
                    f"<small>Win Rate</small>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            
            with col3:
                st.metric("Avg Win", f"${backtest.get('avg_win', 0):.2f}")
            
            with col4:
                st.metric("Avg Loss", f"${backtest.get('avg_loss', 0):.2f}")
        
        # Simple performance chart
        if data.get('backtest_results', {}).get('daily_values') and len(data['backtest_results']['daily_values']) > 0:
            st.subheader("📊 Portfolio Value Over Time")
            
            backtest = data['backtest_results']
            portfolio_df = pd.DataFrame({
                'Date': pd.to_datetime(backtest['dates']) if backtest.get('dates') else [],
                'Portfolio Value': backtest['daily_values']
            })
            
            if not portfolio_df.empty:
                import plotly.graph_objects as go
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=portfolio_df['Date'],
                    y=portfolio_df['Portfolio Value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#00FF88', width=2)
                ))
                
                # Add buy/sell signals to the chart
                if backtest['buy_signals']:
                    buy_dates = [signal['date'] for signal in backtest['buy_signals']]
                    buy_values = [signal['price'] * (backtest['initial_capital'] / backtest['buy_signals'][0]['price']) for signal in backtest['buy_signals']]
                    
                    fig.add_trace(go.Scatter(
                        x=buy_dates,
                        y=buy_values,
                        mode='markers',
                        name='Buy Signals',
                        marker=dict(color='green', size=10, symbol='triangle-up')
                    ))
                
                if backtest['sell_signals']:
                    sell_dates = [signal['date'] for signal in backtest['sell_signals']]
                    sell_values = [signal['price'] * (backtest['initial_capital'] / backtest['sell_signals'][0]['price']) for signal in backtest['sell_signals']]
                    
                    fig.add_trace(go.Scatter(
                        x=sell_dates,
                        y=sell_values,
                        mode='markers',
                        name='Sell Signals',
                        marker=dict(color='red', size=10, symbol='triangle-down')
                    ))
                
                fig.update_layout(
                    title="Backtesting Results: Portfolio Performance",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value ($)",
                    plot_bgcolor='#0E1117',
                    paper_bgcolor='#262730',
                    font=dict(color='#FAFAFA'),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Strategy assessment
        st.subheader("🎯 Strategy Assessment")
        
        # Calculate strategy rating
        score = 0
        if backtest['total_return_pct'] > 10: score += 2
        elif backtest['total_return_pct'] > 0: score += 1
        
        if backtest['sharpe_ratio'] > 1.5: score += 2
        elif backtest['sharpe_ratio'] > 1: score += 1
        
        if backtest['win_rate'] > 60: score += 2
        elif backtest['win_rate'] > 50: score += 1
        
        if backtest['max_drawdown_pct'] < 10: score += 2
        elif backtest['max_drawdown_pct'] < 20: score += 1
        
        if score >= 7:
            rating = "🟢 Excellent Strategy"
            rating_color = "green"
            recommendation = "Strong buy signal strategy with good risk management"
        elif score >= 5:
            rating = "🟡 Good Strategy"
            rating_color = "orange"
            recommendation = "Decent strategy but monitor risk levels"
        elif score >= 3:
            rating = "🟠 Average Strategy"
            rating_color = "orange"
            recommendation = "Strategy shows potential but needs improvement"
        else:
            rating = "🔴 Poor Strategy"
            rating_color = "red"
            recommendation = "Strategy underperforms - consider adjustments"
        
        st.markdown(
            f"<div style='padding: 20px; background-color: {rating_color}20; border-left: 5px solid {rating_color}; border-radius: 10px;'>"
            f"<h3 style='color: {rating_color}; margin: 0;'>{rating}</h3>"
            f"<p style='margin: 10px 0 0 0; color: #FAFAFA;'>{recommendation}</p>"
            f"<small style='color: #CCCCCC;'>Strategy Score: {score}/8</small>"
            f"</div>", 
            unsafe_allow_html=True
        )

def format_large_number(num):
    """Format large numbers with appropriate suffixes"""
    if not num or num == 0:
        return "N/A"
    
    num = float(num)
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

if __name__ == "__main__":
    main()

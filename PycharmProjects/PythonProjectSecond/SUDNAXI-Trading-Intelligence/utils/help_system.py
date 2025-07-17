"""
Comprehensive Help System with Tooltips and Educational Content
"""
import streamlit as st

class HelpSystem:
    """Professional help system with tooltips and educational content"""
    
    def __init__(self):
        self.tooltips = {
            # Trading Metrics
            'total_return': {
                'title': 'Total Return',
                'description': 'The overall percentage gain or loss on your investment from start to finish.',
                'example': 'If you invested $10,000 and now have $12,000, your total return is 20%.',
                'good_range': 'Positive returns are good. 10%+ annually is excellent.',
                'icon': '📈'
            },
            'annualized_return': {
                'title': 'Annualized Return',
                'description': 'The average yearly return if the strategy performed consistently over time.',
                'example': 'A 25% total return over 2 years equals ~11.8% annualized return.',
                'good_range': '8-12% is typical for good strategies. 15%+ is exceptional.',
                'icon': '📊'
            },
            'sharpe_ratio': {
                'title': 'Sharpe Ratio',
                'description': 'Measures how much extra return you get for the extra risk you take.',
                'example': 'Higher is better. It shows if returns justify the volatility.',
                'good_range': '>1.0 is good, >1.5 is very good, >2.0 is excellent.',
                'icon': '⚖️'
            },
            'max_drawdown': {
                'title': 'Maximum Drawdown',
                'description': 'The largest peak-to-trough decline in portfolio value.',
                'example': 'If your portfolio went from $10,000 to $8,000, drawdown is 20%.',
                'good_range': '<10% is excellent, <20% is good, >30% is concerning.',
                'icon': '📉'
            },
            'win_rate': {
                'title': 'Win Rate',
                'description': 'Percentage of trades that were profitable.',
                'example': 'If 6 out of 10 trades made money, win rate is 60%.',
                'good_range': '>50% is good, >60% is very good, >70% is exceptional.',
                'icon': '🎯'
            },
            'profit_factor': {
                'title': 'Profit Factor',
                'description': 'Total profits divided by total losses.',
                'example': 'If you made $3,000 profit and lost $1,500, profit factor is 2.0.',
                'good_range': '>1.0 means profitable, >1.5 is good, >2.0 is excellent.',
                'icon': '💰'
            },
            
            # Technical Indicators
            'rsi': {
                'title': 'RSI (Relative Strength Index)',
                'description': 'Measures if a stock is overbought (too expensive) or oversold (potentially undervalued).',
                'example': 'RSI above 70 suggests overbought, below 30 suggests oversold.',
                'good_range': 'Look for buy signals near 30, sell signals near 70.',
                'icon': '📡'
            },
            'macd': {
                'title': 'MACD (Moving Average Convergence Divergence)',
                'description': 'Shows the relationship between two moving averages to identify trend changes.',
                'example': 'When MACD line crosses above signal line, it may indicate upward momentum.',
                'good_range': 'Crossovers and divergences provide trading signals.',
                'icon': '〰️'
            },
            'bollinger_bands': {
                'title': 'Bollinger Bands',
                'description': 'Price channels that expand and contract based on market volatility.',
                'example': 'When price touches upper band, stock may be overbought.',
                'good_range': 'Price bouncing between bands shows normal trading range.',
                'icon': '📏'
            },
            'volume': {
                'title': 'Trading Volume',
                'description': 'Number of shares traded in a given period.',
                'example': 'High volume during price moves confirms the trend strength.',
                'good_range': 'Higher volume validates price movements.',
                'icon': '📊'
            },
            
            # ML Concepts
            'ml_adaptations': {
                'title': 'ML Adaptations',
                'description': 'Number of times the AI adjusted its strategy based on market performance.',
                'example': 'More adaptations show the AI is actively learning and improving.',
                'good_range': 'Regular adaptations (5-10 per year) show active learning.',
                'icon': '🤖'
            },
            'strategy_rating': {
                'title': 'Strategy Performance Rating',
                'description': 'AI-generated score from 0-100 based on multiple performance factors.',
                'example': 'Combines returns, risk, consistency, and other factors into one score.',
                'good_range': '70+ is good, 80+ is very good, 90+ is exceptional.',
                'icon': '⭐'
            },
            'confidence_score': {
                'title': 'AI Confidence Score',
                'description': 'How confident the AI is in its trading signal or prediction.',
                'example': 'Higher confidence means the AI has stronger conviction in its decision.',
                'good_range': '>70% confidence suggests reliable signals.',
                'icon': '🎯'
            },
            
            # Market Data
            'market_cap': {
                'title': 'Market Capitalization',
                'description': 'Total value of all company shares (Price × Total Shares).',
                'example': 'Apple with 16B shares at $150 each = $2.4T market cap.',
                'good_range': 'Large cap (>$10B), Mid cap ($2-10B), Small cap (<$2B).',
                'icon': '🏢'
            },
            'pe_ratio': {
                'title': 'Price-to-Earnings Ratio',
                'description': 'How much investors pay for each dollar of company earnings.',
                'example': 'PE of 20 means you pay $20 for every $1 of annual earnings.',
                'good_range': '15-25 is typical, <15 may be undervalued, >25 may be overvalued.',
                'icon': '💡'
            },
            'dividend_yield': {
                'title': 'Dividend Yield',
                'description': 'Annual dividend payment as percentage of stock price.',
                'example': '$4 annual dividend on $100 stock = 4% dividend yield.',
                'good_range': '2-4% is typical for dividend stocks, >5% may indicate risk.',
                'icon': '💵'
            },
            
            # Risk Management
            'position_size': {
                'title': 'Position Size',
                'description': 'How much of your portfolio is invested in a single stock.',
                'example': '$2,000 in Apple out of $10,000 portfolio = 20% position size.',
                'good_range': 'Usually 5-10% per stock to diversify risk.',
                'icon': '⚖️'
            },
            'stop_loss': {
                'title': 'Stop Loss',
                'description': 'Automatic sell order triggered when price falls to limit losses.',
                'example': 'Buy at $100, set stop loss at $90 to limit loss to 10%.',
                'good_range': '5-10% below entry price for most strategies.',
                'icon': '🛡️'
            },
            'volatility': {
                'title': 'Volatility',
                'description': 'How much the stock price fluctuates up and down.',
                'example': 'High volatility means large price swings, low volatility means stable.',
                'good_range': 'Lower volatility generally means lower risk.',
                'icon': '📈'
            }
        }
    
    def show_tooltip(self, key: str, position: str = "top") -> str:
        """Generate tooltip HTML for a given concept"""
        if key not in self.tooltips:
            return ""
        
        tooltip = self.tooltips[key]
        
        tooltip_html = f"""
        <div style="position: relative; display: inline-block;">
            <span style="
                background: linear-gradient(135deg, #00FF88, #00D97F);
                color: #000;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                cursor: help;
                margin-left: 5px;
            " title="Click for detailed explanation">?</span>
        </div>
        """
        
        return tooltip_html
    
    def show_detailed_help(self, key: str):
        """Show detailed help in expandable section"""
        if key not in self.tooltips:
            return
        
        tooltip = self.tooltips[key]
        
        with st.expander(f"{tooltip['icon']} {tooltip['title']} - Detailed Help"):
            st.markdown(f"**What it is:** {tooltip['description']}")
            st.markdown(f"**Example:** {tooltip['example']}")
            st.markdown(f"**Good Range:** {tooltip['good_range']}")
    
    def show_concept_help(self, concept: str):
        """Show help for a specific concept"""
        if concept in self.tooltips:
            tooltip = self.tooltips[concept]
            st.info(f"""
            **{tooltip['icon']} {tooltip['title']}**
            
            {tooltip['description']}
            
            **Example:** {tooltip['example']}
            
            **What to look for:** {tooltip['good_range']}
            """)
    
    def add_help_sidebar(self):
        """Add comprehensive help section to sidebar"""
        with st.sidebar:
            st.markdown("### 📚 Help & Education")
            
            help_category = st.selectbox(
                "Choose help topic:",
                ["Trading Metrics", "Technical Indicators", "AI/ML Concepts", "Market Data", "Risk Management"]
            )
            
            if help_category == "Trading Metrics":
                concepts = ['total_return', 'annualized_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'profit_factor']
            elif help_category == "Technical Indicators":
                concepts = ['rsi', 'macd', 'bollinger_bands', 'volume']
            elif help_category == "AI/ML Concepts":
                concepts = ['ml_adaptations', 'strategy_rating', 'confidence_score']
            elif help_category == "Market Data":
                concepts = ['market_cap', 'pe_ratio', 'dividend_yield']
            else:  # Risk Management
                concepts = ['position_size', 'stop_loss', 'volatility']
            
            selected_concept = st.selectbox("Select concept:", concepts)
            
            if selected_concept:
                self.show_concept_help(selected_concept)
    
    def get_educational_insights(self, backtest_results: dict) -> list:
        """Generate educational insights based on results"""
        insights = []
        
        if not backtest_results or backtest_results.get('error'):
            return ["Enable backtesting to get personalized educational insights about your strategy performance."]
        
        metrics = backtest_results.get('performance_metrics', {})
        
        # Total Return Education
        total_return = metrics.get('total_return_pct', 0)
        if total_return > 15:
            insights.append("🎉 Excellent total return! Your strategy significantly outperformed typical market returns.")
        elif total_return > 5:
            insights.append("✅ Good positive returns. Your strategy is profitable and beating savings accounts.")
        elif total_return > 0:
            insights.append("💡 Modest gains. Consider optimizing signal sensitivity or risk management.")
        else:
            insights.append("⚠️ Negative returns suggest strategy needs refinement. Try different parameters or timeframes.")
        
        # Sharpe Ratio Education
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 1.5:
            insights.append("⭐ Outstanding risk-adjusted returns! Your strategy efficiently manages risk vs reward.")
        elif sharpe > 1.0:
            insights.append("👍 Good risk management. Returns justify the volatility you're taking.")
        elif sharpe > 0.5:
            insights.append("📈 Moderate efficiency. Consider reducing position sizes or improving entry timing.")
        else:
            insights.append("🔍 Poor risk-adjusted returns. Focus on reducing losses or improving win rate.")
        
        # Win Rate Education
        win_rate = metrics.get('win_rate_pct', 0)
        if win_rate > 60:
            insights.append("🎯 High accuracy strategy! Most of your trades are profitable.")
        elif win_rate > 50:
            insights.append("✓ Above-average accuracy. You're picking more winners than losers.")
        elif win_rate > 40:
            insights.append("⚖️ Moderate accuracy. Focus on cutting losses quickly and letting winners run.")
        else:
            insights.append("🔧 Low accuracy suggests signals need improvement. Consider additional filters.")
        
        # ML Adaptations Education
        adaptations = len(backtest_results.get('adaptation_events', []))
        if adaptations > 5:
            insights.append("🤖 Active AI learning! Your strategy is continuously adapting to market changes.")
        elif adaptations > 2:
            insights.append("🧠 Moderate AI adaptation. The system is learning from market feedback.")
        else:
            insights.append("📚 Limited adaptations. Consider enabling more aggressive ML learning parameters.")
        
        return insights

# Global help system instance
help_system = HelpSystem()
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

class ChartGenerator:
    """Generates interactive charts for stock data visualization"""
    
    def __init__(self):
        # Dark theme color scheme
        self.colors = {
            'background': '#0E1117',
            'paper': '#262730',
            'text': '#FAFAFA',
            'grid': '#2E3440',
            'up': '#00FF88',
            'down': '#FF4444',
            'volume': '#888888',
            'sma20': '#FFD700',
            'sma50': '#FF6B6B',
            'rsi': '#00BFFF'
        }
    
    def _get_base_layout(self, title: str) -> dict:
        """Get base layout configuration for all charts"""
        return {
            'title': {
                'text': title,
                'x': 0.5,
                'font': {'size': 20, 'color': self.colors['text']}
            },
            'plot_bgcolor': self.colors['background'],
            'paper_bgcolor': self.colors['paper'],
            'font': {'color': self.colors['text']},
            'xaxis': {
                'gridcolor': self.colors['grid'],
                'showgrid': True,
                'zeroline': False
            },
            'yaxis': {
                'gridcolor': self.colors['grid'],
                'showgrid': True,
                'zeroline': False
            },
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': self.colors['text']}
            }
        }
    
    def create_candlestick_chart(self, data: pd.DataFrame, symbol: str, trading_signal: dict = None) -> go.Figure:
        """
        Create an interactive candlestick chart
        
        Args:
            data: Historical stock data
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol,
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down']
            ),
            row=1, col=1
        )
        
        # Volume bars
        colors = [self.colors['up'] if close >= open else self.colors['down'] 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Stock Price - Candlestick Chart')
        layout.update({
            'xaxis2': {'gridcolor': self.colors['grid']},
            'yaxis2': {'gridcolor': self.colors['grid']},
            'height': 700
        })
        
        # Add trading signal annotations
        if trading_signal and 'signal' in trading_signal:
            signal_color = '#00FF88' if 'BUY' in trading_signal['signal'] else '#FF4444' if 'SELL' in trading_signal['signal'] else '#FFD700'
            
            fig.add_annotation(
                x=data.index[-1],
                y=data['High'].iloc[-1],
                text=f"📊 {trading_signal['signal']}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=signal_color,
                bgcolor=signal_color,
                bordercolor=signal_color,
                font=dict(color='white', size=12),
                xref="x",
                yref="y"
            )
        
        fig.update_layout(layout)
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig
    
    def create_line_chart(self, data: pd.DataFrame, symbol: str, trading_signal: dict = None) -> go.Figure:
        """
        Create an interactive line chart
        
        Args:
            data: Historical stock data
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Close price line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color=self.colors['up'], width=2),
                hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Price</b>: $%{y:.2f}<br>' +
                             '<extra></extra>'
            )
        )
        
        # Add trading signal annotations for line chart
        if trading_signal and 'signal' in trading_signal:
            signal_color = '#00FF88' if 'BUY' in trading_signal['signal'] else '#FF4444' if 'SELL' in trading_signal['signal'] else '#FFD700'
            
            fig.add_annotation(
                x=data.index[-1],
                y=data['Close'].iloc[-1],
                text=f"📊 {trading_signal['signal']}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=signal_color,
                bgcolor=signal_color,
                bordercolor=signal_color,
                font=dict(color='white', size=12),
                xref="x",
                yref="y"
            )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Stock Price - Line Chart')
        layout.update({
            'yaxis': {
                'title': 'Price ($)',
                'gridcolor': self.colors['grid']
            },
            'xaxis': {
                'title': 'Date',
                'gridcolor': self.colors['grid']
            },
            'height': 500
        })
        
        fig.update_layout(layout)
        
        return fig
    
    def create_ohlc_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create an interactive OHLC chart
        
        Args:
            data: Historical stock data
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # OHLC chart
        fig.add_trace(
            go.Ohlc(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol,
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down']
            )
        )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Stock Price - OHLC Chart')
        layout.update({
            'yaxis': {
                'title': 'Price ($)',
                'gridcolor': self.colors['grid']
            },
            'xaxis': {
                'title': 'Date',
                'gridcolor': self.colors['grid']
            },
            'height': 500
        })
        
        fig.update_layout(layout)
        
        return fig
    
    def create_technical_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create a technical analysis chart with moving averages and RSI
        
        Args:
            data: Historical stock data with technical indicators
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price with Moving Averages', 'RSI'),
            row_heights=[0.7, 0.3]
        )
        
        # Price line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color=self.colors['text'], width=2)
            ),
            row=1, col=1
        )
        
        # Moving averages
        if 'SMA_20' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color=self.colors['sma20'], width=1)
                ),
                row=1, col=1
            )
        
        if 'SMA_50' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color=self.colors['sma50'], width=1)
                ),
                row=1, col=1
            )
        
        # RSI
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.colors['rsi'], width=2)
                ),
                row=2, col=1
            )
            
            # RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Technical Analysis')
        layout.update({
            'height': 700,
            'yaxis': {'title': 'Price ($)', 'gridcolor': self.colors['grid']},
            'yaxis2': {'title': 'RSI', 'range': [0, 100], 'gridcolor': self.colors['grid']},
            'xaxis2': {'title': 'Date', 'gridcolor': self.colors['grid']}
        })
        
        fig.update_layout(layout)
        
        return fig
    
    def create_volume_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create a volume analysis chart
        
        Args:
            data: Historical stock data
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Volume bars with color coding
        colors = [self.colors['up'] if close >= open else self.colors['down'] 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.8,
                hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Volume</b>: %{y:,.0f}<br>' +
                             '<extra></extra>'
            )
        )
        
        # Volume moving average
        volume_ma = data['Volume'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=volume_ma,
                mode='lines',
                name='Volume MA (20)',
                line=dict(color='orange', width=2)
            )
        )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Volume Analysis')
        layout.update({
            'yaxis': {
                'title': 'Volume',
                'gridcolor': self.colors['grid']
            },
            'xaxis': {
                'title': 'Date',
                'gridcolor': self.colors['grid']
            },
            'height': 400
        })
        
        fig.update_layout(layout)
        
        return fig
    
    def create_bollinger_bands_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create a Bollinger Bands chart
        
        Args:
            data: Historical stock data with Bollinger Bands
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Bollinger Bands
        if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns:
            # Upper band
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_Upper'],
                    mode='lines',
                    name='Upper Band',
                    line=dict(color='red', width=1),
                    fill=None
                )
            )
            
            # Lower band
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_Lower'],
                    mode='lines',
                    name='Lower Band',
                    line=dict(color='red', width=1),
                    fill='tonexty',
                    fillcolor='rgba(255, 0, 0, 0.1)'
                )
            )
            
            # Middle band (SMA)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_Middle'],
                    mode='lines',
                    name='Middle Band (SMA)',
                    line=dict(color='blue', width=1)
                )
            )
        
        # Price line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color=self.colors['up'], width=2)
            )
        )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} Bollinger Bands Analysis')
        layout.update({
            'yaxis': {
                'title': 'Price ($)',
                'gridcolor': self.colors['grid']
            },
            'xaxis': {
                'title': 'Date',
                'gridcolor': self.colors['grid']
            },
            'height': 500
        })
        
        fig.update_layout(layout)
        
        return fig
    
    def create_macd_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create a MACD analysis chart
        
        Args:
            data: Historical stock data with MACD indicators
            symbol: Stock symbol for title
            
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price with EMAs', 'MACD'),
            row_heights=[0.7, 0.3]
        )
        
        # Price line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color=self.colors['text'], width=2)
            ),
            row=1, col=1
        )
        
        # EMAs
        if 'EMA_12' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['EMA_12'],
                    mode='lines',
                    name='EMA 12',
                    line=dict(color=self.colors['sma20'], width=1)
                ),
                row=1, col=1
            )
        
        if 'EMA_26' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['EMA_26'],
                    mode='lines',
                    name='EMA 26',
                    line=dict(color=self.colors['sma50'], width=1)
                ),
                row=1, col=1
            )
        
        # MACD line
        if 'MACD' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color=self.colors['rsi'], width=2)
                ),
                row=2, col=1
            )
        
        # Signal line
        if 'MACD_Signal' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD_Signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='orange', width=1)
                ),
                row=2, col=1
            )
        
        # MACD Histogram
        if 'MACD_Histogram' in data.columns:
            colors = [self.colors['up'] if val >= 0 else self.colors['down'] 
                     for val in data['MACD_Histogram']]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['MACD_Histogram'],
                    name='Histogram',
                    marker_color=colors,
                    opacity=0.6
                ),
                row=2, col=1
            )
        
        # Update layout
        layout = self._get_base_layout(f'{symbol} MACD Analysis')
        layout.update({
            'height': 700,
            'yaxis': {'title': 'Price ($)', 'gridcolor': self.colors['grid']},
            'yaxis2': {'title': 'MACD', 'gridcolor': self.colors['grid']},
            'xaxis2': {'title': 'Date', 'gridcolor': self.colors['grid']}
        })
        
        fig.update_layout(layout)
        
        return fig

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any

class StockDataFetcher:
    """Handles fetching stock data from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive stock information
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary containing stock information or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Validate that we got actual data
            if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
                return None
                
            return info
            
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with historical data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=period)
            
            if hist_data.empty:
                return None
                
            # Clean up the data
            hist_data = hist_data.dropna()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in hist_data.columns for col in required_columns):
                return None
                
            return hist_data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_real_time_price(self, symbol: str) -> Optional[float]:
        """
        Get real-time stock price
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Current stock price or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                return None
                
            return float(data['Close'].iloc[-1])
            
        except Exception as e:
            print(f"Error fetching real-time price for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid data
            return bool(info and ('regularMarketPrice' in info or 'currentPrice' in info))
            
        except Exception:
            return False
    
    def get_financial_ratios(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Calculate and return key financial ratios
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary containing financial ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
                
            ratios = {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins')
            }
            
            # Filter out None values
            return {k: v for k, v in ratios.items() if v is not None}
            
        except Exception as e:
            print(f"Error calculating financial ratios for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for buy/sell signals
        
        Args:
            data: Historical stock data
            
        Returns:
            DataFrame with technical indicators added
        """
        try:
            # Simple Moving Averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            
            # MACD
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
            
            return data
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return data
    
    def get_buy_sell_ratio(self, symbol: str) -> dict:
        """
        Calculate buy/sell ratio and market sentiment indicators
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with buy/sell ratio and market sentiment data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get institutional ownership data
            institutional_holders = ticker.institutional_holders
            major_holders = ticker.major_holders
            
            # Calculate buy/sell ratio based on various metrics
            buy_indicators = 0
            sell_indicators = 0
            
            # Check analyst recommendations
            recommendations = ticker.recommendations
            if recommendations is not None and not recommendations.empty:
                latest_rec = recommendations.iloc[-1]
                strong_buy = latest_rec.get('strongBuy', 0)
                buy = latest_rec.get('buy', 0)
                hold = latest_rec.get('hold', 0)
                sell = latest_rec.get('sell', 0)
                strong_sell = latest_rec.get('strongSell', 0)
                
                total_recs = strong_buy + buy + hold + sell + strong_sell
                if total_recs > 0:
                    buy_ratio = (strong_buy + buy) / total_recs
                    sell_ratio = (sell + strong_sell) / total_recs
                else:
                    buy_ratio = 0.5
                    sell_ratio = 0.5
            else:
                buy_ratio = 0.5
                sell_ratio = 0.5
            
            # Get target price information
            target_high = info.get('targetHighPrice', 0)
            target_low = info.get('targetLowPrice', 0)
            target_mean = info.get('targetMeanPrice', 0)
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # Calculate price target sentiment
            if target_mean and current_price:
                price_upside = ((target_mean - current_price) / current_price) * 100
                if price_upside > 10:
                    buy_indicators += 2
                elif price_upside > 0:
                    buy_indicators += 1
                elif price_upside < -10:
                    sell_indicators += 2
                elif price_upside < 0:
                    sell_indicators += 1
            
            # Calculate overall buy/sell ratio
            total_indicators = buy_indicators + sell_indicators
            if total_indicators > 0:
                calculated_buy_ratio = buy_indicators / total_indicators
                calculated_sell_ratio = sell_indicators / total_indicators
            else:
                calculated_buy_ratio = 0.5
                calculated_sell_ratio = 0.5
            
            # Combine analyst and calculated ratios
            final_buy_ratio = (buy_ratio + calculated_buy_ratio) / 2
            final_sell_ratio = (sell_ratio + calculated_sell_ratio) / 2
            
            # Determine market sentiment
            if final_buy_ratio > 0.6:
                market_sentiment = "Bullish"
                sentiment_color = "green"
            elif final_sell_ratio > 0.6:
                market_sentiment = "Bearish"
                sentiment_color = "red"
            else:
                market_sentiment = "Neutral"
                sentiment_color = "yellow"
            
            return {
                'buy_ratio': round(final_buy_ratio * 100, 1),
                'sell_ratio': round(final_sell_ratio * 100, 1),
                'hold_ratio': round((1 - final_buy_ratio - final_sell_ratio) * 100, 1),
                'market_sentiment': market_sentiment,
                'sentiment_color': sentiment_color,
                'analyst_recommendations': {
                    'strong_buy': strong_buy if 'strong_buy' in locals() else 0,
                    'buy': buy if 'buy' in locals() else 0,
                    'hold': hold if 'hold' in locals() else 0,
                    'sell': sell if 'sell' in locals() else 0,
                    'strong_sell': strong_sell if 'strong_sell' in locals() else 0
                },
                'target_price': target_mean,
                'current_price': current_price,
                'upside_potential': price_upside if 'price_upside' in locals() else 0
            }
            
        except Exception as e:
            print(f"Error calculating buy/sell ratio: {e}")
            return {
                'buy_ratio': 50.0,
                'sell_ratio': 50.0,
                'hold_ratio': 0.0,
                'market_sentiment': 'Neutral',
                'sentiment_color': 'yellow',
                'analyst_recommendations': {
                    'strong_buy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strong_sell': 0
                },
                'target_price': 0,
                'current_price': 0,
                'upside_potential': 0
            }
    
    def generate_buy_sell_signal(self, data: pd.DataFrame, symbol: str = None) -> dict:
        """
        Generate buy/sell signals based on technical indicators and market sentiment
        
        Args:
            data: Historical stock data with technical indicators
            symbol: Stock ticker symbol for additional analysis
            
        Returns:
            Dictionary with signal information
        """
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            
            signals = []
            signal_strength = 0
            
            # RSI signals
            if latest['RSI'] < 30:
                signals.append("RSI oversold (bullish)")
                signal_strength += 2
            elif latest['RSI'] > 70:
                signals.append("RSI overbought (bearish)")
                signal_strength -= 2
            
            # Moving Average signals
            if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                signals.append("Price above moving averages (bullish)")
                signal_strength += 1
            elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
                signals.append("Price below moving averages (bearish)")
                signal_strength -= 1
            
            # MACD signals
            if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signals.append("MACD bullish crossover")
                signal_strength += 2
            elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                signals.append("MACD bearish crossover")
                signal_strength -= 2
            
            # Bollinger Bands signals
            if latest['Close'] < latest['BB_Lower']:
                signals.append("Price below lower Bollinger Band (bullish)")
                signal_strength += 1
            elif latest['Close'] > latest['BB_Upper']:
                signals.append("Price above upper Bollinger Band (bearish)")
                signal_strength -= 1
            
            # Volume confirmation
            if latest['Volume_Ratio'] > 1.5:
                signals.append("High volume activity")
                signal_strength += 0.5 if signal_strength > 0 else -0.5
            
            # Get buy/sell ratio for additional confirmation
            buy_sell_data = None
            if symbol:
                try:
                    buy_sell_data = self.get_buy_sell_ratio(symbol)
                    
                    # Add buy/sell ratio to signal strength
                    if buy_sell_data['buy_ratio'] > 60:
                        signals.append(f"Analyst consensus bullish ({buy_sell_data['buy_ratio']}% buy)")
                        signal_strength += 1
                    elif buy_sell_data['sell_ratio'] > 60:
                        signals.append(f"Analyst consensus bearish ({buy_sell_data['sell_ratio']}% sell)")
                        signal_strength -= 1
                    
                    # Add target price sentiment
                    if buy_sell_data['upside_potential'] > 15:
                        signals.append(f"Strong upside potential (+{buy_sell_data['upside_potential']:.1f}%)")
                        signal_strength += 1
                    elif buy_sell_data['upside_potential'] < -15:
                        signals.append(f"Downside risk ({buy_sell_data['upside_potential']:.1f}%)")
                        signal_strength -= 1
                        
                except Exception as e:
                    print(f"Error getting buy/sell ratio: {e}")
            
            # Determine overall signal
            if signal_strength >= 3:
                overall_signal = "STRONG BUY"
                signal_color = "green"
            elif signal_strength >= 1:
                overall_signal = "BUY"
                signal_color = "lightgreen"
            elif signal_strength <= -3:
                overall_signal = "STRONG SELL"
                signal_color = "red"
            elif signal_strength <= -1:
                overall_signal = "SELL"
                signal_color = "orange"
            else:
                overall_signal = "HOLD"
                signal_color = "yellow"
            
            return {
                'signal': overall_signal,
                'strength': signal_strength,
                'color': signal_color,
                'reasons': signals,
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'price_vs_sma20': ((latest['Close'] - latest['SMA_20']) / latest['SMA_20']) * 100,
                'buy_sell_data': buy_sell_data
            }
            
        except Exception as e:
            print(f"Error generating buy/sell signal: {e}")
            return {
                'signal': 'UNKNOWN',
                'strength': 0,
                'color': 'gray',
                'reasons': ['Error calculating signals'],
                'rsi': None,
                'macd': None,
                'price_vs_sma20': None,
                'buy_sell_data': None
            }

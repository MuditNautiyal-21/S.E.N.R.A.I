import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.data_fetcher import StockDataFetcher

class BacktestingEngine:
    """Professional backtesting engine for trading strategies"""
    
    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.results_cache = {}
    
    def run_backtest(self, symbol: str, period: str = "2y", initial_capital: float = 10000.0) -> Dict:
        """
        Run comprehensive backtest on historical data
        
        Args:
            symbol: Stock ticker symbol
            period: Historical period to test
            initial_capital: Starting capital for backtest
            
        Returns:
            Detailed backtest results
        """
        try:
            # Get historical data
            historical_data = self.data_fetcher.get_historical_data(symbol, period)
            if historical_data is None or historical_data.empty:
                return self._empty_backtest_result()
            
            # Calculate technical indicators
            data_with_indicators = self.data_fetcher.calculate_technical_indicators(historical_data.copy())
            
            # Generate signals for each day
            signals = self._generate_historical_signals(data_with_indicators)
            
            # Simulate trading based on signals
            trades = self._simulate_trades(data_with_indicators, signals, initial_capital)
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades, data_with_indicators, initial_capital)
            
            # Calculate win/loss statistics
            trade_stats = self._calculate_trade_statistics(trades)
            
            # Calculate maximum drawdown
            drawdown_stats = self._calculate_drawdown(trades)
            
            return {
                'symbol': symbol,
                'period': period,
                'initial_capital': initial_capital,
                'final_portfolio_value': performance['final_value'],
                'total_return': performance['total_return'],
                'total_return_pct': performance['total_return_pct'],
                'annualized_return': performance['annualized_return'],
                'volatility': performance['volatility'],
                'sharpe_ratio': performance['sharpe_ratio'],
                'max_drawdown': drawdown_stats['max_drawdown'],
                'max_drawdown_pct': drawdown_stats['max_drawdown_pct'],
                'total_trades': trade_stats['total_trades'],
                'winning_trades': trade_stats['winning_trades'],
                'losing_trades': trade_stats['losing_trades'],
                'win_rate': trade_stats['win_rate'],
                'avg_win': trade_stats['avg_win'],
                'avg_loss': trade_stats['avg_loss'],
                'profit_factor': trade_stats['profit_factor'],
                'trades_detail': trades,
                'daily_values': [trade['portfolio_value'] for trade in trades],
                'dates': data_with_indicators.index.tolist(),
                'buy_signals': signals['buy_signals'],
                'sell_signals': signals['sell_signals']
            }
            
        except Exception as e:
            print(f"Error running backtest for {symbol}: {e}")
            return self._empty_backtest_result()
    
    def _generate_historical_signals(self, data: pd.DataFrame) -> Dict:
        """Generate buy/sell signals for historical data"""
        buy_signals = []
        sell_signals = []
        
        for i in range(1, len(data)):
            try:
                # Create a subset for signal generation (up to current point)
                current_data = data.iloc[:i+1].copy()
                
                # Generate signal for current point
                signal_info = self.data_fetcher.generate_buy_sell_signal(current_data)
                
                signal = signal_info.get('signal', 'HOLD')
                date = data.index[i]
                price = data['Close'].iloc[i]
                
                if 'BUY' in signal:
                    buy_signals.append({
                        'date': date,
                        'price': price,
                        'signal_strength': signal_info.get('strength', 0),
                        'reasons': signal_info.get('reasons', [])
                    })
                elif 'SELL' in signal:
                    sell_signals.append({
                        'date': date,
                        'price': price,
                        'signal_strength': signal_info.get('strength', 0),
                        'reasons': signal_info.get('reasons', [])
                    })
                    
            except Exception as e:
                continue  # Skip problematic data points
        
        return {
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }
    
    def _simulate_trades(self, data: pd.DataFrame, signals: Dict, initial_capital: float) -> List[Dict]:
        """Simulate trading based on generated signals"""
        trades = []
        current_capital = initial_capital
        current_shares = 0
        position_cost = 0
        
        # Combine and sort signals by date
        all_signals = []
        
        for signal in signals['buy_signals']:
            all_signals.append({
                'date': signal['date'],
                'type': 'BUY',
                'price': signal['price'],
                'strength': signal['signal_strength']
            })
        
        for signal in signals['sell_signals']:
            all_signals.append({
                'date': signal['date'],
                'type': 'SELL',
                'price': signal['price'],
                'strength': signal['signal_strength']
            })
        
        # Sort by date
        all_signals.sort(key=lambda x: x['date'])
        
        # Process each signal
        for signal in all_signals:
            date = signal['date']
            price = signal['price']
            signal_type = signal['type']
            
            # Calculate position size based on signal strength (risk management)
            position_size = min(0.1, abs(signal['strength']) * 0.02)  # Max 10% per trade
            
            if signal_type == 'BUY' and current_shares == 0 and current_capital > 0:
                # Buy signal - enter position
                investment_amount = current_capital * position_size
                shares_to_buy = investment_amount / price
                
                current_shares = shares_to_buy
                position_cost = investment_amount
                current_capital -= investment_amount
                
                trades.append({
                    'date': date,
                    'type': 'BUY',
                    'shares': shares_to_buy,
                    'price': price,
                    'amount': investment_amount,
                    'capital': current_capital,
                    'portfolio_value': current_capital + (current_shares * price)
                })
                
            elif signal_type == 'SELL' and current_shares > 0:
                # Sell signal - exit position
                sell_amount = current_shares * price
                profit_loss = sell_amount - position_cost
                
                current_capital += sell_amount
                current_shares = 0
                position_cost = 0
                
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'shares': current_shares,
                    'price': price,
                    'amount': sell_amount,
                    'profit_loss': profit_loss,
                    'capital': current_capital,
                    'portfolio_value': current_capital
                })
        
        # Add daily portfolio values for visualization
        for i, date in enumerate(data.index):
            if not any(trade['date'] == date for trade in trades):
                current_price = data['Close'].iloc[i]
                portfolio_value = current_capital + (current_shares * current_price)
                
                trades.append({
                    'date': date,
                    'type': 'HOLD',
                    'shares': current_shares,
                    'price': current_price,
                    'capital': current_capital,
                    'portfolio_value': portfolio_value
                })
        
        return sorted(trades, key=lambda x: x['date'])
    
    def _calculate_performance_metrics(self, trades: List[Dict], data: pd.DataFrame, initial_capital: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        try:
            if not trades:
                return {'final_value': initial_capital, 'total_return': 0, 'total_return_pct': 0,
                       'annualized_return': 0, 'volatility': 0, 'sharpe_ratio': 0}
            
            final_value = trades[-1]['portfolio_value']
            total_return = final_value - initial_capital
            total_return_pct = (total_return / initial_capital) * 100
            
            # Calculate annualized return
            days = (data.index[-1] - data.index[0]).days
            years = days / 365.25
            annualized_return = ((final_value / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
            
            # Calculate volatility (standard deviation of daily returns)
            portfolio_values = [trade['portfolio_value'] for trade in trades]
            daily_returns = [
                (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                for i in range(1, len(portfolio_values))
            ]
            volatility = np.std(daily_returns) * np.sqrt(252) * 100 if daily_returns else 0  # Annualized
            
            # Calculate Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 2.0
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            return {
                'final_value': final_value,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            }
            
        except Exception as e:
            print(f"Error calculating performance metrics: {e}")
            return {'final_value': initial_capital, 'total_return': 0, 'total_return_pct': 0,
                   'annualized_return': 0, 'volatility': 0, 'sharpe_ratio': 0}
    
    def _calculate_trade_statistics(self, trades: List[Dict]) -> Dict:
        """Calculate win/loss statistics"""
        try:
            trading_trades = [trade for trade in trades if trade.get('type') in ['BUY', 'SELL'] and 'profit_loss' in trade]
            
            if not trading_trades:
                return {'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                       'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0}
            
            profits = [trade['profit_loss'] for trade in trading_trades if trade['profit_loss'] > 0]
            losses = [trade['profit_loss'] for trade in trading_trades if trade['profit_loss'] < 0]
            
            total_trades = len(trading_trades)
            winning_trades = len(profits)
            losing_trades = len(losses)
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            avg_win = np.mean(profits) if profits else 0
            avg_loss = np.mean(losses) if losses else 0
            
            gross_profit = sum(profits)
            gross_loss = abs(sum(losses))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor
            }
            
        except Exception as e:
            print(f"Error calculating trade statistics: {e}")
            return {'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                   'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0}
    
    def _calculate_drawdown(self, trades: List[Dict]) -> Dict:
        """Calculate maximum drawdown"""
        try:
            portfolio_values = [trade['portfolio_value'] for trade in trades]
            if not portfolio_values:
                return {'max_drawdown': 0, 'max_drawdown_pct': 0}
            
            peak = portfolio_values[0]
            max_drawdown = 0
            max_drawdown_pct = 0
            
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = peak - value
                drawdown_pct = (drawdown / peak) * 100 if peak > 0 else 0
                
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_pct = drawdown_pct
            
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown_pct
            }
            
        except Exception as e:
            print(f"Error calculating drawdown: {e}")
            return {'max_drawdown': 0, 'max_drawdown_pct': 0}
    
    def _empty_backtest_result(self) -> Dict:
        """Return empty backtest result for error cases"""
        return {
            'symbol': '',
            'period': '',
            'initial_capital': 0,
            'final_portfolio_value': 0,
            'total_return': 0,
            'total_return_pct': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'trades_detail': [],
            'daily_values': [],
            'dates': [],
            'buy_signals': [],
            'sell_signals': []
        }
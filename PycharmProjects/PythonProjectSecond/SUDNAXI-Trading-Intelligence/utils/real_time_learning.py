"""
Real-time Continuous Learning System for Trading Strategies
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import threading
import time
from utils.enhanced_backtesting import EnhancedBacktestingEngine
from ml.adaptive_strategy import AdaptiveStrategyEngine

class RealTimeLearningEngine:
    """Continuous learning system that adapts strategies in real-time"""
    
    def __init__(self):
        self.adaptive_engine = AdaptiveStrategyEngine()
        self.performance_history = []
        self.learning_sessions = []
        self.is_learning = False
        self.last_adaptation = datetime.now()
        self.adaptation_interval = timedelta(minutes=30)  # Adapt every 30 minutes
        
    def start_continuous_learning(self, symbol: str, data: pd.DataFrame):
        """Start background continuous learning process"""
        if self.is_learning:
            return "Learning already in progress"
        
        self.is_learning = True
        self.learning_thread = threading.Thread(
            target=self._continuous_learning_loop,
            args=(symbol, data),
            daemon=True
        )
        self.learning_thread.start()
        
        return "Continuous learning started"
    
    def stop_continuous_learning(self):
        """Stop the continuous learning process"""
        self.is_learning = False
        return "Continuous learning stopped"
    
    def _continuous_learning_loop(self, symbol: str, data: pd.DataFrame):
        """Main continuous learning loop"""
        while self.is_learning:
            try:
                # Check if it's time for adaptation
                if datetime.now() - self.last_adaptation >= self.adaptation_interval:
                    self._perform_adaptation(symbol, data)
                    self.last_adaptation = datetime.now()
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
            except Exception as e:
                print(f"Continuous learning error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _perform_adaptation(self, symbol: str, data: pd.DataFrame):
        """Perform real-time strategy adaptation"""
        try:
            # Get latest market data
            latest_data = data.tail(100)  # Last 100 data points
            
            # Generate signals with current strategy
            current_signals = []
            for i in range(20, len(latest_data)):
                historical_slice = latest_data.iloc[:i+1]
                signal = self.adaptive_engine.generate_adaptive_signals(historical_slice)
                current_signals.append(signal)
            
            # Evaluate recent performance
            recent_performance = self._evaluate_recent_performance(current_signals, latest_data)
            
            # Adapt strategy if performance is declining
            if recent_performance['needs_adaptation']:
                adaptation_result = self.adaptive_engine.adapt_strategy(recent_performance['trades'])
                
                # Log adaptation event
                adaptation_event = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'trigger': 'Real-time Performance Decline',
                    'adaptations': adaptation_result.get('adaptations', []),
                    'new_weights': adaptation_result.get('new_weights', {}),
                    'performance_metrics': recent_performance['metrics']
                }
                
                self.learning_sessions.append(adaptation_event)
                
                # Retrain models if significant adaptation occurred
                if len(adaptation_result.get('adaptations', [])) > 2:
                    self.adaptive_engine.retrain_if_needed(latest_data)
                
                return adaptation_event
            
        except Exception as e:
            print(f"Adaptation error: {e}")
            return None
    
    def _evaluate_recent_performance(self, signals: List[Dict], data: pd.DataFrame) -> Dict:
        """Evaluate recent trading performance"""
        
        # Simulate trades based on recent signals
        portfolio_value = 10000
        cash = 10000
        shares = 0
        trades = []
        
        for i, signal in enumerate(signals):
            if i + 20 >= len(data):
                break
                
            current_price = data.iloc[i + 20]['Close']
            
            # Simple trading logic
            if signal.get('signal') == 'BUY' and cash > current_price:
                shares_to_buy = min(100, cash // current_price)
                if shares_to_buy > 0:
                    cash -= shares_to_buy * current_price
                    shares += shares_to_buy
                    trades.append({
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'timestamp': i
                    })
            
            elif signal.get('signal') == 'SELL' and shares > 0:
                shares_to_sell = min(shares, 50)
                cash += shares_to_sell * current_price
                shares -= shares_to_sell
                trades.append({
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares_to_sell,
                    'timestamp': i
                })
        
        # Calculate performance metrics
        final_value = cash + shares * data.iloc[-1]['Close']
        total_return = (final_value - 10000) / 10000
        
        # Determine if adaptation is needed
        needs_adaptation = (
            total_return < -0.02 or  # More than 2% loss
            len(trades) < 3 or       # Very few trades
            len([t for t in trades if t['action'] == 'BUY']) == 0  # No buy signals
        )
        
        return {
            'needs_adaptation': needs_adaptation,
            'trades': trades,
            'metrics': {
                'total_return': total_return,
                'final_value': final_value,
                'total_trades': len(trades),
                'portfolio_value': final_value
            }
        }
    
    def get_learning_status(self) -> Dict:
        """Get current learning status and statistics"""
        return {
            'is_learning': self.is_learning,
            'last_adaptation': self.last_adaptation.isoformat() if self.last_adaptation else None,
            'total_adaptations': len(self.learning_sessions),
            'next_adaptation_in': str(self.adaptation_interval - (datetime.now() - self.last_adaptation)),
            'recent_sessions': self.learning_sessions[-5:] if self.learning_sessions else []
        }
    
    def force_adaptation(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Force immediate strategy adaptation"""
        return self._perform_adaptation(symbol, data)
    
    def get_adaptation_history(self) -> List[Dict]:
        """Get history of all adaptations"""
        return self.learning_sessions
    
    def reset_learning_history(self):
        """Reset learning history and start fresh"""
        self.learning_sessions = []
        self.performance_history = []
        return "Learning history reset"

# Global real-time learning engine
real_time_engine = RealTimeLearningEngine()
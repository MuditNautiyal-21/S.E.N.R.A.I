"""
Reinforcement Learning Trading Agent with Real-time Strategy Adaptation
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import joblib
import os
from datetime import datetime, timedelta

# Try to import RL dependencies, fallback if not available
try:
    import gym
    from gym import spaces
    from stable_baselines3 import PPO, A2C, DQN
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv
    HAS_RL_DEPS = True
except ImportError:
    HAS_RL_DEPS = False
    # Create dummy classes for compatibility
    class Env:
        pass
    class spaces:
        @staticmethod
        def Discrete(n):
            return None
        @staticmethod
        def Box(low, high, shape, dtype):
            return None

class TradingEnvironment(Env if HAS_RL_DEPS else object):
    """Custom Trading Environment for Reinforcement Learning"""
    
    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000, 
                 lookback_window: int = 20, transaction_cost: float = 0.001):
        if HAS_RL_DEPS:
            super(TradingEnvironment, self).__init__()
        
        self.data = data.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.lookback_window = lookback_window
        self.transaction_cost = transaction_cost
        
        # Environment state
        self.current_step = 0
        self.balance = initial_balance
        self.shares_held = 0
        self.net_worth = initial_balance
        self.max_net_worth = initial_balance
        self.total_shares_sold = 0
        self.total_sales_value = 0
        
        # Action space: 0=Hold, 1=Buy, 2=Sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: OHLCV + technical indicators + portfolio state
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(lookback_window * 8 + 3,), dtype=np.float32
        )
        
        # Performance tracking
        self.trades = []
        self.portfolio_values = []
        self.actions_taken = []
        
    def reset(self):
        """Reset the environment to initial state"""
        self.current_step = self.lookback_window
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.trades = []
        self.portfolio_values = []
        self.actions_taken = []
        
        return self._get_observation()
    
    def _get_observation(self):
        """Get current observation state"""
        # Get lookback window data
        start = max(0, self.current_step - self.lookback_window)
        end = self.current_step
        
        if end > len(self.data):
            end = len(self.data)
            start = max(0, end - self.lookback_window)
        
        frame = self.data.iloc[start:end]
        
        # Normalize price data
        if len(frame) < self.lookback_window:
            # Pad with zeros if not enough data
            padding = np.zeros((self.lookback_window - len(frame), 8))
            obs_data = np.vstack([padding, frame[['Open', 'High', 'Low', 'Close', 'Volume', 
                                               'RSI', 'MACD', 'SMA_20']].values])
        else:
            obs_data = frame[['Open', 'High', 'Low', 'Close', 'Volume', 
                            'RSI', 'MACD', 'SMA_20']].values
        
        # Flatten the observation
        obs = obs_data.flatten()
        
        # Add portfolio state
        portfolio_state = np.array([
            self.balance / self.initial_balance,
            self.shares_held,
            self.net_worth / self.initial_balance
        ])
        
        return np.concatenate([obs, portfolio_state]).astype(np.float32)
    
    def step(self, action):
        """Execute one step in the environment"""
        current_price = self.data.iloc[self.current_step]['Close']
        
        # Execute action
        reward = 0
        if action == 1:  # Buy
            reward = self._buy_stock(current_price)
        elif action == 2:  # Sell
            reward = self._sell_stock(current_price)
        
        # Update portfolio value
        self.net_worth = self.balance + self.shares_held * current_price
        self.portfolio_values.append(self.net_worth)
        self.actions_taken.append(action)
        
        # Calculate reward based on portfolio performance
        if len(self.portfolio_values) > 1:
            return_rate = (self.portfolio_values[-1] - self.portfolio_values[-2]) / self.portfolio_values[-2]
            reward += return_rate * 100  # Scale reward
        
        # Penalty for excessive trading
        if action != 0:  # Not holding
            reward -= self.transaction_cost * 10
        
        # Bonus for outperforming buy-and-hold
        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth
            reward += 1
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        return self._get_observation(), reward, done, {}
    
    def _buy_stock(self, current_price):
        """Execute buy action"""
        # Use 20% of available balance for each buy
        buy_amount = self.balance * 0.2
        shares_to_buy = buy_amount / current_price
        cost = shares_to_buy * current_price * (1 + self.transaction_cost)
        
        if cost <= self.balance:
            self.balance -= cost
            self.shares_held += shares_to_buy
            
            self.trades.append({
                'action': 'BUY',
                'shares': shares_to_buy,
                'price': current_price,
                'step': self.current_step,
                'balance': self.balance
            })
            return 1  # Positive reward for successful buy
        return -1  # Penalty for invalid buy
    
    def _sell_stock(self, current_price):
        """Execute sell action"""
        if self.shares_held > 0:
            # Sell 50% of holdings
            shares_to_sell = self.shares_held * 0.5
            sale_amount = shares_to_sell * current_price * (1 - self.transaction_cost)
            
            self.balance += sale_amount
            self.shares_held -= shares_to_sell
            self.total_shares_sold += shares_to_sell
            self.total_sales_value += sale_amount
            
            self.trades.append({
                'action': 'SELL',
                'shares': shares_to_sell,
                'price': current_price,
                'step': self.current_step,
                'balance': self.balance
            })
            return 1  # Positive reward for successful sell
        return -1  # Penalty for invalid sell


class ReinforcementLearningTrader:
    """Advanced RL Trading Agent with Strategy Adaptation"""
    
    def __init__(self, algorithm: str = 'PPO'):
        self.algorithm = algorithm
        self.model = None
        self.scaler = StandardScaler()
        self.performance_history = []
        self.strategy_adaptations = []
        
    def train_model(self, data: pd.DataFrame, episodes: int = 10000, 
                   save_path: str = None) -> Dict:
        """Train the RL model on historical data"""
        
        if not HAS_RL_DEPS:
            print("Warning: RL dependencies not available. Using fallback basic strategy.")
            return {
                'algorithm': 'Fallback',
                'training_episodes': 0,
                'final_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'warning': 'RL dependencies not available'
            }
        
        # Create training environment
        env = TradingEnvironment(data)
        env = DummyVecEnv([lambda: env])
        
        # Initialize model based on algorithm
        if self.algorithm == 'PPO':
            self.model = PPO('MlpPolicy', env, verbose=1, 
                           learning_rate=0.0003, n_steps=2048)
        elif self.algorithm == 'A2C':
            self.model = A2C('MlpPolicy', env, verbose=1)
        elif self.algorithm == 'DQN':
            self.model = DQN('MlpPolicy', env, verbose=1, 
                           learning_rate=0.0001, buffer_size=50000)
        
        # Train the model
        print(f"Training {self.algorithm} model for {episodes} timesteps...")
        self.model.learn(total_timesteps=episodes)
        
        # Save model if path provided
        if save_path:
            self.model.save(save_path)
            joblib.dump(self.scaler, f"{save_path}_scaler.pkl")
        
        # Evaluate training performance
        train_results = self._evaluate_model(data)
        
        return {
            'algorithm': self.algorithm,
            'training_episodes': episodes,
            'final_return': train_results['total_return'],
            'sharpe_ratio': train_results['sharpe_ratio'],
            'max_drawdown': train_results['max_drawdown']
        }
    
    def _evaluate_model(self, data: pd.DataFrame) -> Dict:
        """Evaluate model performance on given data"""
        env = TradingEnvironment(data)
        
        obs = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action, _states = self.model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
        
        # Calculate performance metrics
        portfolio_values = env.portfolio_values
        if len(portfolio_values) > 1:
            returns = np.diff(portfolio_values) / portfolio_values[:-1]
            total_return = (portfolio_values[-1] - env.initial_balance) / env.initial_balance
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # Calculate max drawdown
            peak = np.maximum.accumulate(portfolio_values)
            drawdown = (portfolio_values - peak) / peak
            max_drawdown = np.min(drawdown)
        else:
            total_return = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(env.trades),
            'portfolio_values': portfolio_values,
            'trades': env.trades,
            'actions': env.actions_taken
        }
    
    def adaptive_backtest(self, data: pd.DataFrame, adaptation_frequency: int = 50) -> Dict:
        """Run adaptive backtesting with real-time strategy updates"""
        
        total_length = len(data)
        adaptation_points = range(adaptation_frequency, total_length, adaptation_frequency)
        
        results = {
            'adaptations': [],
            'performance_segments': [],
            'overall_performance': {},
            'strategy_evolution': []
        }
        
        current_start = 0
        overall_portfolio_values = []
        overall_trades = []
        
        for i, adaptation_point in enumerate(adaptation_points):
            # Get data segment for training
            train_data = data.iloc[current_start:adaptation_point]
            
            if len(train_data) < 20:  # Skip if not enough data
                continue
            
            print(f"Adaptation {i+1}: Training on data from {current_start} to {adaptation_point}")
            
            # Retrain model on recent data
            training_results = self.train_model(train_data, episodes=2000)
            
            # Test on next segment
            test_start = adaptation_point
            test_end = min(adaptation_point + adaptation_frequency, total_length)
            test_data = data.iloc[test_start:test_end]
            
            if len(test_data) > 5:
                segment_results = self._evaluate_model(test_data)
                
                adaptation_info = {
                    'adaptation_number': i + 1,
                    'train_period': (current_start, adaptation_point),
                    'test_period': (test_start, test_end),
                    'training_performance': training_results,
                    'test_performance': segment_results
                }
                
                results['adaptations'].append(adaptation_info)
                results['performance_segments'].append(segment_results)
                
                # Track strategy evolution
                strategy_state = {
                    'timestamp': datetime.now().isoformat(),
                    'adaptation_point': adaptation_point,
                    'performance_improvement': segment_results['total_return'],
                    'trade_frequency': len(segment_results['trades']) / len(test_data)
                }
                results['strategy_evolution'].append(strategy_state)
                
                overall_portfolio_values.extend(segment_results['portfolio_values'])
                overall_trades.extend(segment_results['trades'])
            
            current_start = adaptation_point
        
        # Calculate overall performance
        if overall_portfolio_values:
            initial_value = overall_portfolio_values[0] if overall_portfolio_values else 10000
            final_value = overall_portfolio_values[-1] if overall_portfolio_values else 10000
            
            returns = np.diff(overall_portfolio_values) / overall_portfolio_values[:-1]
            total_return = (final_value - initial_value) / initial_value
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            peak = np.maximum.accumulate(overall_portfolio_values)
            drawdown = (overall_portfolio_values - peak) / peak
            max_drawdown = np.min(drawdown)
            
            results['overall_performance'] = {
                'total_return': total_return,
                'total_return_pct': total_return * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'total_adaptations': len(adaptation_points),
                'total_trades': len(overall_trades),
                'portfolio_values': overall_portfolio_values,
                'all_trades': overall_trades
            }
        
        return results
    
    def load_model(self, model_path: str):
        """Load a pre-trained model"""
        if self.algorithm == 'PPO':
            self.model = PPO.load(model_path)
        elif self.algorithm == 'A2C':
            self.model = A2C.load(model_path)
        elif self.algorithm == 'DQN':
            self.model = DQN.load(model_path)
        
        # Load scaler if available
        scaler_path = f"{model_path}_scaler.pkl"
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
    
    def predict_action(self, observation: np.ndarray) -> Tuple[int, float]:
        """Predict next action given current market state"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        action, _states = self.model.predict(observation, deterministic=True)
        
        # Get confidence score (simplified)
        action_probs = self.model.policy.get_distribution(observation).distribution.probs
        confidence = float(np.max(action_probs))
        
        return int(action), confidence
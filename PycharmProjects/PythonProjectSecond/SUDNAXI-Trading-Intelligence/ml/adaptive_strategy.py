"""
Adaptive Trading Strategy Engine with Machine Learning and Self-Learning Capabilities
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
import json

class AdaptiveStrategyEngine:
    """Advanced ML-based trading strategy that learns and adapts in real-time"""
    
    def __init__(self, learning_rate: float = 0.01, adaptation_threshold: float = 0.05):
        self.learning_rate = learning_rate
        self.adaptation_threshold = adaptation_threshold
        
        # ML Models for different aspects
        self.price_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.signal_classifier = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.risk_assessor = RandomForestRegressor(n_estimators=50, random_state=42)
        
        # Scalers for feature normalization
        self.price_scaler = StandardScaler()
        self.signal_scaler = StandardScaler()
        self.risk_scaler = StandardScaler()
        
        # Strategy state tracking
        self.strategy_weights = {
            'technical': 0.4,
            'momentum': 0.3,
            'mean_reversion': 0.2,
            'volatility': 0.1
        }
        
        # Performance tracking
        self.performance_history = []
        self.adaptation_log = []
        self.trade_outcomes = []
        
        # Model performance metrics
        self.model_accuracy = {'price': 0.0, 'signal': 0.0, 'risk': 0.0}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare comprehensive feature set for ML models"""
        df = data.copy()
        
        # Price-based features
        df['price_change'] = df['Close'].pct_change()
        df['price_change_abs'] = df['price_change'].abs()
        df['high_low_pct'] = (df['High'] - df['Low']) / df['Close']
        df['open_close_pct'] = (df['Close'] - df['Open']) / df['Open']
        
        # Moving averages and trends
        for window in [5, 10, 20, 50]:
            df[f'sma_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'price_vs_sma_{window}'] = df['Close'] / df[f'sma_{window}'] - 1
        
        # Volatility features
        df['volatility_5'] = df['price_change'].rolling(5).std()
        df['volatility_20'] = df['price_change'].rolling(20).std()
        df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']
        
        # Volume features
        df['volume_sma_10'] = df['Volume'].rolling(10).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_10']
        df['price_volume'] = df['price_change'] * df['volume_ratio']
        
        # Technical momentum
        df['rsi_momentum'] = df['RSI'].diff()
        df['macd_momentum'] = df['MACD'].diff()
        df['price_momentum_5'] = df['Close'].pct_change(5)
        df['price_momentum_10'] = df['Close'].pct_change(10)
        
        # Support/Resistance levels
        df['resistance_strength'] = df['High'].rolling(20).max() / df['Close'] - 1
        df['support_strength'] = 1 - df['Low'].rolling(20).min() / df['Close']
        
        # Market regime detection
        df['trend_strength'] = (df['Close'] / df['sma_50'] - 1).rolling(10).mean()
        df['market_regime'] = np.where(df['trend_strength'] > 0.02, 1, 
                                     np.where(df['trend_strength'] < -0.02, -1, 0))
        
        # Bollinger Band position
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            df['bb_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
            df['bb_squeeze'] = (df['BB_upper'] - df['BB_lower']) / df['Close']
        
        return df
    
    def train_models(self, data: pd.DataFrame) -> Dict:
        """Train all ML models on historical data"""
        
        # Prepare features
        df = self.prepare_features(data)
        df = df.dropna()
        
        if len(df) < 50:
            return {'status': 'error', 'message': 'Insufficient data for training'}
        
        # Feature columns for different models
        price_features = [col for col in df.columns if col not in 
                         ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
        
        # Prepare target variables
        df['future_return_1'] = df['Close'].pct_change().shift(-1)  # Next period return
        df['future_return_5'] = df['Close'].pct_change(5).shift(-5)  # 5-period return
        df['signal_target'] = np.where(df['future_return_1'] > 0.01, 1, 
                                     np.where(df['future_return_1'] < -0.01, -1, 0))
        
        # Remove rows with NaN targets
        df = df.dropna()
        
        if len(df) < 30:
            return {'status': 'error', 'message': 'Insufficient data after preprocessing'}
        
        X = df[price_features].values
        
        # Train price prediction model
        y_price = df['future_return_1'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y_price, test_size=0.2, random_state=42)
        
        X_train_scaled = self.price_scaler.fit_transform(X_train)
        X_test_scaled = self.price_scaler.transform(X_test)
        
        self.price_predictor.fit(X_train_scaled, y_train)
        price_pred = self.price_predictor.predict(X_test_scaled)
        price_accuracy = r2_score(y_test, price_pred)
        self.model_accuracy['price'] = max(0, price_accuracy)
        
        # Train signal classification model
        y_signal = df['signal_target'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y_signal, test_size=0.2, random_state=42)
        
        X_train_scaled = self.signal_scaler.fit_transform(X_train)
        X_test_scaled = self.signal_scaler.transform(X_test)
        
        self.signal_classifier.fit(X_train_scaled, y_train)
        signal_pred = self.signal_classifier.predict(X_test_scaled)
        signal_accuracy = r2_score(y_test, signal_pred)
        self.model_accuracy['signal'] = max(0, signal_accuracy)
        
        # Train risk assessment model
        df['volatility_target'] = df['volatility_20']
        y_risk = df['volatility_target'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y_risk, test_size=0.2, random_state=42)
        
        X_train_scaled = self.risk_scaler.fit_transform(X_train)
        X_test_scaled = self.risk_scaler.transform(X_test)
        
        self.risk_assessor.fit(X_train_scaled, y_train)
        risk_pred = self.risk_assessor.predict(X_test_scaled)
        risk_accuracy = r2_score(y_test, risk_pred)
        self.model_accuracy['risk'] = max(0, risk_accuracy)
        
        training_results = {
            'status': 'success',
            'samples_trained': len(df),
            'price_model_accuracy': price_accuracy,
            'signal_model_accuracy': signal_accuracy,
            'risk_model_accuracy': risk_accuracy,
            'features_used': len(price_features),
            'training_date': datetime.now().isoformat()
        }
        
        return training_results
    
    def generate_adaptive_signals(self, data: pd.DataFrame) -> Dict:
        """Generate trading signals using adaptive ML models"""
        
        # Prepare features for latest data point
        df = self.prepare_features(data)
        latest_features = df.iloc[-1]
        
        # Get feature columns
        feature_cols = [col for col in df.columns if col not in 
                       ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
        
        X_latest = latest_features[feature_cols].values.reshape(1, -1)
        
        # Handle missing values
        if np.isnan(X_latest).any():
            X_latest = np.nan_to_num(X_latest, nan=0.0)
        
        try:
            # Get predictions from all models
            X_price_scaled = self.price_scaler.transform(X_latest)
            X_signal_scaled = self.signal_scaler.transform(X_latest)
            X_risk_scaled = self.risk_scaler.transform(X_latest)
            
            price_prediction = self.price_predictor.predict(X_price_scaled)[0]
            signal_strength = self.signal_classifier.predict(X_signal_scaled)[0]
            risk_assessment = self.risk_assessor.predict(X_risk_scaled)[0]
            
            # Combine predictions with adaptive weights
            final_signal_strength = (
                price_prediction * self.strategy_weights['technical'] +
                signal_strength * self.strategy_weights['momentum'] +
                risk_assessment * self.strategy_weights['volatility']
            )
            
            # Determine action based on signal strength and confidence
            confidence = (
                self.model_accuracy['price'] * 0.4 +
                self.model_accuracy['signal'] * 0.4 +
                self.model_accuracy['risk'] * 0.2
            )
            
            # Generate trading signal
            if final_signal_strength > 0.01 and confidence > 0.3:
                signal = "BUY"
                action_strength = min(5, final_signal_strength * 10)
            elif final_signal_strength < -0.01 and confidence > 0.3:
                signal = "SELL"
                action_strength = min(5, abs(final_signal_strength) * 10)
            else:
                signal = "HOLD"
                action_strength = 0
            
            return {
                'signal': signal,
                'strength': action_strength,
                'confidence': confidence,
                'price_prediction': price_prediction,
                'signal_raw': signal_strength,
                'risk_level': risk_assessment,
                'model_agreement': confidence,
                'strategy_weights': self.strategy_weights.copy(),
                'reasons': self._generate_signal_reasons(price_prediction, signal_strength, risk_assessment)
            }
            
        except Exception as e:
            # Fallback to traditional signal if ML fails
            return {
                'signal': 'HOLD',
                'strength': 0,
                'confidence': 0.1,
                'error': f'ML prediction failed: {str(e)}',
                'fallback': True,
                'reasons': ['Using fallback strategy due to prediction error']
            }
    
    def _generate_signal_reasons(self, price_pred: float, signal_strength: float, risk_level: float) -> List[str]:
        """Generate human-readable reasons for the trading signal"""
        reasons = []
        
        if abs(price_pred) > 0.02:
            direction = "upward" if price_pred > 0 else "downward"
            reasons.append(f"ML price model predicts {direction} movement ({price_pred:.3f})")
        
        if abs(signal_strength) > 0.5:
            direction = "bullish" if signal_strength > 0 else "bearish"
            reasons.append(f"Signal classifier shows {direction} momentum ({signal_strength:.2f})")
        
        if risk_level > 0.02:
            reasons.append(f"Risk model indicates high volatility ({risk_level:.3f})")
        elif risk_level < 0.01:
            reasons.append(f"Risk model indicates low volatility environment")
        
        # Add strategy weight insights
        dominant_strategy = max(self.strategy_weights, key=self.strategy_weights.get)
        reasons.append(f"Current strategy emphasizes {dominant_strategy} approach ({self.strategy_weights[dominant_strategy]:.2f})")
        
        return reasons
    
    def adapt_strategy(self, recent_performance: List[Dict]) -> Dict:
        """Adapt strategy weights based on recent performance"""
        
        if len(recent_performance) < 10:
            return {'status': 'insufficient_data', 'adaptations': []}
        
        # Analyze performance by strategy component
        strategy_performance = {strategy: [] for strategy in self.strategy_weights.keys()}
        
        for trade in recent_performance[-20:]:  # Last 20 trades
            if trade.get('profit_loss') is not None:
                # Attribute performance to dominant strategy at time of trade
                dominant = max(self.strategy_weights, key=self.strategy_weights.get)
                strategy_performance[dominant].append(trade['profit_loss'])
        
        adaptations = []
        
        # Adjust weights based on performance
        for strategy, profits in strategy_performance.items():
            if len(profits) >= 3:
                avg_profit = np.mean(profits)
                success_rate = len([p for p in profits if p > 0]) / len(profits)
                
                if success_rate > 0.6 and avg_profit > 0:
                    # Increase weight for successful strategy
                    old_weight = self.strategy_weights[strategy]
                    self.strategy_weights[strategy] = min(0.6, old_weight + self.learning_rate)
                    adaptations.append(f"Increased {strategy} weight from {old_weight:.3f} to {self.strategy_weights[strategy]:.3f}")
                
                elif success_rate < 0.4 or avg_profit < 0:
                    # Decrease weight for unsuccessful strategy
                    old_weight = self.strategy_weights[strategy]
                    self.strategy_weights[strategy] = max(0.1, old_weight - self.learning_rate)
                    adaptations.append(f"Decreased {strategy} weight from {old_weight:.3f} to {self.strategy_weights[strategy]:.3f}")
        
        # Normalize weights to sum to 1
        total_weight = sum(self.strategy_weights.values())
        for strategy in self.strategy_weights:
            self.strategy_weights[strategy] /= total_weight
        
        # Log adaptation
        adaptation_record = {
            'timestamp': datetime.now().isoformat(),
            'adaptations': adaptations,
            'new_weights': self.strategy_weights.copy(),
            'performance_analyzed': len(recent_performance)
        }
        
        self.adaptation_log.append(adaptation_record)
        
        return {
            'status': 'adapted',
            'adaptations': adaptations,
            'new_weights': self.strategy_weights,
            'adaptation_count': len(adaptations)
        }
    
    def retrain_if_needed(self, new_data: pd.DataFrame, performance_threshold: float = 0.3) -> bool:
        """Retrain models if performance drops below threshold"""
        
        current_avg_accuracy = np.mean(list(self.model_accuracy.values()))
        
        if current_avg_accuracy < performance_threshold:
            print(f"Model accuracy ({current_avg_accuracy:.3f}) below threshold ({performance_threshold})")
            print("Initiating model retraining...")
            
            retraining_results = self.train_models(new_data)
            
            if retraining_results['status'] == 'success':
                print(f"Retraining completed. New accuracy: {np.mean(list(self.model_accuracy.values())):.3f}")
                return True
            else:
                print(f"Retraining failed: {retraining_results.get('message', 'Unknown error')}")
                return False
        
        return False
    
    def save_strategy(self, filepath: str):
        """Save the trained strategy to disk"""
        strategy_data = {
            'strategy_weights': self.strategy_weights,
            'model_accuracy': self.model_accuracy,
            'adaptation_log': self.adaptation_log,
            'learning_rate': self.learning_rate,
            'adaptation_threshold': self.adaptation_threshold
        }
        
        # Save models
        joblib.dump(self.price_predictor, f"{filepath}_price_model.pkl")
        joblib.dump(self.signal_classifier, f"{filepath}_signal_model.pkl")
        joblib.dump(self.risk_assessor, f"{filepath}_risk_model.pkl")
        
        # Save scalers
        joblib.dump(self.price_scaler, f"{filepath}_price_scaler.pkl")
        joblib.dump(self.signal_scaler, f"{filepath}_signal_scaler.pkl")
        joblib.dump(self.risk_scaler, f"{filepath}_risk_scaler.pkl")
        
        # Save strategy data
        with open(f"{filepath}_strategy.json", 'w') as f:
            json.dump(strategy_data, f, indent=2)
    
    def load_strategy(self, filepath: str):
        """Load a trained strategy from disk"""
        try:
            # Load models
            self.price_predictor = joblib.load(f"{filepath}_price_model.pkl")
            self.signal_classifier = joblib.load(f"{filepath}_signal_model.pkl")
            self.risk_assessor = joblib.load(f"{filepath}_risk_model.pkl")
            
            # Load scalers
            self.price_scaler = joblib.load(f"{filepath}_price_scaler.pkl")
            self.signal_scaler = joblib.load(f"{filepath}_signal_scaler.pkl")
            self.risk_scaler = joblib.load(f"{filepath}_risk_scaler.pkl")
            
            # Load strategy data
            with open(f"{filepath}_strategy.json", 'r') as f:
                strategy_data = json.load(f)
            
            self.strategy_weights = strategy_data['strategy_weights']
            self.model_accuracy = strategy_data['model_accuracy']
            self.adaptation_log = strategy_data['adaptation_log']
            self.learning_rate = strategy_data['learning_rate']
            self.adaptation_threshold = strategy_data['adaptation_threshold']
            
            return True
        except Exception as e:
            print(f"Failed to load strategy: {e}")
            return False
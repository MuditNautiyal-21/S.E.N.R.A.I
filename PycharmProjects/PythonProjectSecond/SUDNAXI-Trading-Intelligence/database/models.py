"""
Database models for the professional trading platform
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from config import config

Base = declarative_base()

class TradingStrategy(Base):
    """Model for storing trading strategies and their performance"""
    __tablename__ = 'trading_strategies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # 'RL', 'Technical', 'Hybrid'
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    total_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)

class BacktestResult(Base):
    """Model for storing backtest results"""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    
    # Detailed metrics
    total_return_pct = Column(Float, nullable=False)
    annualized_return = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    
    # Trade details stored as JSON
    trades_data = Column(JSON, nullable=False)
    daily_returns = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    """Model for individual trades"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(10), nullable=False)
    trade_type = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    signal_strength = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Trade outcome (filled after position closes)
    profit_loss = Column(Float, default=0.0)
    is_profitable = Column(Boolean, default=None)

class StrategyPerformance(Base):
    """Model for tracking strategy performance over time"""
    __tablename__ = 'strategy_performance'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    portfolio_value = Column(Float, nullable=False)
    daily_return = Column(Float, nullable=False)
    cumulative_return = Column(Float, nullable=False)
    drawdown = Column(Float, nullable=False)

class MarketData(Base):
    """Model for caching market data"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)

# Database setup functions
def get_database_url():
    """Get database URL from configuration"""
    db_url = config.DATABASE_URL
    
    # Handle postgres:// URL format (convert to postgresql://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def create_engine_and_session():
    """Create database engine and session"""
    try:
        db_url = get_database_url()
        
        # Configure engine based on database type
        if db_url.startswith('sqlite'):
            engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(db_url, echo=False)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    except Exception as e:
        # Fallback to SQLite if main database fails
        fallback_url = 'sqlite:///./trading_app.db'
        engine = create_engine(fallback_url, echo=False, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal

def init_database():
    """Initialize database tables"""
    engine, _ = create_engine_and_session()
    Base.metadata.create_all(bind=engine)
    return engine

def get_db_session():
    """Get database session"""
    _, SessionLocal = create_engine_and_session()
    session = SessionLocal()
    try:
        return session
    finally:
        pass  # Don't close here, let caller handle it
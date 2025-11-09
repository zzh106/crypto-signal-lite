"""
技术指标计算和信号检测模块
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class IndicatorCalculator:
    """技术指标计算器"""
    
    def __init__(self):
        pass
    
    def _sma(self, series: pd.Series, length: int) -> pd.Series:
        """计算简单移动平均"""
        return series.rolling(window=length).mean()
    
    def _ema(self, series: pd.Series, length: int) -> pd.Series:
        """计算指数移动平均"""
        return series.ewm(span=length, adjust=False).mean()
    
    def _macd(self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        ema_fast = self._ema(series, fast)
        ema_slow = self._ema(series, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._ema(macd_line, signal)
        histogram = macd_line - signal_line
        return {
            "MACD": macd_line,
            "MACD_signal": signal_line,
            "MACD_hist": histogram
        }
    
    def _rsi(self, series: pd.Series, length: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _bbands(self, series: pd.Series, length: int = 20, std: float = 2.0) -> Dict[str, pd.Series]:
        """计算布林带"""
        middle = self._sma(series, length)
        std_dev = series.rolling(window=length).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return {
            "BB_upper": upper,
            "BB_middle": middle,
            "BB_lower": lower
        }
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            df: 包含 OHLCV 数据的 DataFrame
            
        Returns:
            添加了技术指标的 DataFrame
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # MA20, MA60
        df["MA20"] = self._sma(df["close"], 20)
        df["MA60"] = self._sma(df["close"], 60)
        
        # MACD (12, 26, 9)
        macd_data = self._macd(df["close"], fast=12, slow=26, signal=9)
        df["MACD"] = macd_data["MACD"]
        df["MACD_signal"] = macd_data["MACD_signal"]
        df["MACD_hist"] = macd_data["MACD_hist"]
        
        # RSI(14)
        df["RSI"] = self._rsi(df["close"], length=14)
        
        # BOLL(20)
        boll_data = self._bbands(df["close"], length=20, std=2.0)
        df["BB_upper"] = boll_data["BB_upper"]
        df["BB_middle"] = boll_data["BB_middle"]
        df["BB_lower"] = boll_data["BB_lower"]
        
        return df
    
    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        检测买卖信号
        
        买入信号：
        - MA20 上穿 MA60
        - MACD柱 > 0
        - RSI > 50
        
        卖出信号：
        - MA20 下穿 MA60
        - MACD柱 < 0
        - RSI < 60
        
        Args:
            df: 包含技术指标的 DataFrame
            
        Returns:
            添加了信号列的 DataFrame
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # 初始化信号列
        df["signal"] = 0  # 0: 无信号, 1: 买入, -1: 卖出
        df["signal_type"] = ""
        
        # 计算MA交叉
        df["MA_cross_up"] = (df["MA20"] > df["MA60"]) & (df["MA20"].shift(1) <= df["MA60"].shift(1))
        df["MA_cross_down"] = (df["MA20"] < df["MA60"]) & (df["MA20"].shift(1) >= df["MA60"].shift(1))
        
        # 买入信号条件
        buy_condition = (
            df["MA_cross_up"] &
            (df["MACD_hist"] > 0) &
            (df["RSI"] > 50)
        )
        
        # 卖出信号条件
        sell_condition = (
            df["MA_cross_down"] &
            (df["MACD_hist"] < 0) &
            (df["RSI"] < 60)
        )
        
        # 标记信号
        df.loc[buy_condition, "signal"] = 1
        df.loc[buy_condition, "signal_type"] = "买入"
        
        df.loc[sell_condition, "signal"] = -1
        df.loc[sell_condition, "signal_type"] = "卖出"
        
        return df
    
    def get_latest_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        获取最新信号
        
        Args:
            df: 包含信号的 DataFrame
            
        Returns:
            最新信号的字典，如果没有信号则返回None
        """
        if df is None or df.empty:
            return None
        
        # 获取最后一行有信号的数据
        signals = df[df["signal"] != 0]
        if signals.empty:
            return None
        
        latest = signals.iloc[-1]
        
        return {
            "timestamp": latest.name,
            "signal": latest["signal"],
            "signal_type": latest["signal_type"],
            "close": latest["close"],
            "MA20": latest["MA20"],
            "MA60": latest["MA60"],
            "MACD_hist": latest["MACD_hist"],
            "RSI": latest["RSI"]
        }


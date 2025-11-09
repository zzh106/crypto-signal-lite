"""
EMA 信号检测模块
基于快慢EMA交叉判断趋势
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional


class EMASignal:
    """EMA 信号检测器"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均"""
        return series.ewm(span=period, adjust=False).mean()
    
    def detect_signal(self, df: pd.DataFrame) -> Dict:
        """
        检测EMA信号
        
        Args:
            df: 包含价格数据的DataFrame
            
        Returns:
            信号字典: {
                "signal": 1/-1/0,
                "strength": 0.0-1.0,
                "type": "买入"/"卖出"/"无",
                "details": {...}
            }
        """
        if df is None or df.empty or len(df) < self.slow_period:
            return {
                "signal": 0,
                "strength": 0.0,
                "type": "无",
                "details": {}
            }
        
        close = df["close"]
        
        # 计算EMA
        ema_fast = self.calculate_ema(close, self.fast_period)
        ema_slow = self.calculate_ema(close, self.slow_period)
        
        # 获取最新值
        latest_fast = ema_fast.iloc[-1]
        latest_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2] if len(ema_fast) > 1 else latest_fast
        prev_slow = ema_slow.iloc[-2] if len(ema_slow) > 1 else latest_slow
        
        # 判断交叉
        cross_up = (latest_fast > latest_slow) and (prev_fast <= prev_slow)
        cross_down = (latest_fast < latest_slow) and (prev_fast >= prev_slow)
        
        # 计算信号强度（基于EMA差距和趋势）
        ema_diff = abs(latest_fast - latest_slow) / latest_slow if latest_slow > 0 else 0
        trend_strength = abs(ema_fast.diff().iloc[-1]) / close.iloc[-1] if close.iloc[-1] > 0 else 0
        
        strength = min(1.0, (ema_diff * 10 + trend_strength * 100))
        
        if cross_up:
            return {
                "signal": 1,
                "strength": strength,
                "type": "买入",
                "details": {
                    "ema_fast": float(latest_fast),
                    "ema_slow": float(latest_slow),
                    "cross_type": "上穿",
                    "price": float(close.iloc[-1])
                }
            }
        elif cross_down:
            return {
                "signal": -1,
                "strength": strength,
                "type": "卖出",
                "details": {
                    "ema_fast": float(latest_fast),
                    "ema_slow": float(latest_slow),
                    "cross_type": "下穿",
                    "price": float(close.iloc[-1])
                }
            }
        else:
            # 无交叉，但可以判断趋势方向
            if latest_fast > latest_slow:
                trend_signal = 1
                trend_type = "多头"
            else:
                trend_signal = -1
                trend_type = "空头"
            
            return {
                "signal": 0,
                "strength": strength * 0.5,  # 无交叉时强度减半
                "type": f"趋势{trend_type}",
                "details": {
                    "ema_fast": float(latest_fast),
                    "ema_slow": float(latest_slow),
                    "trend": trend_type,
                    "price": float(close.iloc[-1])
                }
            }


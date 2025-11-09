"""
MACD 信号检测模块
"""
import pandas as pd
from typing import Dict


class MACDSignal:
    """MACD 信号检测器"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均"""
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, series: pd.Series) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        ema_fast = self.calculate_ema(series, self.fast)
        ema_slow = self.calculate_ema(series, self.slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, self.signal)
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def detect_signal(self, df: pd.DataFrame) -> Dict:
        """
        检测MACD信号
        
        Returns:
            信号字典
        """
        if df is None or df.empty or len(df) < self.slow:
            return {
                "signal": 0,
                "strength": 0.0,
                "type": "无",
                "details": {}
            }
        
        close = df["close"]
        macd_data = self.calculate_macd(close)
        
        macd = macd_data["macd"]
        signal_line = macd_data["signal"]
        histogram = macd_data["histogram"]
        
        # 获取最新值
        latest_macd = macd.iloc[-1]
        latest_signal = signal_line.iloc[-1]
        latest_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2] if len(histogram) > 1 else latest_hist
        
        # 判断交叉
        cross_up = (latest_hist > 0) and (prev_hist <= 0)
        cross_down = (latest_hist < 0) and (prev_hist >= 0)
        
        # 计算信号强度（基于MACD柱的大小和趋势）
        hist_abs = abs(latest_hist)
        hist_max = abs(histogram).max() if len(histogram) > 0 else 1
        strength = min(1.0, hist_abs / hist_max if hist_max > 0 else 0)
        
        # 增强强度计算（考虑MACD和信号线的位置）
        if abs(latest_macd) > 0:
            macd_strength = abs(latest_macd - latest_signal) / abs(latest_macd)
            strength = (strength + macd_strength) / 2
        
        if cross_up:
            return {
                "signal": 1,
                "strength": strength,
                "type": "买入",
                "details": {
                    "macd": float(latest_macd),
                    "signal": float(latest_signal),
                    "histogram": float(latest_hist),
                    "cross_type": "柱状图上穿",
                    "price": float(close.iloc[-1])
                }
            }
        elif cross_down:
            return {
                "signal": -1,
                "strength": strength,
                "type": "卖出",
                "details": {
                    "macd": float(latest_macd),
                    "signal": float(latest_signal),
                    "histogram": float(latest_hist),
                    "cross_type": "柱状图下穿",
                    "price": float(close.iloc[-1])
                }
            }
        else:
            # 无交叉，判断趋势
            if latest_hist > 0:
                trend = "多头"
                trend_signal = 1
            else:
                trend = "空头"
                trend_signal = -1
            
            return {
                "signal": 0,
                "strength": strength * 0.5,
                "type": f"趋势{trend}",
                "details": {
                    "macd": float(latest_macd),
                    "signal": float(latest_signal),
                    "histogram": float(latest_hist),
                    "trend": trend,
                    "price": float(close.iloc[-1])
                }
            }


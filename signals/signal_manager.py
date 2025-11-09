"""
信号管理器 - 综合多个指标生成最终信号
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from signals.ema_signal import EMASignal
from signals.macd_signal import MACDSignal
from signals.kdj_signal import KDJSignal


class SignalManager:
    """信号管理器 - 综合多个技术指标"""
    
    def __init__(self, config: dict):
        self.config = config
        indicator_config = config.get("signals", {}).get("indicators", {})
        
        # 初始化各个信号检测器
        ema_config = indicator_config.get("ema", {})
        self.ema_signal = EMASignal(
            fast_period=ema_config.get("fast", 12),
            slow_period=ema_config.get("slow", 26)
        )
        
        macd_config = indicator_config.get("macd", {})
        self.macd_signal = MACDSignal(
            fast=macd_config.get("fast", 12),
            slow=macd_config.get("slow", 26),
            signal=macd_config.get("signal", 9)
        )
        
        kdj_config = indicator_config.get("kdj", {})
        self.kdj_signal = KDJSignal(
            period=kdj_config.get("period", 9),
            k_period=kdj_config.get("k_period", 3),
            d_period=kdj_config.get("d_period", 3)
        )
        
        # 信号强度阈值
        signal_config = config.get("signals", {})
        self.strong_threshold = signal_config.get("strong_threshold", 0.8)
        self.medium_threshold = signal_config.get("medium_threshold", 0.6)
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        综合分析，生成最终信号
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            最终信号字典: {
                "signal": 1/-1/0,
                "strength": 0.0-1.0,
                "level": "strong"/"medium"/"weak"/"none",
                "type": "买入"/"卖出"/"无",
                "indicators": {
                    "ema": {...},
                    "macd": {...},
                    "kdj": {...}
                },
                "timestamp": datetime,
                "price": float
            }
        """
        if df is None or df.empty:
            return self._empty_signal()
        
        # 获取各个指标的信号
        ema_result = self.ema_signal.detect_signal(df)
        macd_result = self.macd_signal.detect_signal(df)
        kdj_result = self.kdj_signal.detect_signal(df)
        
        # 综合判断
        signals = [ema_result, macd_result, kdj_result]
        
        # 统计买入和卖出信号数量
        buy_count = sum(1 for s in signals if s["signal"] == 1)
        sell_count = sum(1 for s in signals if s["signal"] == -1)
        
        # 计算平均强度
        avg_strength = sum(s["strength"] for s in signals) / len(signals) if signals else 0
        
        # 判断最终信号
        if buy_count >= 2:  # 至少2个指标看多
            final_signal = 1
            signal_type = "买入"
        elif sell_count >= 2:  # 至少2个指标看空
            final_signal = -1
            signal_type = "卖出"
        elif buy_count == 1 and sell_count == 0:
            final_signal = 1
            signal_type = "买入（弱）"
        elif sell_count == 1 and buy_count == 0:
            final_signal = -1
            signal_type = "卖出（弱）"
        else:
            final_signal = 0
            signal_type = "无"
        
        # 确定信号级别
        if final_signal != 0:
            if avg_strength >= self.strong_threshold:
                level = "strong"
            elif avg_strength >= self.medium_threshold:
                level = "medium"
            else:
                level = "weak"
        else:
            level = "none"
        
        return {
            "signal": final_signal,
            "strength": avg_strength,
            "level": level,
            "type": signal_type,
            "indicators": {
                "ema": ema_result,
                "macd": macd_result,
                "kdj": kdj_result
            },
            "timestamp": datetime.now(),
            "price": float(df["close"].iloc[-1]),
            "consensus": {
                "buy_count": buy_count,
                "sell_count": sell_count,
                "total_indicators": len(signals)
            }
        }
    
    def _empty_signal(self) -> Dict:
        """返回空信号"""
        return {
            "signal": 0,
            "strength": 0.0,
            "level": "none",
            "type": "无",
            "indicators": {},
            "timestamp": datetime.now(),
            "price": 0.0,
            "consensus": {
                "buy_count": 0,
                "sell_count": 0,
                "total_indicators": 0
            }
        }
    
    def should_notify(self, signal_result: Dict, min_level: str = "medium") -> bool:
        """
        判断是否应该发送通知
        
        Args:
            signal_result: 信号结果
            min_level: 最小通知级别
            
        Returns:
            是否应该通知
        """
        if signal_result["signal"] == 0:
            return False
        
        level_order = {"none": 0, "weak": 1, "medium": 2, "strong": 3}
        signal_level = level_order.get(signal_result["level"], 0)
        min_level_value = level_order.get(min_level, 1)
        
        return signal_level >= min_level_value


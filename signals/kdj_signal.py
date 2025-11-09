"""
KDJ 信号检测模块
"""
import pandas as pd
import numpy as np
from typing import Dict


class KDJSignal:
    """KDJ 信号检测器"""
    
    def __init__(self, period: int = 9, k_period: int = 3, d_period: int = 3):
        self.period = period
        self.k_period = k_period
        self.d_period = d_period
    
    def calculate_kdj(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            df: 包含high, low, close的DataFrame
            
        Returns:
            K, D, J 序列
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        # 计算RSV
        lowest_low = low.rolling(window=self.period).min()
        highest_high = high.rolling(window=self.period).max()
        
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        rsv = rsv.fillna(50)  # 处理NaN
        
        # 计算K值（RSV的EMA）
        k = rsv.ewm(alpha=1/self.k_period, adjust=False).mean()
        
        # 计算D值（K的EMA）
        d = k.ewm(alpha=1/self.d_period, adjust=False).mean()
        
        # 计算J值
        j = 3 * k - 2 * d
        
        return {
            "k": k,
            "d": d,
            "j": j
        }
    
    def detect_signal(self, df: pd.DataFrame) -> Dict:
        """
        检测KDJ信号
        
        Returns:
            信号字典
        """
        if df is None or df.empty or len(df) < self.period:
            return {
                "signal": 0,
                "strength": 0.0,
                "type": "无",
                "details": {}
            }
        
        kdj_data = self.calculate_kdj(df)
        k = kdj_data["k"]
        d = kdj_data["d"]
        j = kdj_data["j"]
        
        # 获取最新值
        latest_k = k.iloc[-1]
        latest_d = d.iloc[-1]
        latest_j = j.iloc[-1]
        prev_k = k.iloc[-2] if len(k) > 1 else latest_k
        prev_d = d.iloc[-2] if len(d) > 1 else latest_d
        
        # 判断交叉
        cross_up = (latest_k > latest_d) and (prev_k <= prev_d)
        cross_down = (latest_k < latest_d) and (prev_k >= prev_d)
        
        # 计算信号强度
        kd_diff = abs(latest_k - latest_d)
        strength = min(1.0, kd_diff / 50.0)  # 归一化到0-1
        
        # 超买超卖判断
        oversold = latest_k < 20 and latest_d < 20
        overbought = latest_k > 80 and latest_d > 80
        
        if cross_up and oversold:
            # 金叉 + 超卖 = 强烈买入信号
            return {
                "signal": 1,
                "strength": min(1.0, strength + 0.3),
                "type": "买入",
                "details": {
                    "k": float(latest_k),
                    "d": float(latest_d),
                    "j": float(latest_j),
                    "cross_type": "金叉",
                    "position": "超卖区域",
                    "price": float(df["close"].iloc[-1])
                }
            }
        elif cross_down and overbought:
            # 死叉 + 超买 = 强烈卖出信号
            return {
                "signal": -1,
                "strength": min(1.0, strength + 0.3),
                "type": "卖出",
                "details": {
                    "k": float(latest_k),
                    "d": float(latest_d),
                    "j": float(latest_j),
                    "cross_type": "死叉",
                    "position": "超买区域",
                    "price": float(df["close"].iloc[-1])
                }
            }
        elif cross_up:
            return {
                "signal": 1,
                "strength": strength,
                "type": "买入",
                "details": {
                    "k": float(latest_k),
                    "d": float(latest_d),
                    "j": float(latest_j),
                    "cross_type": "金叉",
                    "price": float(df["close"].iloc[-1])
                }
            }
        elif cross_down:
            return {
                "signal": -1,
                "strength": strength,
                "type": "卖出",
                "details": {
                    "k": float(latest_k),
                    "d": float(latest_d),
                    "j": float(latest_j),
                    "cross_type": "死叉",
                    "price": float(df["close"].iloc[-1])
                }
            }
        else:
            # 无交叉，判断位置
            if oversold:
                position = "超卖"
                trend_signal = 1
            elif overbought:
                position = "超买"
                trend_signal = -1
            else:
                position = "中性"
                trend_signal = 0
            
            return {
                "signal": 0,
                "strength": strength * 0.3,
                "type": f"位置{position}",
                "details": {
                    "k": float(latest_k),
                    "d": float(latest_d),
                    "j": float(latest_j),
                    "position": position,
                    "price": float(df["close"].iloc[-1])
                }
            }


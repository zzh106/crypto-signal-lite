"""
数据获取模块 - 从 Binance API 获取K线数据
"""
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional


class BinanceDataFetcher:
    """Binance 数据获取器"""
    
    BASE_URL = "https://api.binance.com/api/v3/klines"
    
    def __init__(self, symbol: str = "ARUSDT"):
        self.symbol = symbol
    
    def fetch_klines(self, interval: str, limit: int = 500) -> pd.DataFrame:
        """
        获取K线数据
        
        Args:
            interval: 时间周期 (1d, 1w, 1h等)
            limit: 获取数量，默认500
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        params = {
            "symbol": self.symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise ValueError(f"No data returned for {self.symbol} {interval}")
            
            # 转换为 DataFrame
            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])
            
            # 转换数据类型
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            
            # 选择需要的列并重命名
            df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
            df.set_index("timestamp", inplace=True)
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch data from Binance: {e}")
        except Exception as e:
            raise ValueError(f"Error processing data: {e}")
    
    def fetch_multiple_intervals(self, intervals: List[str], limit: int = 500) -> Dict[str, pd.DataFrame]:
        """
        获取多个周期的数据
        
        Args:
            intervals: 时间周期列表
            limit: 获取数量
            
        Returns:
            字典，key为周期，value为DataFrame
        """
        result = {}
        for interval in intervals:
            print(f"📥 正在获取 {self.symbol} {interval} 数据...")
            try:
                df = self.fetch_klines(interval, limit)
                result[interval] = df
                print(f"✅ 成功获取 {len(df)} 根K线数据")
            except Exception as e:
                print(f"❌ 获取 {interval} 数据失败: {e}")
                result[interval] = None
        
        return result


"""
通知推送模块 - 支持 Server酱
"""
import requests
from typing import Optional
from datetime import datetime


class Notifier:
    """通知推送器"""
    
    def __init__(self, method: str = "serverchan", key: Optional[str] = None):
        self.method = method
        self.key = key
    
    def send_serverchan(self, title: str, content: str) -> bool:
        """
        发送 Server酱 通知
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            是否发送成功
        """
        if not self.key or self.key == "your_serverchan_key_here":
            print("⚠️  Server酱 key 未配置，跳过推送")
            return False
        
        url = f"https://sctapi.ftqq.com/{self.key}.send"
        
        data = {
            "title": title,
            "desp": content
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ Server酱推送成功")
                return True
            else:
                print(f"❌ Server酱推送失败: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Server酱推送异常: {e}")
            return False
    
    def notify(self, title: str, content: str) -> bool:
        """
        发送通知（根据配置的方法）
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            是否发送成功
        """
        if self.method == "serverchan":
            return self.send_serverchan(title, content)
        else:
            # 默认只打印
            print(f"\n📢 {title}")
            print(f"{content}\n")
            return True
    
    def notify_signal(self, symbol: str, interval: str, signal_info: dict) -> bool:
        """
        发送交易信号通知
        
        Args:
            symbol: 交易对
            interval: 周期
            signal_info: 信号信息字典
            
        Returns:
            是否发送成功
        """
        signal_type = signal_info.get("signal_type", "")
        close_price = signal_info.get("close", 0)
        timestamp = signal_info.get("timestamp", datetime.now())
        
        title = f"📈 {symbol} {signal_type}信号 | {interval}"
        content = f"""
**交易对**: {symbol}
**周期**: {interval}
**信号类型**: {signal_type}
**当前价格**: {close_price:.4f}
**时间**: {timestamp}

**技术指标**:
- MA20: {signal_info.get('MA20', 0):.4f}
- MA60: {signal_info.get('MA60', 0):.4f}
- MACD柱: {signal_info.get('MACD_hist', 0):.4f}
- RSI: {signal_info.get('RSI', 0):.2f}
"""
        
        return self.notify(title, content)


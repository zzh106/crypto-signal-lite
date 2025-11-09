"""
Server酱 推送模块
"""
import requests
from typing import Optional, Dict
from datetime import datetime


class ServerChanNotifier:
    """Server酱通知器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sctapi.ftqq.com"
    
    def send(self, title: str, content: str, desp: Optional[str] = None) -> bool:
        """
        发送Server酱通知
        
        Args:
            title: 标题
            content: 内容（Markdown格式）
            desp: 描述（可选）
            
        Returns:
            是否发送成功
        """
        if not self.api_key or self.api_key == "your_serverchan_key_here":
            print("⚠️  Server酱 key 未配置，跳过推送")
            return False
        
        url = f"{self.base_url}/{self.api_key}.send"
        
        data = {
            "title": title,
            "desp": content
        }
        
        if desp:
            data["desp"] = f"{desp}\n\n{content}"
        
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
    
    def send_signal(self, symbol: str, signal_result: Dict) -> bool:
        """
        发送交易信号通知
        
        Args:
            symbol: 交易对
            signal_result: 信号结果字典
            
        Returns:
            是否发送成功
        """
        signal_type = signal_result.get("type", "无")
        level = signal_result.get("level", "none")
        strength = signal_result.get("strength", 0.0)
        price = signal_result.get("price", 0.0)
        timestamp = signal_result.get("timestamp", datetime.now())
        
        # 信号级别图标
        level_icons = {
            "strong": "🔥",
            "medium": "⚡",
            "weak": "💡",
            "none": "📊"
        }
        icon = level_icons.get(level, "📊")
        
        title = f"{icon} {symbol} {signal_type}信号 | {level.upper()}"
        
        # 构建内容
        content = f"""## 📈 交易信号通知

**交易对**: {symbol}
**信号类型**: {signal_type}
**信号强度**: {strength:.2%}
**信号级别**: {level.upper()}
**当前价格**: ${price:.4f}
**时间**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

### 📊 指标详情

"""
        
        indicators = signal_result.get("indicators", {})
        consensus = signal_result.get("consensus", {})
        
        # EMA指标
        if "ema" in indicators:
            ema_info = indicators["ema"]
            content += f"**EMA**: {ema_info.get('type', '无')} (强度: {ema_info.get('strength', 0):.2%})\n"
            if "details" in ema_info:
                details = ema_info["details"]
                content += f"  - EMA快线: ${details.get('ema_fast', 0):.4f}\n"
                content += f"  - EMA慢线: ${details.get('ema_slow', 0):.4f}\n"
        
        # MACD指标
        if "macd" in indicators:
            macd_info = indicators["macd"]
            content += f"**MACD**: {macd_info.get('type', '无')} (强度: {macd_info.get('strength', 0):.2%})\n"
            if "details" in macd_info:
                details = macd_info["details"]
                content += f"  - MACD柱: {details.get('histogram', 0):.4f}\n"
        
        # KDJ指标
        if "kdj" in indicators:
            kdj_info = indicators["kdj"]
            content += f"**KDJ**: {kdj_info.get('type', '无')} (强度: {kdj_info.get('strength', 0):.2%})\n"
            if "details" in kdj_info:
                details = kdj_info["details"]
                content += f"  - K值: {details.get('k', 0):.2f}\n"
                content += f"  - D值: {details.get('d', 0):.2f}\n"
        
        content += f"\n### 🎯 指标共识\n"
        content += f"看多指标: {consensus.get('buy_count', 0)}/{consensus.get('total_indicators', 0)}\n"
        content += f"看空指标: {consensus.get('sell_count', 0)}/{consensus.get('total_indicators', 0)}\n"
        
        content += f"\n---\n"
        content += f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return self.send(title, content)
    
    def send_daily_report(self, report_data: Dict) -> bool:
        """
        发送每日报告
        
        Args:
            report_data: 报告数据字典
            
        Returns:
            是否发送成功
        """
        title = f"📊 每日交易信号报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""## 📈 每日交易信号汇总

**报告日期**: {datetime.now().strftime('%Y-%m-%d')}

### 📊 今日信号统计

"""
        
        for symbol, data in report_data.items():
            content += f"**{symbol}**\n"
            content += f"- 信号数: {data.get('signal_count', 0)}\n"
            content += f"- 最新价格: ${data.get('latest_price', 0):.4f}\n"
            content += f"- 最新信号: {data.get('latest_signal', '无')}\n"
            content += f"\n"
        
        content += f"---\n"
        content += f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return self.send(title, content)


"""
主程序 - crypto-signal-lite
分析 AR/USDT 交易信号
"""
import yaml
import schedule
import time
from datetime import datetime
from pathlib import Path

from app.fetch_data import OKXDataFetcher
from app.indicators import IndicatorCalculator
from app.notifier import Notifier
from backtest import Backtester
from visualize import ChartVisualizer


class CryptoSignalLite:
    """Crypto Signal Lite 主类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.fetcher = OKXDataFetcher(symbol=self.config["symbol"])
        self.calculator = IndicatorCalculator()
        self.notifier = Notifier(
            method=self.config.get("notify", {}).get("method", "serverchan"),
            key=self.config.get("notify", {}).get("key")
        )
        self.visualizer = ChartVisualizer()
    
    def load_config(self) -> dict:
        """加载配置文件"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def analyze_interval(self, interval: str) -> dict:
        """
        分析单个周期的数据
        
        Args:
            interval: 时间周期
            
        Returns:
            分析结果字典
        """
        print(f"\n{'='*60}")
        print(f"📊 分析周期: {interval}")
        print(f"{'='*60}")
        
        # 1. 获取数据
        df = self.fetcher.fetch_klines(
            interval=interval,
            limit=self.config.get("data_limit", 500)
        )
        
        if df is None or df.empty:
            print(f"❌ 无法获取 {interval} 数据")
            return {}
        
        # 2. 计算技术指标
        print("🔢 计算技术指标...")
        df = self.calculator.calculate_indicators(df)
        
        # 3. 检测信号
        print("🔍 检测交易信号...")
        df = self.calculator.detect_signals(df)
        
        # 4. 获取最新信号
        latest_signal = self.calculator.get_latest_signal(df)
        
        # 5. 回测
        print("📈 运行历史回测...")
        backtester = Backtester(df)
        backtest_result = backtester.run_backtest()
        
        # 6. 可视化
        print("🎨 生成可视化图表...")
        chart_path = self.visualizer.create_candlestick_chart(
            df=df,
            symbol=self.config["symbol"],
            interval=interval
        )
        
        # 7. 输出结果
        result = {
            "interval": interval,
            "latest_signal": latest_signal,
            "backtest": backtest_result,
            "chart_path": chart_path,
            "data": df
        }
        
        return result
    
    def run(self):
        """运行一次完整分析"""
        print(f"\n{'='*60}")
        print(f"🚀 Crypto Signal Lite 启动")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"交易对: {self.config['symbol']}")
        print(f"{'='*60}\n")
        
        intervals = self.config.get("intervals", ["1d"])
        results = {}
        
        for interval in intervals:
            try:
                result = self.analyze_interval(interval)
                results[interval] = result
                
                # 打印最新信号
                if result.get("latest_signal"):
                    signal = result["latest_signal"]
                    print(f"\n📈 {self.config['symbol']} 触发{signal['signal_type']}信号 | {interval} | 收盘价 {signal['close']:.4f}")
                    
                    # 发送通知
                    self.notifier.notify_signal(
                        symbol=self.config["symbol"],
                        interval=interval,
                        signal_info=signal
                    )
                else:
                    print(f"\n⚠️  {self.config['symbol']} {interval} 当前无信号")
                
                # 打印回测结果
                backtest = result.get("backtest", {})
                if backtest:
                    print(f"📊 历史胜率: {backtest.get('win_rate', 0):.1f}% | "
                          f"平均收益: {backtest.get('avg_return', 0):+.2f}% | "
                          f"最大回撤: {backtest.get('max_drawdown', 0):.2f}%")
                    
                    # 打印最近12个月交易记录
                    backtester = Backtester(result.get("data"))
                    backtester.print_recent_trades_table(months=12)
                
                # 打印图表路径
                chart_path = result.get("chart_path")
                if chart_path:
                    print(f"📊 可视化图表已保存至: {chart_path}")
                
            except Exception as e:
                print(f"❌ 分析 {interval} 时出错: {e}")
                import traceback
                traceback.print_exc()
        
        return results
    
    def run_scheduled(self):
        """运行定时任务"""
        # 每天北京时间 09:00 运行（UTC+8，即 UTC 01:00）
        schedule.every().day.at("01:00").do(self.run)
        
        print("⏰ 定时任务已启动，每天 UTC 01:00 (北京时间 09:00) 运行")
        print("按 Ctrl+C 退出\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n👋 程序已退出")


def main():
    """主函数"""
    import sys
    
    # 检查是否使用定时模式
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        app = CryptoSignalLite()
        app.run_scheduled()
    else:
        # 立即运行一次
        app = CryptoSignalLite()
        app.run()


if __name__ == "__main__":
    main()


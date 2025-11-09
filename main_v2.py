"""
量化信号监控系统 - 主程序
每4小时运行一次信号检测，每日生成报告
"""
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from app.fetch_data import OKXDataFetcher
from signals.signal_manager import SignalManager
from notifier.serverchan_push import ServerChanNotifier
from position_manager import PositionManager
from logger import SignalLogger


class QuantSignalSystem:
    """量化信号监控系统"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 初始化组件
        self.logger = SignalLogger(
            log_file=self.config["logging"]["file"],
            level=self.config["logging"]["level"],
            max_size_mb=self.config["logging"]["max_size_mb"],
            backup_count=self.config["logging"]["backup_count"]
        )
        
        self.fetcher = OKXDataFetcher()
        self.signal_manager = SignalManager(self.config)
        
        # 通知器
        notify_config = self.config.get("notify", {})
        if notify_config.get("method") == "serverchan" and notify_config.get("serverchan", {}).get("enable"):
            self.notifier = ServerChanNotifier(
                api_key=notify_config["serverchan"]["key"]
            )
        else:
            self.notifier = None
        
        # 持仓管理器
        max_holding_days = self.config["signals"]["max_holding_days"]
        self.position_manager = PositionManager(max_holding_days=max_holding_days)
        
        self.logger.log_info("="*60)
        self.logger.log_info("🚀 量化信号监控系统启动")
        self.logger.log_info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log_info("="*60)
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def check_signal(self, symbol: str) -> Dict:
        """
        检测单个交易对的信号
        
        Args:
            symbol: 交易对（如 "AR/USDT"）
            
        Returns:
            检测结果字典
        """
        self.logger.log_info(f"\n{'='*60}")
        self.logger.log_info(f"📊 检测 {symbol} 交易信号")
        self.logger.log_info(f"{'='*60}")
        
        try:
            # 1. 获取数据（使用4小时线进行信号检测）
            intervals = self.config["data"]["intervals"]
            signal_interval = "4h"  # 使用4小时线
            
            self.logger.log_info(f"📥 获取 {symbol} {signal_interval} 数据...")
            df = self.fetcher.fetch_klines(symbol, signal_interval, self.config["data"]["limit"])
            
            if df is None or df.empty:
                self.logger.log_error(f"❌ 无法获取 {symbol} 数据")
                return {}
            
            self.logger.log_info(f"✅ 获取到 {len(df)} 根K线数据")
            
            # 2. 信号分析
            self.logger.log_info("🔍 分析交易信号...")
            signal_result = self.signal_manager.analyze(df)
            
            # 3. 记录信号
            self.logger.log_signal(symbol, signal_result)
            
            # 4. 检查是否需要通知
            min_level = self.config["notify"].get("min_level", "medium")
            should_notify = self.signal_manager.should_notify(signal_result, min_level)
            
            if should_notify and self.notifier:
                self.logger.log_info("📤 发送信号通知...")
                self.notifier.send_signal(symbol, signal_result)
            
            # 5. 处理持仓
            current_price = signal_result.get("price", 0.0)
            
            # 检查是否有未平仓持仓（先获取，后面会用到）
            open_positions = self.position_manager.get_open_positions(symbol)
            
            # 检查强制平仓
            forced_closed = self.position_manager.check_forced_close(symbol, current_price)
            for position in forced_closed:
                self.logger.log_position(
                    "forced_close", symbol,
                    exit_price=position["exit_price"],
                    profit_loss=position["profit_loss"],
                    profit_loss_pct=position["profit_loss_pct"]
                )
                if self.notifier:
                    self.notifier.send(
                        f"⚠️ {symbol} 强制平仓",
                        f"持仓超过{self.config['signals']['max_holding_days']}天，已强制平仓\n"
                        f"入场价: ${position['entry_price']:.4f}\n"
                        f"出场价: ${position['exit_price']:.4f}\n"
                        f"盈亏: ${position['profit_loss']:.2f} ({position['profit_loss_pct']:+.2f}%)"
                    )
            
            # 重新获取（强制平仓后可能有变化）
            open_positions = self.position_manager.get_open_positions(symbol)
            
            # 6. 处理新信号（开仓/平仓）
            signal = signal_result.get("signal", 0)
            signal_type = signal_result.get("type", "无")
            signal_level = signal_result.get("level", "none")
            signal_strength = signal_result.get("strength", 0.0)
            
            if signal != 0:
                
                if signal == 1:  # 买入信号
                    if not open_positions:  # 没有持仓，开仓
                        position_id = self.position_manager.open_position(
                            symbol, "买入", current_price, signal_strength, signal_level
                        )
                        self.logger.log_position(
                            "open", symbol,
                            signal_type="买入",
                            entry_price=current_price,
                            strength=signal_strength
                        )
                    # 如果有持仓，继续持有
                
                elif signal == -1:  # 卖出信号
                    if open_positions:  # 有持仓，平仓
                        closed = self.position_manager.close_position(symbol, current_price)
                        for position in closed:
                            self.logger.log_position(
                                "close", symbol,
                                exit_price=position["exit_price"],
                                profit_loss=position["profit_loss"],
                                profit_loss_pct=position["profit_loss_pct"]
                            )
                            if self.notifier:
                                self.notifier.send(
                                    f"💰 {symbol} 平仓通知",
                                    f"信号触发平仓\n"
                                    f"入场价: ${position['entry_price']:.4f}\n"
                                    f"出场价: ${position['exit_price']:.4f}\n"
                                    f"盈亏: ${position['profit_loss']:.2f} ({position['profit_loss_pct']:+.2f}%)\n"
                                    f"持仓天数: {position['holding_days']}天"
                                )
            
            return {
                "symbol": symbol,
                "signal_result": signal_result,
                "current_price": current_price,
                "open_positions": len(open_positions),
                "forced_closed": len(forced_closed)
            }
            
        except Exception as e:
            self.logger.log_error(f"❌ 检测 {symbol} 信号时出错: {e}", exc_info=True)
            return {}
    
    def run_signal_check(self):
        """运行一次信号检测（每4小时）"""
        self.logger.log_info("\n" + "="*60)
        self.logger.log_info("🔄 开始信号检测任务")
        self.logger.log_info("="*60)
        
        symbols = self.config["symbols"]
        results = {}
        
        for symbol in symbols:
            result = self.check_signal(symbol)
            if result:
                results[symbol] = result
        
        self.logger.log_info("\n" + "="*60)
        self.logger.log_info("✅ 信号检测任务完成")
        self.logger.log_info("="*60)
        
        return results
    
    def generate_daily_report(self):
        """生成每日报告"""
        self.logger.log_info("\n" + "="*60)
        self.logger.log_info("📊 生成每日报告")
        self.logger.log_info("="*60)
        
        symbols = self.config["symbols"]
        report_data = {}
        
        for symbol in symbols:
            # 获取统计信息
            stats = self.position_manager.get_statistics(symbol)
            open_positions = self.position_manager.get_open_positions(symbol)
            
            # 获取最新价格
            try:
                df = self.fetcher.fetch_klines(symbol, "1d", 1)
                latest_price = float(df["close"].iloc[-1]) if not df.empty else 0.0
            except:
                latest_price = 0.0
            
            # 获取最新信号
            try:
                df = self.fetcher.fetch_klines(symbol, "4h", 100)
                signal_result = self.signal_manager.analyze(df)
                latest_signal = signal_result.get("type", "无")
            except:
                latest_signal = "无"
            
            report_data[symbol] = {
                "latest_price": latest_price,
                "latest_signal": latest_signal,
                "signal_count": stats["total_trades"],
                "open_positions": len(open_positions),
                "win_rate": stats["win_rate"],
                "total_profit": stats["total_profit"]
            }
        
        # 发送报告
        if self.notifier:
            self.notifier.send_daily_report(report_data)
        
        self.logger.log_info("✅ 每日报告已生成并发送")
        
        return report_data


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # 生成日报
        system = QuantSignalSystem()
        system.generate_daily_report()
    else:
        # 信号检测
        system = QuantSignalSystem()
        system.run_signal_check()


if __name__ == "__main__":
    main()


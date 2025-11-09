"""
历史回测模块 - 计算信号胜率和收益率
"""
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class Backtester:
    """回测器"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.signals = []
        self.trades = []
    
    def run_backtest(self) -> Dict:
        """
        运行回测
        
        Returns:
            回测结果字典
        """
        if self.df is None or self.df.empty:
            return {}
        
        # 获取所有信号
        signals_df = self.df[self.df["signal"] != 0].copy()
        
        if signals_df.empty:
            return {
                "total_signals": 0,
                "win_rate": 0,
                "avg_return": 0,
                "max_drawdown": 0,
                "trades": []
            }
        
        trades = []
        position = None  # None: 无持仓, {"entry_price": float, "entry_date": datetime}
        
        for idx, row in signals_df.iterrows():
            signal = row["signal"]
            price = row["close"]
            date = idx
            
            if signal == 1:  # 买入信号
                if position is None:
                    position = {
                        "entry_price": price,
                        "entry_date": date,
                        "signal_type": "买入"
                    }
            elif signal == -1:  # 卖出信号
                if position is not None:
                    # 计算持仓期间的收益
                    exit_price = price
                    entry_price = position["entry_price"]
                    return_pct = ((exit_price - entry_price) / entry_price) * 100
                    
                    # 计算持仓期间的最高价和最低价
                    period_df = self.df[
                        (self.df.index >= position["entry_date"]) & 
                        (self.df.index <= date)
                    ]
                    
                    if not period_df.empty:
                        high_price = period_df["high"].max()
                        low_price = period_df["low"].min()
                        max_return = ((high_price - entry_price) / entry_price) * 100
                        max_drawdown = ((low_price - entry_price) / entry_price) * 100
                    else:
                        high_price = exit_price
                        low_price = entry_price
                        max_return = return_pct
                        max_drawdown = 0
                    
                    trade = {
                        "date": date,
                        "signal_type": position["signal_type"],
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "high_price": high_price,
                        "low_price": low_price,
                        "return_pct": return_pct,
                        "max_return": max_return,
                        "max_drawdown": max_drawdown,
                        "status": "✅" if return_pct > 0 else "❌"
                    }
                    trades.append(trade)
                    position = None
        
        # 如果最后还有持仓，用最新价格结算
        if position is not None and not self.df.empty:
            latest_price = self.df["close"].iloc[-1]
            entry_price = position["entry_price"]
            return_pct = ((latest_price - entry_price) / entry_price) * 100
            
            period_df = self.df[self.df.index >= position["entry_date"]]
            if not period_df.empty:
                high_price = period_df["high"].max()
                low_price = period_df["low"].min()
                max_return = ((high_price - entry_price) / entry_price) * 100
                max_drawdown = ((low_price - entry_price) / entry_price) * 100
            else:
                high_price = latest_price
                low_price = entry_price
                max_return = return_pct
                max_drawdown = 0
            
            trade = {
                "date": self.df.index[-1],
                "signal_type": position["signal_type"],
                "entry_price": entry_price,
                "exit_price": latest_price,
                "high_price": high_price,
                "low_price": low_price,
                "return_pct": return_pct,
                "max_return": max_return,
                "max_drawdown": max_drawdown,
                "status": "✅" if return_pct > 0 else "❌"
            }
            trades.append(trade)
        
        # 计算统计指标
        if trades:
            returns = [t["return_pct"] for t in trades]
            wins = [r for r in returns if r > 0]
            
            win_rate = (len(wins) / len(returns)) * 100 if returns else 0
            avg_return = sum(returns) / len(returns) if returns else 0
            max_drawdown = min([t["max_drawdown"] for t in trades]) if trades else 0
        else:
            win_rate = 0
            avg_return = 0
            max_drawdown = 0
        
        return {
            "total_signals": len(signals_df),
            "total_trades": len(trades),
            "win_rate": win_rate,
            "avg_return": avg_return,
            "max_drawdown": max_drawdown,
            "trades": trades
        }
    
    def get_recent_trades(self, months: int = 12) -> List[Dict]:
        """
        获取最近N个月的交易记录
        
        Args:
            months: 月数
            
        Returns:
            交易记录列表
        """
        if not self.trades:
            result = self.run_backtest()
            self.trades = result.get("trades", [])
        
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        recent_trades = [
            t for t in self.trades 
            if isinstance(t["date"], pd.Timestamp) and t["date"].to_pydatetime() >= cutoff_date
        ]
        
        return recent_trades
    
    def print_backtest_summary(self):
        """打印回测摘要"""
        result = self.run_backtest()
        
        print("\n" + "="*60)
        print("📊 回测结果摘要")
        print("="*60)
        print(f"总信号数: {result['total_signals']}")
        print(f"总交易数: {result['total_trades']}")
        print(f"胜率: {result['win_rate']:.1f}%")
        print(f"平均收益率: {result['avg_return']:+.2f}%")
        print(f"最大回撤: {result['max_drawdown']:.2f}%")
        print("="*60 + "\n")
    
    def print_recent_trades_table(self, months: int = 12):
        """打印最近N个月的交易表格"""
        recent_trades = self.get_recent_trades(months)
        
        if not recent_trades:
            print(f"\n⚠️  最近 {months} 个月无交易记录\n")
            return
        
        print(f"\n📋 最近 {months} 个月交易记录")
        print("-"*80)
        print(f"{'日期':<12} {'信号':<6} {'入场价':<10} {'出场价':<10} {'最高价':<10} {'收益率':<10} {'状态':<6}")
        print("-"*80)
        
        for trade in recent_trades:
            date_str = str(trade["date"])[:10] if isinstance(trade["date"], pd.Timestamp) else str(trade["date"])
            print(
                f"{date_str:<12} "
                f"{trade['signal_type']:<6} "
                f"{trade['entry_price']:<10.4f} "
                f"{trade['exit_price']:<10.4f} "
                f"{trade['high_price']:<10.4f} "
                f"{trade['return_pct']:>+9.2f}% "
                f"{trade['status']:<6}"
            )
        
        print("-"*80 + "\n")


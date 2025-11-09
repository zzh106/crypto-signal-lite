"""
持仓管理器 - 跟踪交易信号、入场价、出场价和盈亏
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class PositionManager:
    """持仓管理器"""
    
    def __init__(self, data_file: str = "logs/positions.json", max_holding_days: int = 7):
        self.data_file = Path(data_file)
        self.max_holding_days = max_holding_days
        self.positions_file = self.data_file
        self.positions_file.parent.mkdir(parents=True, exist_ok=True)
        self.positions = self._load_positions()
    
    def _load_positions(self) -> Dict:
        """加载持仓数据"""
        if self.positions_file.exists():
            try:
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_positions(self):
        """保存持仓数据"""
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2, default=str)
    
    def open_position(self, symbol: str, signal_type: str, entry_price: float, 
                     signal_strength: float, signal_level: str) -> str:
        """
        开仓
        
        Args:
            symbol: 交易对
            signal_type: 信号类型（买入/卖出）
            entry_price: 入场价
            signal_strength: 信号强度
            signal_level: 信号级别
            
        Returns:
            持仓ID
        """
        position_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        position = {
            "id": position_id,
            "symbol": symbol,
            "signal_type": signal_type,
            "entry_price": entry_price,
            "entry_time": datetime.now().isoformat(),
            "exit_price": None,
            "exit_time": None,
            "signal_strength": signal_strength,
            "signal_level": signal_level,
            "status": "open",  # open, closed, forced_close
            "profit_loss": None,
            "profit_loss_pct": None,
            "holding_days": 0
        }
        
        if symbol not in self.positions:
            self.positions[symbol] = []
        
        self.positions[symbol].append(position)
        self._save_positions()
        
        return position_id
    
    def close_position(self, symbol: str, exit_price: float, 
                      position_id: Optional[str] = None, forced: bool = False) -> List[Dict]:
        """
        平仓
        
        Args:
            symbol: 交易对
            exit_price: 出场价
            position_id: 持仓ID（如果为None，则平掉所有未平仓）
            forced: 是否强制平仓
            
        Returns:
            已平仓的持仓列表
        """
        closed_positions = []
        
        if symbol not in self.positions:
            return closed_positions
        
        for position in self.positions[symbol]:
            if position["status"] != "open":
                continue
            
            if position_id and position["id"] != position_id:
                continue
            
            # 计算盈亏
            entry_price = position["entry_price"]
            if position["signal_type"] == "买入":
                profit_loss = exit_price - entry_price
                profit_loss_pct = (exit_price - entry_price) / entry_price * 100
            else:  # 卖出（做空）
                profit_loss = entry_price - exit_price
                profit_loss_pct = (entry_price - exit_price) / entry_price * 100
            
            # 更新持仓
            position["exit_price"] = exit_price
            position["exit_time"] = datetime.now().isoformat()
            position["status"] = "forced_close" if forced else "closed"
            position["profit_loss"] = profit_loss
            position["profit_loss_pct"] = profit_loss_pct
            
            # 计算持仓天数
            entry_time = datetime.fromisoformat(position["entry_time"])
            exit_time = datetime.fromisoformat(position["exit_time"])
            position["holding_days"] = (exit_time - entry_time).days
            
            closed_positions.append(position)
        
        self._save_positions()
        return closed_positions
    
    def check_forced_close(self, symbol: str, current_price: float) -> List[Dict]:
        """
        检查是否需要强制平仓（超过7天）
        
        Args:
            symbol: 交易对
            current_price: 当前价格
            
        Returns:
            被强制平仓的持仓列表
        """
        forced_closed = []
        
        if symbol not in self.positions:
            return forced_closed
        
        for position in self.positions[symbol]:
            if position["status"] != "open":
                continue
            
            entry_time = datetime.fromisoformat(position["entry_time"])
            holding_days = (datetime.now() - entry_time).days
            
            if holding_days >= self.max_holding_days:
                closed = self.close_position(symbol, current_price, position["id"], forced=True)
                forced_closed.extend(closed)
        
        return forced_closed
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        获取未平仓持仓
        
        Args:
            symbol: 交易对（如果为None，返回所有）
            
        Returns:
            未平仓持仓列表
        """
        open_positions = []
        
        symbols = [symbol] if symbol else self.positions.keys()
        
        for sym in symbols:
            if sym not in self.positions:
                continue
            
            for position in self.positions[sym]:
                if position["status"] == "open":
                    open_positions.append(position)
        
        return open_positions
    
    def get_statistics(self, symbol: Optional[str] = None) -> Dict:
        """
        获取统计信息
        
        Args:
            symbol: 交易对（如果为None，统计所有）
            
        Returns:
            统计字典
        """
        symbols = [symbol] if symbol else self.positions.keys()
        
        total_trades = 0
        closed_trades = 0
        open_trades = 0
        total_profit = 0.0
        win_trades = 0
        loss_trades = 0
        
        for sym in symbols:
            if sym not in self.positions:
                continue
            
            for position in self.positions[sym]:
                total_trades += 1
                
                if position["status"] == "open":
                    open_trades += 1
                else:
                    closed_trades += 1
                    if position["profit_loss"] is not None:
                        total_profit += position["profit_loss"]
                        if position["profit_loss"] > 0:
                            win_trades += 1
                        else:
                            loss_trades += 1
        
        win_rate = (win_trades / closed_trades * 100) if closed_trades > 0 else 0
        
        return {
            "total_trades": total_trades,
            "closed_trades": closed_trades,
            "open_trades": open_trades,
            "win_trades": win_trades,
            "loss_trades": loss_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "avg_profit_per_trade": total_profit / closed_trades if closed_trades > 0 else 0
        }


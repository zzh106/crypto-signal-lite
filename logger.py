"""
日志系统
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


class SignalLogger:
    """信号日志记录器"""
    
    def __init__(self, log_file: str = "logs/signal_log.txt", 
                 level: str = "INFO", max_size_mb: int = 10, backup_count: int = 5):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        self.logger = logging.getLogger("SignalLogger")
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 文件handler（带轮转）
            max_bytes = max_size_mb * 1024 * 1024
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_signal(self, symbol: str, signal_result: dict):
        """记录交易信号"""
        signal_type = signal_result.get("type", "无")
        level = signal_result.get("level", "none")
        strength = signal_result.get("strength", 0.0)
        price = signal_result.get("price", 0.0)
        
        self.logger.info(
            f"[信号] {symbol} | {signal_type} | 级别:{level} | 强度:{strength:.2%} | 价格:${price:.4f}"
        )
    
    def log_position(self, action: str, symbol: str, **kwargs):
        """记录持仓操作"""
        if action == "open":
            self.logger.info(
                f"[开仓] {symbol} | 类型:{kwargs.get('signal_type')} | "
                f"价格:${kwargs.get('entry_price', 0):.4f} | 强度:{kwargs.get('strength', 0):.2%}"
            )
        elif action == "close":
            self.logger.info(
                f"[平仓] {symbol} | 价格:${kwargs.get('exit_price', 0):.4f} | "
                f"盈亏:${kwargs.get('profit_loss', 0):.2f} ({kwargs.get('profit_loss_pct', 0):+.2f}%)"
            )
        elif action == "forced_close":
            self.logger.warning(
                f"[强制平仓] {symbol} | 持仓超过7天 | 价格:${kwargs.get('exit_price', 0):.4f}"
            )
    
    def log_error(self, message: str, exc_info=False):
        """记录错误"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)


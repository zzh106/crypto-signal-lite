"""
可视化模块 - 使用 Plotly 绘制K线图
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
import os


class ChartVisualizer:
    """图表可视化器"""
    
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_candlestick_chart(
        self, 
        df: pd.DataFrame, 
        symbol: str = "ARUSDT",
        interval: str = "1d",
        output_file: Optional[str] = None
    ) -> str:
        """
        创建K线图
        
        Args:
            df: 包含OHLCV和信号的DataFrame
            symbol: 交易对名称
            interval: 周期
            output_file: 输出文件名，默认自动生成
            
        Returns:
            输出文件路径
        """
        if df is None or df.empty:
            raise ValueError("DataFrame is empty")
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=("K线图 + MA", "MACD", "RSI")
        )
        
        # 1. K线图
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="K线"
            ),
            row=1, col=1
        )
        
        # MA20 和 MA60
        if "MA20" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["MA20"],
                    name="MA20",
                    line=dict(color="blue", width=1)
                ),
                row=1, col=1
            )
        
        if "MA60" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["MA60"],
                    name="MA60",
                    line=dict(color="orange", width=1)
                ),
                row=1, col=1
            )
        
        # 买入信号标记（绿色上三角）
        buy_signals = df[df["signal"] == 1]
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals["low"] * 0.98,  # 在K线下方一点
                    mode="markers",
                    name="买入信号",
                    marker=dict(
                        symbol="triangle-up",
                        size=12,
                        color="green",
                        line=dict(width=2, color="darkgreen")
                    )
                ),
                row=1, col=1
            )
        
        # 卖出信号标记（红色下三角）
        sell_signals = df[df["signal"] == -1]
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals["high"] * 1.02,  # 在K线上方一点
                    mode="markers",
                    name="卖出信号",
                    marker=dict(
                        symbol="triangle-down",
                        size=12,
                        color="red",
                        line=dict(width=2, color="darkred")
                    )
                ),
                row=1, col=1
            )
        
        # 2. MACD
        if "MACD" in df.columns and "MACD_hist" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["MACD"],
                    name="MACD",
                    line=dict(color="blue", width=1)
                ),
                row=2, col=1
            )
            
            if "MACD_signal" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["MACD_signal"],
                        name="Signal",
                        line=dict(color="red", width=1)
                    ),
                    row=2, col=1
                )
            
            # MACD柱状图
            colors = ["green" if x > 0 else "red" for x in df["MACD_hist"]]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["MACD_hist"],
                    name="MACD Hist",
                    marker_color=colors
                ),
                row=2, col=1
            )
        
        # 3. RSI
        if "RSI" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["RSI"],
                    name="RSI",
                    line=dict(color="purple", width=1)
                ),
                row=3, col=1
            )
            
            # RSI 超买超卖线
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
        
        # 更新布局
        fig.update_layout(
            title=f"{symbol} {interval} K线图 - 交易信号分析",
            xaxis_rangeslider_visible=False,
            height=900,
            showlegend=True,
            hovermode="x unified"
        )
        
        # 更新x轴
        fig.update_xaxes(title_text="时间", row=3, col=1)
        
        # 更新y轴标签
        fig.update_yaxes(title_text="价格", row=1, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        # 生成输出文件名
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"{symbol.lower()}_signal_chart.html")
        else:
            output_file = os.path.join(self.output_dir, output_file)
        
        # 保存图表
        fig.write_html(output_file)
        
        return output_file


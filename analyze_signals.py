#!/usr/bin/env python3
"""
分析过去3个月的交易信号
"""
from app.fetch_data import OKXDataFetcher
from app.indicators import IndicatorCalculator
from backtest import Backtester
import pandas as pd
from datetime import datetime, timedelta


def analyze_3months_signals():
    """分析过去3个月的交易信号"""
    print("="*70)
    print("📊 AR/USDT 过去3个月交易信号分析")
    print("="*70)
    print()
    
    # 获取数据（3个月约90根K线，OKX单次最多100根）
    fetcher = OKXDataFetcher('ARUSDT')
    print("📥 正在获取过去3个月的日线数据...")
    df = fetcher.fetch_klines('1d', 100)  # OKX最多100根
    
    print(f"✅ 获取到 {len(df)} 根K线数据")
    print(f"   数据范围: {df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
    print()
    
    # 计算技术指标
    print("🔢 计算技术指标...")
    calculator = IndicatorCalculator()
    df = calculator.calculate_indicators(df)
    
    # 显示最新指标
    latest = df.iloc[-1]
    print(f"\n📈 最新技术指标 (日期: {df.index[-1].strftime('%Y-%m-%d %H:%M')}):")
    print(f"   收盘价: ${latest['close']:.4f}")
    print(f"   最高价: ${latest['high']:.4f}")
    print(f"   最低价: ${latest['low']:.4f}")
    print(f"   MA20: ${latest['MA20']:.4f}")
    print(f"   MA60: ${latest['MA60']:.4f}")
    print(f"   MACD: {latest['MACD']:.4f}")
    print(f"   MACD柱: {latest['MACD_hist']:.4f}")
    print(f"   RSI: {latest['RSI']:.2f}")
    print()
    
    # 检测信号
    print("🔍 检测交易信号...")
    df = calculator.detect_signals(df)
    
    # 获取所有信号
    signals = df[df['signal'] != 0].copy()
    print(f"✅ 共检测到 {len(signals)} 个交易信号")
    print()
    
    if len(signals) > 0:
        print("="*70)
        print("📋 交易信号详细列表")
        print("="*70)
        print(f"{'日期':<12} {'信号':<6} {'价格':<10} {'MA20':<10} {'MA60':<10} {'MACD柱':<10} {'RSI':<8}")
        print("-"*70)
        
        for idx, row in signals.iterrows():
            date_str = idx.strftime('%Y-%m-%d')
            signal_type = row['signal_type']
            price = row['close']
            ma20 = row['MA20']
            ma60 = row['MA60']
            macd_hist = row['MACD_hist']
            rsi = row['RSI']
            
            print(f"{date_str:<12} {signal_type:<6} ${price:<9.4f} ${ma20:<9.4f} ${ma60:<9.4f} {macd_hist:<9.4f} {rsi:<8.2f}")
        
        print("="*70)
        print()
        
        # 获取最新信号
        latest_signal = signals.iloc[-1]
        print("🎯 最新交易信号:")
        print(f"   日期: {latest_signal.name.strftime('%Y-%m-%d')}")
        print(f"   信号类型: {latest_signal['signal_type']}")
        print(f"   价格: ${latest_signal['close']:.4f}")
        print(f"   MA20: ${latest_signal['MA20']:.4f}")
        print(f"   MA60: ${latest_signal['MA60']:.4f}")
        print(f"   MACD柱: {latest_signal['MACD_hist']:.4f}")
        print(f"   RSI: {latest_signal['RSI']:.2f}")
        print()
        
        # 分析信号质量
        print("📊 信号统计:")
        buy_signals = signals[signals['signal'] == 1]
        sell_signals = signals[signals['signal'] == -1]
        print(f"   买入信号数: {len(buy_signals)}")
        print(f"   卖出信号数: {len(sell_signals)}")
        
        if len(buy_signals) > 0:
            latest_buy = buy_signals.iloc[-1]
            print(f"   最近买入信号: {latest_buy.name.strftime('%Y-%m-%d')} @ ${latest_buy['close']:.4f}")
        if len(sell_signals) > 0:
            latest_sell = sell_signals.iloc[-1]
            print(f"   最近卖出信号: {latest_sell.name.strftime('%Y-%m-%d')} @ ${latest_sell['close']:.4f}")
        
    else:
        print("⚠️  过去3个月未检测到交易信号")
        print()
        print("💡 当前市场状态分析:")
        latest = df.iloc[-1]
        ma20 = latest['MA20']
        ma60 = latest['MA60']
        
        if pd.notna(ma20) and pd.notna(ma60):
            if ma20 > ma60:
                print("   ✅ MA20 > MA60 (短期均线在长期均线上方，趋势向上)")
            else:
                print("   ⚠️  MA20 < MA60 (短期均线在长期均线下方，趋势向下)")
            print(f"   均线差距: ${abs(ma20 - ma60):.4f} ({abs(ma20 - ma60) / ma60 * 100:.2f}%)")
        
        if pd.notna(latest['MACD_hist']):
            if latest['MACD_hist'] > 0:
                print("   ✅ MACD柱 > 0 (动能向上，多头力量较强)")
            else:
                print("   ⚠️  MACD柱 < 0 (动能向下，空头力量较强)")
        
        if pd.notna(latest['RSI']):
            rsi = latest['RSI']
            if rsi > 70:
                print(f"   ⚠️  RSI = {rsi:.2f} (超买区域，可能回调)")
            elif rsi < 30:
                print(f"   ✅ RSI = {rsi:.2f} (超卖区域，可能反弹)")
            elif rsi > 50:
                print(f"   📊 RSI = {rsi:.2f} (偏强区域)")
            else:
                print(f"   📊 RSI = {rsi:.2f} (偏弱区域)")
        
        print()
        print("💡 为什么没有信号？")
        print("   交易信号需要同时满足以下条件：")
        print("   买入信号: MA20上穿MA60 + MACD柱>0 + RSI>50")
        print("   卖出信号: MA20下穿MA60 + MACD柱<0 + RSI<60")
        print("   当前市场可能只满足部分条件，建议继续观察")
    
    print()
    print("="*70)
    
    # 运行回测
    print("\n📈 运行历史回测分析...")
    backtester = Backtester(df)
    backtest_result = backtester.run_backtest()
    
    if backtest_result and backtest_result.get('total_trades', 0) > 0:
        print(f"\n📊 回测结果统计:")
        print(f"   总信号数: {backtest_result.get('total_signals', 0)}")
        print(f"   总交易数: {backtest_result.get('total_trades', 0)}")
        print(f"   胜率: {backtest_result.get('win_rate', 0):.1f}%")
        print(f"   平均收益: {backtest_result.get('avg_return', 0):+.2f}%")
        print(f"   最大回撤: {backtest_result.get('max_drawdown', 0):.2f}%")
        
        # 显示交易记录
        trades = backtest_result.get('trades', [])
        if trades:
            print(f"\n📋 完整交易记录:")
            print("-"*90)
            print(f"{'日期':<12} {'信号':<6} {'入场价':<10} {'出场价':<10} {'最高价':<10} {'收益率':<10} {'状态':<6}")
            print("-"*90)
            for trade in trades:
                date_str = str(trade['date'])[:10] if isinstance(trade['date'], pd.Timestamp) else str(trade['date'])
                print(f"{date_str:<12} {trade['signal_type']:<6} ${trade['entry_price']:<9.4f} ${trade['exit_price']:<9.4f} ${trade['high_price']:<9.4f} {trade['return_pct']:>+9.2f}% {trade['status']:<6}")
            print("-"*90)
    else:
        print("⚠️  无交易记录可回测")
    
    print()
    print("="*70)
    print("✅ 分析完成")
    print("="*70)


if __name__ == "__main__":
    analyze_3months_signals()


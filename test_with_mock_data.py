"""
使用模拟数据测试程序功能
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.indicators import IndicatorCalculator
from backtest import Backtester
from visualize import ChartVisualizer


def generate_mock_data(days=500, start_price=10.0):
    """生成模拟K线数据"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成价格走势（带趋势和波动）
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, days)  # 日收益率
    prices = [start_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # 生成OHLCV数据
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        volatility = abs(np.random.normal(0, 0.01))
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.uniform(1000000, 5000000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df


def test_indicators():
    """测试技术指标计算"""
    print("="*60)
    print("🧪 测试技术指标计算")
    print("="*60)
    
    # 生成模拟数据
    df = generate_mock_data(days=500, start_price=15.0)
    print(f"✅ 生成 {len(df)} 根模拟K线数据")
    print(f"   价格范围: {df['close'].min():.4f} - {df['close'].max():.4f}")
    
    # 计算指标
    calculator = IndicatorCalculator()
    df = calculator.calculate_indicators(df)
    print("✅ 技术指标计算完成")
    print(f"   MA20: {df['MA20'].iloc[-1]:.4f}")
    print(f"   MA60: {df['MA60'].iloc[-1]:.4f}")
    print(f"   MACD: {df['MACD'].iloc[-1]:.4f}")
    print(f"   RSI: {df['RSI'].iloc[-1]:.2f}")
    
    # 检测信号
    df = calculator.detect_signals(df)
    signals = df[df['signal'] != 0]
    print(f"✅ 信号检测完成，共发现 {len(signals)} 个信号")
    
    # 获取最新信号
    latest = calculator.get_latest_signal(df)
    if latest:
        print(f"✅ 最新信号: {latest['signal_type']} | 价格: {latest['close']:.4f}")
    else:
        print("⚠️  当前无信号")
    
    return df


def test_backtest(df):
    """测试回测功能"""
    print("\n" + "="*60)
    print("🧪 测试回测功能")
    print("="*60)
    
    backtester = Backtester(df)
    result = backtester.run_backtest()
    
    print(f"✅ 回测完成")
    print(f"   总信号数: {result['total_signals']}")
    print(f"   总交易数: {result['total_trades']}")
    print(f"   胜率: {result['win_rate']:.1f}%")
    print(f"   平均收益: {result['avg_return']:+.2f}%")
    print(f"   最大回撤: {result['max_drawdown']:.2f}%")
    
    # 打印最近交易记录
    backtester.print_recent_trades_table(months=12)
    
    return result


def test_visualize(df):
    """测试可视化功能"""
    print("\n" + "="*60)
    print("🧪 测试可视化功能")
    print("="*60)
    
    visualizer = ChartVisualizer()
    chart_path = visualizer.create_candlestick_chart(
        df=df,
        symbol="ARUSDT",
        interval="1d",
        output_file="test_chart.html"
    )
    
    print(f"✅ 图表生成成功: {chart_path}")
    return chart_path


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 Crypto Signal Lite - 功能测试")
    print("="*60 + "\n")
    
    try:
        # 1. 测试指标计算
        df = test_indicators()
        
        # 2. 测试回测
        test_backtest(df)
        
        # 3. 测试可视化
        test_visualize(df)
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        print("\n📊 查看图表: charts/test_chart.html")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


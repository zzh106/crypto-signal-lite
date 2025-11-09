#!/usr/bin/env python3
"""
系统测试脚本
"""
from main_v2 import QuantSignalSystem
from signals.signal_manager import SignalManager
from notifier.serverchan_push import ServerChanNotifier
from position_manager import PositionManager
import yaml


def test_signal_detection():
    """测试信号检测"""
    print("="*60)
    print("🧪 测试信号检测功能")
    print("="*60)
    
    with open("config/settings.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    signal_manager = SignalManager(config)
    
    # 这里可以添加测试数据
    print("✅ 信号管理器初始化成功")
    print(f"   强烈信号阈值: {config['signals']['strong_threshold']}")
    print(f"   中等信号阈值: {config['signals']['medium_threshold']}")
    print(f"   最大持仓天数: {config['signals']['max_holding_days']}")


def test_notifier():
    """测试通知功能"""
    print("\n" + "="*60)
    print("🧪 测试Server酱推送")
    print("="*60)
    
    with open("config/settings.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    notify_config = config.get("notify", {})
    if notify_config.get("serverchan", {}).get("enable"):
        key = notify_config["serverchan"]["key"]
        notifier = ServerChanNotifier(key)
        
        result = notifier.send("测试通知", "这是一条测试消息\n\n系统运行正常 ✅")
        if result:
            print("✅ Server酱推送测试成功")
        else:
            print("❌ Server酱推送测试失败")
    else:
        print("⚠️  Server酱未启用")


def test_position_manager():
    """测试持仓管理"""
    print("\n" + "="*60)
    print("🧪 测试持仓管理")
    print("="*60)
    
    pm = PositionManager()
    
    # 测试开仓
    position_id = pm.open_position(
        "AR/USDT", "买入", 5.50, 0.8, "strong"
    )
    print(f"✅ 开仓成功: {position_id}")
    
    # 测试查询
    open_positions = pm.get_open_positions("AR/USDT")
    print(f"✅ 当前持仓数: {len(open_positions)}")
    
    # 测试平仓
    if open_positions:
        closed = pm.close_position("AR/USDT", 5.60)
        print(f"✅ 平仓成功: {len(closed)} 个持仓")
        if closed:
            p = closed[0]
            print(f"   盈亏: ${p['profit_loss']:.2f} ({p['profit_loss_pct']:+.2f}%)")
    
    # 测试统计
    stats = pm.get_statistics("AR/USDT")
    print(f"✅ 统计信息:")
    print(f"   总交易数: {stats['total_trades']}")
    print(f"   胜率: {stats['win_rate']:.2f}%")
    print(f"   总盈亏: ${stats['total_profit']:.2f}")


def test_full_system():
    """测试完整系统"""
    print("\n" + "="*60)
    print("🧪 测试完整系统（信号检测）")
    print("="*60)
    
    system = QuantSignalSystem()
    results = system.run_signal_check()
    
    print(f"\n✅ 检测完成，共处理 {len(results)} 个交易对")
    for symbol, result in results.items():
        signal_type = result.get("signal_result", {}).get("type", "无")
        print(f"   {symbol}: {signal_type}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "signal":
            test_signal_detection()
        elif test_type == "notify":
            test_notifier()
        elif test_type == "position":
            test_position_manager()
        elif test_type == "full":
            test_full_system()
        else:
            print("用法: python3 test_system.py [signal|notify|position|full]")
    else:
        # 运行所有测试
        test_signal_detection()
        test_notifier()
        test_position_manager()
        print("\n" + "="*60)
        print("✅ 所有测试完成")
        print("="*60)


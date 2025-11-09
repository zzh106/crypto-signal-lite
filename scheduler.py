"""
定时任务调度器
每4小时运行一次信号检测，每天生成一次报告
"""
import schedule
import time
from datetime import datetime
from main_v2 import QuantSignalSystem


def run_signal_check():
    """运行信号检测任务"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始信号检测任务...")
    try:
        system = QuantSignalSystem()
        system.run_signal_check()
    except Exception as e:
        print(f"❌ 信号检测任务失败: {e}")
        import traceback
        traceback.print_exc()


def run_daily_report():
    """运行每日报告任务"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成每日报告...")
    try:
        system = QuantSignalSystem()
        system.generate_daily_report()
    except Exception as e:
        print(f"❌ 每日报告任务失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """启动定时任务"""
    print("="*60)
    print("⏰ 量化信号监控系统 - 定时任务启动")
    print("="*60)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📅 任务计划:")
    print("  - 信号检测: 每4小时运行一次")
    print("  - 每日报告: 每天 09:00 运行")
    print()
    print("按 Ctrl+C 退出")
    print("="*60)
    
    # 每4小时运行一次信号检测
    schedule.every(4).hours.do(run_signal_check)
    
    # 每天09:00运行一次报告（北京时间）
    schedule.every().day.at("09:00").do(run_daily_report)
    
    # 立即运行一次信号检测
    run_signal_check()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n\n👋 定时任务已停止")


if __name__ == "__main__":
    main()


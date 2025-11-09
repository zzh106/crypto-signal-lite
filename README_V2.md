# 量化信号监控系统 v2.0

基于 CryptoSignal 框架思路构建的自动化量化信号监控与推送系统。

## 🎯 核心特性

- ✅ **多币种监控** - 支持配置多个交易对
- ✅ **多指标综合** - EMA、MACD、KDJ、布林带综合判断
- ✅ **信号强度分级** - strong/medium/weak 三级信号
- ✅ **持仓管理** - 自动跟踪入场价、出场价、盈亏，7天强制平仓
- ✅ **定时任务** - 每4小时信号检测，每日报告
- ✅ **Server酱推送** - 微信实时通知
- ✅ **完整日志** - 所有操作记录到日志文件

## 📁 项目结构

```
crypto-signal-lite/
├── config/
│   └── settings.yaml          # 配置文件
├── signals/                   # 信号检测模块
│   ├── ema_signal.py         # EMA信号
│   ├── macd_signal.py        # MACD信号
│   ├── kdj_signal.py         # KDJ信号
│   └── signal_manager.py     # 信号管理器（综合判断）
├── notifier/                  # 通知模块
│   └── serverchan_push.py    # Server酱推送
├── logs/                      # 日志目录
│   ├── signal_log.txt        # 信号日志
│   └── positions.json        # 持仓记录
├── main_v2.py                # 主程序（信号检测）
├── scheduler.py              # 定时任务调度器
├── position_manager.py       # 持仓管理器
└── logger.py                 # 日志系统
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config/settings.yaml`:

```yaml
symbols:
  - "AR/USDT"    # 主跟踪币
  # - "BTC/USDT" # 可选备用币

notify:
  serverchan:
    key: "your_serverchan_key"  # 替换为你的Server酱Key
```

### 3. 运行

#### 立即运行一次信号检测

```bash
python3 main_v2.py
```

#### 启动定时任务（每4小时检测 + 每日报告）

```bash
python3 scheduler.py
```

#### 生成每日报告

```bash
python3 main_v2.py --report
```

## 📊 信号逻辑

### 技术指标

- **EMA (12, 26)**: 快慢均线交叉
- **MACD (12, 26, 9)**: 动能指标
- **KDJ (9, 3, 3)**: 超买超卖指标

### 信号生成规则

**买入信号**（需至少2个指标看多）:
- EMA快线上穿慢线
- MACD柱状图上穿
- KDJ金叉（尤其在超卖区域）

**卖出信号**（需至少2个指标看空）:
- EMA快线下穿慢线
- MACD柱状图下穿
- KDJ死叉（尤其在超买区域）

### 信号强度分级

- **strong** (≥0.8): 强烈信号，3个指标一致
- **medium** (≥0.6): 中等信号，2个指标一致
- **weak** (<0.6): 弱信号，1个指标

## 💼 持仓管理

### 自动跟踪

- ✅ 记录每次开仓（入场价、时间、信号强度）
- ✅ 记录每次平仓（出场价、时间、盈亏）
- ✅ 自动计算盈亏百分比
- ✅ 7天强制平仓机制

### 持仓数据

存储在 `logs/positions.json`:

```json
{
  "AR/USDT": [
    {
      "id": "AR/USDT_20251109_140000",
      "signal_type": "买入",
      "entry_price": 5.55,
      "entry_time": "2025-11-09T14:00:00",
      "exit_price": 5.80,
      "exit_time": "2025-11-10T10:00:00",
      "profit_loss": 0.25,
      "profit_loss_pct": 4.50,
      "holding_days": 1,
      "status": "closed"
    }
  ]
}
```

## 📝 日志系统

### 日志文件

- `logs/signal_log.txt` - 所有操作日志
- 自动轮转（最大10MB，保留5个备份）

### 日志内容

- 信号检测记录
- 开仓/平仓记录
- 强制平仓警告
- 错误信息

## ⏰ 定时任务

### 任务计划

- **信号检测**: 每4小时运行一次
- **每日报告**: 每天 09:00 运行

### macOS 部署

#### 方式1: 使用 scheduler.py（推荐）

```bash
# 后台运行
nohup python3 scheduler.py > logs/scheduler.log 2>&1 &
```

#### 方式2: 使用 launchd

创建 `~/Library/LaunchAgents/com.quant.signal.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quant.signal</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/crypto-signal-lite/main_v2.py</string>
    </array>
    <key>StartInterval</key>
    <integer>14400</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

加载任务:
```bash
launchctl load ~/Library/LaunchAgents/com.quant.signal.plist
```

#### 方式3: 使用 crontab

```bash
crontab -e
```

添加:
```
0 */4 * * * cd /path/to/crypto-signal-lite && /usr/local/bin/python3 main_v2.py
0 9 * * * cd /path/to/crypto-signal-lite && /usr/local/bin/python3 main_v2.py --report
```

## 🔔 通知配置

### Server酱

1. 访问 https://sct.ftqq.com/
2. 注册/登录获取 SendKey
3. 在 `config/settings.yaml` 中配置

### 通知级别

在配置文件中设置 `notify.min_level`:
- `strong`: 只推送强烈信号
- `medium`: 推送中等及以上信号（推荐）
- `weak`: 推送所有信号

## 📊 工作流程

```
1. 定时任务触发（每4小时）
   ↓
2. 获取K线数据（OKX API，4小时线）
   ↓
3. 计算技术指标（EMA、MACD、KDJ）
   ↓
4. 综合判断生成信号（信号管理器）
   ↓
5. 检查信号强度（strong/medium/weak）
   ↓
6. 记录日志
   ↓
7. 发送通知（如果达到最小级别）
   ↓
8. 处理持仓（开仓/平仓/强制平仓）
   ↓
9. 保存持仓记录
```

## 🧪 测试

### 测试信号检测

```bash
python3 main_v2.py
```

### 测试Server酱推送

```python
from notifier.serverchan_push import ServerChanNotifier

notifier = ServerChanNotifier("your_key")
notifier.send("测试", "这是一条测试消息")
```

## 📈 统计功能

### 查看持仓统计

```python
from position_manager import PositionManager

pm = PositionManager()
stats = pm.get_statistics("AR/USDT")
print(f"胜率: {stats['win_rate']:.2f}%")
print(f"总盈亏: ${stats['total_profit']:.2f}")
```

## 🔧 配置说明

### 主要配置项

- `symbols`: 监控币种列表
- `signals.max_holding_days`: 最大持仓天数（默认7天）
- `signals.strong_threshold`: 强烈信号阈值（默认0.8）
- `signals.medium_threshold`: 中等信号阈值（默认0.6）
- `notify.min_level`: 最小通知级别
- `scheduler.signal_check_interval`: 信号检测间隔（小时）

## ⚠️ 注意事项

1. **7天强制平仓**: 系统会自动平掉超过7天的持仓
2. **信号条件**: 需要至少2个指标一致才会生成信号
3. **数据限制**: OKX API 单次最多返回100根K线
4. **网络要求**: 需要能访问 OKX API（对大陆友好）

## 🚀 后续优化方向

- [ ] 支持更多技术指标
- [ ] 机器学习优化信号判断
- [ ] Web Dashboard 可视化
- [ ] 支持更多通知方式（邮件、Telegram）
- [ ] 策略回测优化
- [ ] 仓位控制功能

## 📝 更新日志

### v2.0 (2025-11-09)
- ✅ 重构项目结构
- ✅ 添加EMA、KDJ信号
- ✅ 实现信号强度分级
- ✅ 添加持仓管理（7天强制平仓）
- ✅ 实现日志系统
- ✅ 定时任务（每4小时 + 每日报告）
- ✅ 多币种支持

---

**项目状态**: ✅ 可用  
**Python版本**: 3.9+  
**最后更新**: 2025-11-09


# Crypto Signal Lite - 项目架构与工作流程文档

## 📋 目录
1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [核心模块详解](#核心模块详解)
4. [工作流程](#工作流程)
5. [数据流](#数据流)
6. [当前能力总结](#当前能力总结)
7. [技术栈](#技术栈)
8. [已知限制](#已知限制)

---

## 📖 项目概述

**Crypto Signal Lite** 是一个专用于分析 AR/USDT (Arweave) 的量化交易信号检测工具。通过技术指标分析、历史回测和可视化，为交易决策提供数据支持。

### 核心功能
- ✅ 实时数据获取（OKX API）
- ✅ 技术指标计算（MA、MACD、RSI、BOLL）
- ✅ 交易信号检测（买入/卖出）
- ✅ 历史回测分析
- ✅ 可视化图表生成
- ✅ 消息推送通知（Server酱）

---

## 🏗️ 系统架构

```
crypto-signal-lite/
├── main.py                    # 主程序入口，协调各模块
├── config.yaml               # 配置文件（交易对、周期、通知等）
├── requirements.txt          # Python依赖包
│
├── app/                       # 核心应用模块
│   ├── fetch_data.py         # 数据获取模块（OKX API）
│   ├── indicators.py         # 技术指标计算与信号检测
│   └── notifier.py           # 消息推送模块（Server酱）
│
├── backtest.py               # 历史回测模块
├── visualize.py              # 可视化模块（Plotly）
│
└── 辅助工具/
    ├── analyze_signals.py    # 信号分析脚本
    └── test_with_mock_data.py # 测试脚本（模拟数据）
```

### 模块依赖关系

```
main.py
  ├── OKXDataFetcher (fetch_data.py)
  ├── IndicatorCalculator (indicators.py)
  ├── Notifier (notifier.py)
  ├── Backtester (backtest.py)
  └── ChartVisualizer (visualize.py)
```

---

## 🔧 核心模块详解

### 1. 数据获取模块 (`app/fetch_data.py`)

**类名**: `OKXDataFetcher`

**职责**:
- 从 OKX API 获取K线数据
- 处理数据格式转换
- 备用数据源（CoinGecko + 模拟数据）

**主要方法**:
- `fetch_klines(interval, limit)`: 获取指定周期的K线数据
- `_convert_interval(interval)`: 转换时间周期格式（1d → 1D）
- `_fetch_fallback_data()`: 备用数据获取（当OKX API失败时）

**数据格式**:
```python
DataFrame columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
Index: timestamp (datetime)
```

**限制**:
- OKX API 单次最多返回 100 根K线
- 需要处理地区访问限制（已实现备用方案）

---

### 2. 技术指标模块 (`app/indicators.py`)

**类名**: `IndicatorCalculator`

**职责**:
- 计算技术指标
- 检测交易信号
- 获取最新信号

**计算的指标**:
1. **MA20/MA60**: 简单移动平均线
   - 方法: `_sma(series, length)`
   - 用途: 判断趋势方向

2. **MACD (12, 26, 9)**: 指数平滑异同移动平均线
   - 方法: `_macd(series, fast, slow, signal)`
   - 返回: MACD线、信号线、柱状图
   - 用途: 判断动能和趋势变化

3. **RSI(14)**: 相对强弱指标
   - 方法: `_rsi(series, length)`
   - 用途: 判断超买超卖

4. **BOLL(20)**: 布林带
   - 方法: `_bbands(series, length, std)`
   - 返回: 上轨、中轨、下轨
   - 用途: 判断波动和支撑阻力

**信号检测逻辑**:

**买入信号**（需同时满足）:
```python
- MA20 上穿 MA60 (MA_cross_up)
- MACD柱 > 0
- RSI > 50
```

**卖出信号**（需同时满足）:
```python
- MA20 下穿 MA60 (MA_cross_down)
- MACD柱 < 0
- RSI < 60
```

**主要方法**:
- `calculate_indicators(df)`: 计算所有技术指标
- `detect_signals(df)`: 检测并标记交易信号
- `get_latest_signal(df)`: 获取最新信号信息

---

### 3. 回测模块 (`backtest.py`)

**类名**: `Backtester`

**职责**:
- 模拟历史交易
- 计算回测指标
- 生成交易记录

**回测逻辑**:
1. 遍历所有信号点
2. 买入信号 → 开仓
3. 卖出信号 → 平仓
4. 计算每笔交易的收益

**计算的指标**:
- `total_signals`: 总信号数
- `total_trades`: 总交易数
- `win_rate`: 胜率（盈利交易占比）
- `avg_return`: 平均收益率
- `max_drawdown`: 最大回撤

**主要方法**:
- `run_backtest()`: 运行完整回测
- `get_recent_trades(months)`: 获取最近N个月的交易
- `print_backtest_summary()`: 打印回测摘要
- `print_recent_trades_table(months)`: 打印交易记录表

---

### 4. 可视化模块 (`visualize.py`)

**类名**: `ChartVisualizer`

**职责**:
- 生成交互式K线图
- 标注买卖信号点
- 显示技术指标

**图表内容**:
1. **主图**: K线 + MA20/MA60 均线
2. **买入信号**: 绿色上三角（在K线下方）
3. **卖出信号**: 红色下三角（在K线上方）
4. **MACD指标图**: MACD线、信号线、柱状图
5. **RSI指标图**: RSI线 + 超买超卖区域（30/50/70）

**输出格式**: HTML文件（Plotly交互式图表）

**主要方法**:
- `create_candlestick_chart(df, symbol, interval, output_file)`: 创建完整图表

---

### 5. 通知模块 (`app/notifier.py`)

**类名**: `Notifier`

**职责**:
- 发送交易信号通知
- 支持多种通知方式（当前：Server酱）

**通知内容**:
- 交易对和周期
- 信号类型（买入/卖出）
- 当前价格
- 技术指标数据

**主要方法**:
- `send_serverchan(title, content)`: 发送Server酱通知
- `notify(title, content)`: 通用通知方法
- `notify_signal(symbol, interval, signal_info)`: 发送交易信号通知

---

### 6. 主程序 (`main.py`)

**类名**: `CryptoSignalLite`

**职责**:
- 协调各模块工作
- 执行完整分析流程
- 支持定时任务

**主要方法**:
- `load_config()`: 加载配置文件
- `analyze_interval(interval)`: 分析单个周期
- `run()`: 运行一次完整分析
- `run_scheduled()`: 运行定时任务（每天09:00）

---

## 🔄 工作流程

### 完整执行流程

```
1. 初始化
   ├── 加载 config.yaml
   ├── 创建 OKXDataFetcher
   ├── 创建 IndicatorCalculator
   ├── 创建 Notifier
   └── 创建 ChartVisualizer

2. 对每个时间周期（1d, 1w）:
   │
   ├── 2.1 数据获取
   │   ├── 调用 OKXDataFetcher.fetch_klines()
   │   ├── 如果失败 → 使用备用数据源
   │   └── 返回 DataFrame (OHLCV)
   │
   ├── 2.2 技术指标计算
   │   ├── 调用 IndicatorCalculator.calculate_indicators()
   │   ├── 计算 MA20, MA60
   │   ├── 计算 MACD (12, 26, 9)
   │   ├── 计算 RSI(14)
   │   └── 计算 BOLL(20)
   │
   ├── 2.3 信号检测
   │   ├── 调用 IndicatorCalculator.detect_signals()
   │   ├── 检测MA交叉
   │   ├── 检查MACD柱
   │   ├── 检查RSI
   │   └── 标记买入/卖出信号
   │
   ├── 2.4 获取最新信号
   │   └── 调用 IndicatorCalculator.get_latest_signal()
   │
   ├── 2.5 历史回测
   │   ├── 创建 Backtester
   │   ├── 调用 run_backtest()
   │   └── 计算胜率、平均收益、最大回撤
   │
   ├── 2.6 可视化
   │   ├── 调用 ChartVisualizer.create_candlestick_chart()
   │   └── 生成 HTML 图表文件
   │
   └── 2.7 通知推送
       ├── 如果有信号 → 调用 Notifier.notify_signal()
       └── 发送 Server酱通知

3. 输出结果
   ├── 打印信号信息
   ├── 打印回测统计
   ├── 打印交易记录表
   └── 显示图表保存路径
```

### 定时任务流程

```
启动定时任务
  ↓
每天 UTC 01:00 (北京时间 09:00)
  ↓
执行完整分析流程
  ↓
检测到信号 → 发送通知
  ↓
等待下一次执行
```

---

## 📊 数据流

### 数据流转过程

```
OKX API
  ↓
[原始K线数据]
  ↓
OKXDataFetcher.fetch_klines()
  ↓
[DataFrame: OHLCV]
  ↓
IndicatorCalculator.calculate_indicators()
  ↓
[DataFrame: OHLCV + 技术指标]
  ↓
IndicatorCalculator.detect_signals()
  ↓
[DataFrame: OHLCV + 技术指标 + 信号]
  ↓
    ├──→ Backtester.run_backtest()
    │     ↓
    │   [回测结果: 胜率、收益、回撤]
    │
    ├──→ ChartVisualizer.create_candlestick_chart()
    │     ↓
    │   [HTML图表文件]
    │
    └──→ Notifier.notify_signal()
          ↓
        [Server酱通知]
```

### 数据结构

**输入数据** (OKX API):
```json
{
  "code": "0",
  "data": [
    ["timestamp_ms", "open", "high", "low", "close", "volume", ...]
  ]
}
```

**处理后数据** (DataFrame):
```python
DataFrame:
  Index: timestamp (datetime)
  Columns:
    - open, high, low, close, volume (float)
    - MA20, MA60 (float)
    - MACD, MACD_signal, MACD_hist (float)
    - RSI (float)
    - BB_upper, BB_middle, BB_lower (float)
    - signal (int: 0/1/-1)
    - signal_type (str: ""/"买入"/"卖出")
```

**输出结果**:
```python
{
  "interval": "1d",
  "latest_signal": {
    "timestamp": datetime,
    "signal": 1/-1,
    "signal_type": "买入"/"卖出",
    "close": float,
    "MA20": float,
    "MA60": float,
    "MACD_hist": float,
    "RSI": float
  },
  "backtest": {
    "total_signals": int,
    "total_trades": int,
    "win_rate": float,
    "avg_return": float,
    "max_drawdown": float,
    "trades": [...]
  },
  "chart_path": "charts/arusdt_signal_chart.html",
  "data": DataFrame
}
```

---

## ✅ 当前能力总结

### 已实现功能

#### 1. 数据获取 ✅
- [x] OKX API 数据获取
- [x] 自动格式转换（ARUSDT → AR-USDT）
- [x] 时间周期转换（1d → 1D）
- [x] 备用数据源（CoinGecko + 模拟数据）
- [x] 错误处理和重试机制

#### 2. 技术指标 ✅
- [x] MA20/MA60 移动平均线
- [x] MACD (12, 26, 9)
- [x] RSI(14)
- [x] BOLL(20) 布林带
- [x] 所有指标手动实现（不依赖外部库）

#### 3. 信号检测 ✅
- [x] 买入信号检测（3个条件同时满足）
- [x] 卖出信号检测（3个条件同时满足）
- [x] 信号标记和存储
- [x] 最新信号获取

#### 4. 回测分析 ✅
- [x] 历史交易模拟
- [x] 胜率计算
- [x] 平均收益率计算
- [x] 最大回撤计算
- [x] 交易记录生成

#### 5. 可视化 ✅
- [x] Plotly 交互式K线图
- [x] MA均线叠加
- [x] 买卖信号标注
- [x] MACD指标图
- [x] RSI指标图
- [x] HTML格式输出

#### 6. 通知推送 ✅
- [x] Server酱集成
- [x] 信号通知格式化
- [x] 错误处理

#### 7. 定时任务 ✅
- [x] Schedule 定时执行
- [x] 每天自动运行
- [x] 后台运行支持

#### 8. 配置管理 ✅
- [x] YAML配置文件
- [x] 多周期支持
- [x] 通知配置

---

## 🛠️ 技术栈

### 核心依赖
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **requests**: HTTP请求（API调用）
- **pyyaml**: 配置文件解析
- **plotly**: 交互式图表
- **schedule**: 定时任务

### 外部服务
- **OKX API**: 主要数据源
- **CoinGecko API**: 备用数据源（获取当前价格）
- **Server酱**: 消息推送服务

---

## ⚠️ 已知限制

### 1. 数据获取限制
- ❌ OKX API 单次最多返回 100 根K线
- ❌ 无法获取超过100天的历史数据（需要多次请求）
- ⚠️ 备用数据源使用模拟数据，不够准确

### 2. 信号检测限制
- ❌ 信号条件过于严格（需3个条件同时满足）
- ❌ 可能错过部分交易机会
- ❌ 没有信号强度评分

### 3. 回测限制
- ❌ 没有考虑交易手续费
- ❌ 没有考虑滑点
- ❌ 简单的买入卖出逻辑，没有止损止盈

### 4. 功能限制
- ❌ 只支持单一交易对（AR/USDT）
- ❌ 只支持日线和周线
- ❌ 没有实时监控功能
- ❌ 没有策略优化功能

### 5. 通知限制
- ❌ 只支持 Server酱
- ❌ 没有通知频率限制（可能重复通知）

---

## 📝 配置文件说明

### config.yaml 结构

```yaml
symbol: ARUSDT              # 交易对（自动转换为 AR-USDT）
exchange: okx               # 交易所（当前仅支持 okx）
intervals: ["1d", "1w"]     # 分析周期列表
data_limit: 500             # 数据获取数量（实际受OKX限制为100）

notify:
  method: serverchan        # 通知方式
  key: SCT301986...         # Server酱 API Key
```

---

## 🚀 运行模式

### 1. 立即运行
```bash
python main.py
```

### 2. 定时运行
```bash
python main.py --schedule
```

### 3. 信号分析
```bash
python analyze_signals.py
```

### 4. 测试模式
```bash
python test_with_mock_data.py
```

---

## 📈 性能指标

- **数据获取**: ~2-3秒（OKX API）
- **指标计算**: ~0.5秒（100根K线）
- **回测分析**: ~0.1秒
- **图表生成**: ~1-2秒
- **总执行时间**: ~5-10秒（单周期）

---

## 🔍 代码质量

- ✅ 模块化设计，职责清晰
- ✅ 错误处理完善
- ✅ 代码注释完整
- ✅ 类型提示（部分）
- ⚠️ 缺少单元测试
- ⚠️ 缺少日志系统

---

## 📚 相关文档

- `README.md`: 用户使用指南
- `EXAMPLE_OUTPUT.md`: 运行示例
- `ARCHITECTURE.md`: 本文档（架构说明）

---

**文档版本**: v1.0  
**最后更新**: 2025-11-09  
**维护者**: zzh106


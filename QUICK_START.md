# 🚀 快速开始指南

## 一键运行测试

```bash
# 1. 进入项目目录
cd crypto-signal-lite

# 2. 安装依赖（如果还没安装）
pip3 install -r requirements.txt

# 3. 运行一次信号检测
python3 main_v2.py
```

## 📋 核心文件说明

| 文件 | 功能 | 运行方式 |
|------|------|----------|
| `main_v2.py` | 主程序（信号检测） | `python3 main_v2.py` |
| `scheduler.py` | 定时任务调度器 | `python3 scheduler.py` |
| `test_system.py` | 系统测试脚本 | `python3 test_system.py` |
| `config/settings.yaml` | 配置文件 | 编辑此文件 |

## ⚙️ 配置要点

### 1. 设置监控币种

编辑 `config/settings.yaml`:

```yaml
symbols:
  - "AR/USDT"    # 主跟踪币
  # - "BTC/USDT" # 取消注释添加更多币种
```

### 2. 配置Server酱

```yaml
notify:
  serverchan:
    key: "SCT301986TWvJKtkBJjIQAwWm7ayQkhs79"  # 你的Server酱Key
    enable: true
```

### 3. 调整信号阈值

```yaml
signals:
  strong_threshold: 0.8    # 强烈信号阈值
  medium_threshold: 0.6    # 中等信号阈值
  max_holding_days: 7      # 最大持仓天数
```

## 🎯 运行模式

### 模式1: 单次运行（测试）

```bash
python3 main_v2.py
```

### 模式2: 定时任务（生产）

```bash
# 后台运行
nohup python3 scheduler.py > logs/scheduler.log 2>&1 &
```

### 模式3: 生成日报

```bash
python3 main_v2.py --report
```

## 📊 查看结果

### 日志文件

```bash
# 实时查看
tail -f logs/signal_log.txt

# 查看持仓
cat logs/positions.json | python3 -m json.tool
```

### 测试各个模块

```bash
python3 test_system.py signal    # 测试信号检测
python3 test_system.py notify     # 测试Server酱
python3 test_system.py position   # 测试持仓管理
python3 test_system.py full       # 完整测试
```

## 🔍 工作流程

```
每4小时自动运行:
  1. 获取K线数据 (OKX API)
  2. 计算技术指标 (EMA/MACD/KDJ)
  3. 综合判断生成信号
  4. 检查持仓（7天强制平仓）
  5. 处理开仓/平仓
  6. 发送通知（如果达到级别）
  7. 记录日志

每天09:00自动运行:
  生成并发送每日报告
```

## ✅ 验证系统运行

运行后应该看到：

```
✅ 量化信号监控系统启动
✅ 获取到 100 根K线数据
✅ 分析交易信号...
[信号] AR/USDT | 无 | 级别:none | 强度:24.90% | 价格:$5.4310
✅ 信号检测任务完成
```

## 📚 更多文档

- `README_V2.md` - 完整功能说明
- `DEPLOYMENT.md` - 部署指南
- `ARCHITECTURE.md` - 架构文档

---

**准备好了吗？运行 `python3 main_v2.py` 开始！** 🚀


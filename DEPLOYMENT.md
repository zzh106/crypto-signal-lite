# 部署指南 - macOS

## 🚀 快速部署

### 1. 环境准备

```bash
# 确保 Python 3.9+
python3 --version

# 安装依赖
cd crypto-signal-lite
pip3 install -r requirements.txt
```

### 2. 配置

编辑 `config/settings.yaml`:

```yaml
symbols:
  - "AR/USDT"    # 你的交易对

notify:
  serverchan:
    key: "your_serverchan_key"  # 替换为你的Key
    enable: true
```

### 3. 测试运行

```bash
# 测试完整系统
python3 main_v2.py

# 测试各个模块
python3 test_system.py signal    # 测试信号检测
python3 test_system.py notify     # 测试通知
python3 test_system.py position   # 测试持仓管理
python3 test_system.py full       # 测试完整流程
```

---

## ⏰ 定时任务部署

### 方式1: 使用 scheduler.py（推荐，简单）

```bash
# 前台运行（测试）
python3 scheduler.py

# 后台运行（生产）
nohup python3 scheduler.py > logs/scheduler.log 2>&1 &

# 查看日志
tail -f logs/scheduler.log

# 停止
pkill -f scheduler.py
```

### 方式2: 使用 launchd（macOS 原生）

#### 创建 plist 文件

```bash
nano ~/Library/LaunchAgents/com.quant.signal.plist
```

内容：

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
        <string>/Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite/main_v2.py</string>
    </array>
    
    <key>StartInterval</key>
    <integer>14400</integer>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite/logs/launchd.out</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite/logs/launchd.err</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite</string>
</dict>
</plist>
```

**注意**: 修改路径为你的实际路径！

#### 加载任务

```bash
# 加载
launchctl load ~/Library/LaunchAgents/com.quant.signal.plist

# 立即运行一次
launchctl start com.quant.signal

# 查看状态
launchctl list | grep com.quant.signal

# 卸载
launchctl unload ~/Library/LaunchAgents/com.quant.signal.plist
```

### 方式3: 使用 crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每4小时运行一次）
0 */4 * * * cd /path/to/crypto-signal-lite && /usr/local/bin/python3 main_v2.py >> logs/cron.log 2>&1

# 每天09:00生成报告
0 9 * * * cd /path/to/crypto-signal-lite && /usr/local/bin/python3 main_v2.py --report >> logs/cron.log 2>&1
```

---

## 📊 监控和日志

### 查看日志

```bash
# 实时查看信号日志
tail -f logs/signal_log.txt

# 查看持仓记录
cat logs/positions.json | python3 -m json.tool
```

### 检查运行状态

```bash
# 检查进程
ps aux | grep main_v2.py

# 检查定时任务
ps aux | grep scheduler.py
```

---

## 🔧 故障排查

### 问题1: 无法获取数据

```bash
# 测试OKX API连接
python3 -c "from app.fetch_data import OKXDataFetcher; f = OKXDataFetcher(); print(f.fetch_klines('AR/USDT', '4h', 10))"
```

### 问题2: Server酱推送失败

```bash
# 测试推送
python3 test_system.py notify
```

### 问题3: 模块导入错误

```bash
# 检查Python路径
python3 -c "import sys; print(sys.path)"

# 确保在项目根目录运行
pwd
```

---

## 📝 维护建议

1. **定期检查日志**: 每天查看 `logs/signal_log.txt`
2. **监控持仓**: 检查 `logs/positions.json` 中的持仓状态
3. **更新配置**: 根据需要调整 `config/settings.yaml`
4. **备份数据**: 定期备份 `logs/` 目录

---

## 🎯 一键运行命令

```bash
# 测试运行
python3 main_v2.py

# 生成报告
python3 main_v2.py --report

# 启动定时任务
python3 scheduler.py
```


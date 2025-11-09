# 手动推送代码到 GitHub

当前 Token 权限不足，请使用以下方法之一：

## 方法一：重新生成 Token（推荐）

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. **必须勾选权限**：
   - ✅ **repo** (完整仓库访问权限) - **这是必需的！**
4. 生成新 token
5. 运行以下命令（替换 YOUR_NEW_TOKEN）：

```bash
cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite
git remote set-url origin https://zzh106:YOUR_NEW_TOKEN@github.com/zzh106/crypto-signal-lite.git
git push -u origin main
```

## 方法二：使用 GitHub Desktop

1. 下载安装 GitHub Desktop：https://desktop.github.com/
2. 登录你的 GitHub 账号
3. 在 GitHub Desktop 中：
   - File → Add Local Repository
   - 选择：`/Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite`
   - 点击 "Publish repository"
   - 选择 `zzh106/crypto-signal-lite`

## 方法三：使用 SSH（如果已配置）

```bash
cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite
git remote set-url origin git@github.com:zzh106/crypto-signal-lite.git
git push -u origin main
```

## 方法四：手动输入凭据

```bash
cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite
git remote set-url origin https://github.com/zzh106/crypto-signal-lite.git
git push -u origin main
# 当提示输入用户名时：输入 zzh106
# 当提示输入密码时：输入你的 GitHub token（不是密码）
```

---

**当前仓库状态：**
- ✅ 本地代码已准备好（2个提交，13个文件）
- ✅ 远程仓库已创建：https://github.com/zzh106/crypto-signal-lite
- ⚠️ 等待推送代码


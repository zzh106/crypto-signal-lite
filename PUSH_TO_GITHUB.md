# 上传到 GitHub 的步骤

## 方法一：使用 GitHub 网页创建（推荐）

1. **在 GitHub 上创建新仓库**
   - 访问 https://github.com/new
   - Repository name: `crypto-signal-lite`
   - Description: `AR/USDT trading signal analyzer with backtesting and visualization`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **推送代码**
   运行以下命令（将 YOUR_USERNAME 替换为你的 GitHub 用户名）：

   ```bash
   cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite
   git remote add origin https://github.com/YOUR_USERNAME/crypto-signal-lite.git
   git branch -M main
   git push -u origin main
   ```

## 方法二：使用 GitHub CLI（如果已安装）

```bash
gh repo create crypto-signal-lite --public --source=. --remote=origin --push
```

## 方法三：使用 SSH（如果已配置 SSH key）

```bash
git remote add origin git@github.com:YOUR_USERNAME/crypto-signal-lite.git
git branch -M main
git push -u origin main
```


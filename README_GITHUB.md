# 上传到 GitHub 的两种方法

## 🚀 方法一：使用自动化脚本（推荐）

### 1. 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. 勾选 **`repo`** 权限（完整仓库访问权限）
4. 点击 **"Generate token"**
5. **复制生成的 token**（只显示一次，请保存好）

### 2. 运行脚本

```bash
cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite
./create_github_repo.sh YOUR_GITHUB_USERNAME YOUR_GITHUB_TOKEN
```

**示例：**
```bash
./create_github_repo.sh zhangzh crypto-signal-lite ghp_xxxxxxxxxxxxxxxxxxxx
```

脚本会自动：
- ✅ 在 GitHub 上创建 `crypto-signal-lite` 仓库
- ✅ 添加远程仓库地址
- ✅ 推送所有代码

---

## 📝 方法二：手动操作

### 1. 在 GitHub 网页创建仓库

1. 访问 https://github.com/new
2. **Repository name**: `crypto-signal-lite`
3. **Description**: `AR/USDT trading signal analyzer with backtesting and visualization`
4. 选择 **Public** 或 **Private**
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 **"Create repository"**

### 2. 推送代码

在终端运行以下命令（替换 `YOUR_USERNAME` 为你的 GitHub 用户名）：

```bash
cd /Users/zzh/.cursor/worktrees/Crypto-Signal/4my78/crypto-signal-lite

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/crypto-signal-lite.git

# 设置主分支
git branch -M main

# 推送代码
git push -u origin main
```

如果使用 SSH（已配置 SSH key）：

```bash
git remote add origin git@github.com:YOUR_USERNAME/crypto-signal-lite.git
git branch -M main
git push -u origin main
```

---

## ✅ 验证

推送成功后，访问：
```
https://github.com/YOUR_USERNAME/crypto-signal-lite
```

你应该能看到所有文件已上传。


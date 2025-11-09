#!/bin/bash

# GitHub 仓库创建和推送脚本
# 使用方法: ./create_github_repo.sh YOUR_GITHUB_USERNAME YOUR_GITHUB_TOKEN

set -e

GITHUB_USERNAME=${1:-""}
GITHUB_TOKEN=${2:-""}
REPO_NAME="crypto-signal-lite"
REPO_DESCRIPTION="AR/USDT trading signal analyzer with backtesting and visualization"

if [ -z "$GITHUB_USERNAME" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 错误: 需要提供 GitHub 用户名和 Token"
    echo ""
    echo "使用方法:"
    echo "  ./create_github_repo.sh YOUR_USERNAME YOUR_TOKEN"
    echo ""
    echo "获取 GitHub Token:"
    echo "  1. 访问 https://github.com/settings/tokens"
    echo "  2. 点击 'Generate new token (classic)'"
    echo "  3. 勾选 'repo' 权限"
    echo "  4. 生成并复制 token"
    exit 1
fi

echo "🚀 正在创建 GitHub 仓库..."
echo "   仓库名: $REPO_NAME"
echo "   用户名: $GITHUB_USERNAME"
echo ""

# 创建 GitHub 仓库
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESCRIPTION\",\"private\":false}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ GitHub 仓库创建成功!"
    echo ""
    
    # 添加远程仓库
    echo "📡 添加远程仓库..."
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    
    # 设置分支
    git branch -M main
    
    # 推送代码
    echo "📤 推送代码到 GitHub..."
    git push -u origin main
    
    echo ""
    echo "✅ 完成! 仓库地址:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    
elif [ "$HTTP_CODE" -eq 422 ]; then
    echo "⚠️  仓库已存在，直接推送代码..."
    echo ""
    
    # 添加远程仓库
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    
    # 设置分支
    git branch -M main
    
    # 推送代码
    echo "📤 推送代码到 GitHub..."
    git push -u origin main
    
    echo ""
    echo "✅ 完成! 仓库地址:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    
else
    echo "❌ 创建仓库失败 (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi


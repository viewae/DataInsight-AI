#!/bin/bash
# DataInsight AI — 一键启动脚本（在 WSL 中执行）

set -e

# 1. 修复 Docker 权限
sudo chmod 777 /var/run/docker.sock 2>/dev/null || true

# 2. 加载 API 密钥（优先用环境变量，其次从 Windows 系统变量读取）
if [ -z "$DEEPSEEK_API_KEY" ]; then
  # 尝试从 Windows 环境变量读取（WSL 可通过 /mnt/wslg/ 或 /proc/sys/... 读取）
  echo "⚠ DEEPSEEK_API_KEY 未设置，请在启动时传入："
  echo "   DEEPSEEK_API_KEY=sk-xxx ./start.sh"
fi

# 3. 启动所有服务
cd "$(dirname "$0")"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}" docker compose up -d --build

echo ""
echo "✅ 服务已启动："
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   前端开发: npm run dev (在 frontend/ 目录)"
echo ""

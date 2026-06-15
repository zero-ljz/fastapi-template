#!/bin/bash
set -e

# ================================
# 容器入口脚本
# ================================

# ---------- 等待 MySQL 就绪 ----------
echo "⏳ 正在等待 MySQL 数据库就绪..."

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python -c "import socket; s=socket.create_connection(('$DB_HOST', ${DB_PORT:-3306}), timeout=2); s.close()" 2>/dev/null; then
        echo "✅ MySQL 数据库已就绪！"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ MySQL 尚未就绪，正在重试 ($RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ 无法连接到 MySQL 数据库，已达到最大重试次数 ($MAX_RETRIES)，退出。"
    exit 1
fi

# ---------- 执行数据库迁移 ----------
echo "🔄 正在执行数据库迁移 (alembic upgrade head)..."
alembic upgrade head
echo "✅ 数据库迁移完成！"

# ---------- 初始化种子数据 ----------
echo "🌱 正在初始化种子数据..."
python app/initial_data.py
echo "✅ 种子数据初始化完成！"

# ---------- 启动应用服务 ----------
echo "🚀 正在启动应用服务..."
exec "$@"

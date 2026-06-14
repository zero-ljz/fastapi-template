#!/bin/bash

# 1. 定义虚拟环境目录
VENV_DIR=".venv"

echo "--- 正在检查并安装系统级依赖 ---"
# 注意：这通常需要 sudo 权限
sudo apt-get update
sudo apt-get install -y build-essential pkg-config default-libmysqlclient-dev python3-dev

# 2. 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "--- 首次运行：正在创建虚拟环境并安装依赖 ---"
    python3 -m venv $VENV_DIR
    
    # 使用虚拟环境内的 pip，无需手动 source 激活
    $VENV_DIR/bin/pip install --upgrade pip
    $VENV_DIR/bin/pip install -r requirements.txt
    echo "--- 环境初始化完成 ---"
else
    echo "--- 虚拟环境已就绪 ---"
fi

# 3. 启动 FastAPI
echo "--- 正在启动项目 ---"
$VENV_DIR/bin/python run.py
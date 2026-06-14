# 1. 定义虚拟环境目录
$VENV_DIR = ".venv"

# 2. 检查虚拟环境是否存在
if (!(Test-Path $VENV_DIR)) {
    Write-Host "--- 首次运行：正在创建虚拟环境并安装依赖 ---" -ForegroundColor Cyan
    python -m venv $VENV_DIR
    
    # 直接调用虚拟环境内的路径执行安装
    & "$VENV_DIR\Scripts\python.exe" -m pip install --upgrade pip
    & "$VENV_DIR\Scripts\pip.exe" install -r requirements.txt
    Write-Host "--- 环境初始化完成 ---" -ForegroundColor Green
} else {
    Write-Host "--- 虚拟环境已就绪 ---" -ForegroundColor Gray
}

# 3. 启动 FastAPI
Write-Host "--- 正在启动项目 ---" -ForegroundColor Green
& "$VENV_DIR\Scripts\python.exe" run.py
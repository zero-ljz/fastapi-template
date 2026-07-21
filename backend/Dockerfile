# ================================
# 阶段一：构建阶段（安装依赖）
# ================================
FROM python:3.10-slim-bullseye AS builder

# 防止Python在容器中生成.pyc文件
ENV PYTHONDONTWRITEBYTECODE=1
# 关闭缓冲以便更容易地记录容器日志
ENV PYTHONUNBUFFERED=1

# 设置pip源
RUN pip config set global.index-url https://pypi.org/simple/

# 安装编译mysqlclient所需的系统依赖（合并为单层以减少镜像体积）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 pip 依赖到指定目录，方便后续拷贝
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt

# ================================
# 阶段二：运行阶段（最终镜像）
# ================================
FROM python:3.10-slim-bullseye AS runtime

# 防止Python在容器中生成.pyc文件
ENV PYTHONDONTWRITEBYTECODE=1
# 关闭缓冲以便更容易地记录容器日志
ENV PYTHONUNBUFFERED=1

# 安装运行时所需的系统依赖并设置时区（合并为单层以减少镜像体积）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
        default-libmysqlclient-dev \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段拷贝已安装的Python依赖
COPY --from=builder /install /usr/local

# 设置工作目录
WORKDIR /app

# 拷贝项目代码
COPY . /app

# 拷贝入口脚本并赋予可执行权限
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

# 创建非root用户（uid 1000）并赋予 /app 目录权限
RUN adduser --uid 1000 --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 容器入口：先执行数据库迁移，再启动应用服务
ENTRYPOINT ["bash", "scripts/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

FROM python:3.11-slim

WORKDIR /app

# 单独复制 requirements.txt，这样依赖不变时可以复用 pip 缓存层
COPY requirements.txt .

# 缓存 pip 安装层
RUN pip install --no-cache-dir -r requirements.txt

# 安装系统依赖（ffmpeg）
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 再复制代码，避免频繁触发重构前面的层
COPY . .

CMD ["python", "main.py"]

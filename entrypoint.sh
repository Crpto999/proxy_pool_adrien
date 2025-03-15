#!/bin/bash
set -e

# 设置时区
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建配置目录（如果不存在）
mkdir -p /app/mihomo/config

# 首次生成 config_multi 配置文件
python /app/python/config_updater.py --generate

# 启动 mihomo（作为后台进程）
mihomo -f /app/mihomo/config/config_multi.yaml > /proc/1/fd/1 2>/proc/1/fd/1 &

# 等待 mihomo 启动完成（可根据需要调整等待时间）
sleep 10

# 启动定时任务，用于定期更新配置
python /app/python/generate_config_multi.py &

# 启动 API 服务（前台进程，确保容器持续运行）
cd /app/python
uvicorn api:app --host 0.0.0.0 --port 20000

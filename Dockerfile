FROM python:3.12-slim

# 设置 pip 使用清华镜像源
RUN mkdir -p /root/.pip && echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple" > /root/.pip/pip.conf

# 复制项目文件
COPY requirements.txt /app/
COPY python /app/python
COPY entrypoint.sh /app/entrypoint.sh
COPY mihomo-linux-amd64-alpha-3e966e8.gz /app/mihomo/mihomo.gz
COPY mihomo/ui /app/mihomo/ui
# 安装 Python 依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 解压并安装 mihomo
RUN mkdir -p /app/mihomo && \
    gunzip /app/mihomo/mihomo.gz && \
    chmod +x /app/mihomo/mihomo && \
    mv /app/mihomo/mihomo /usr/local/bin/mihomo

# 设置工作目录
WORKDIR /app

# 赋予 entrypoint.sh 可执行权限
RUN chmod +x /app/entrypoint.sh

# 设置时区
ENV TZ=${TZ}

# 暴露端口
EXPOSE 20000
EXPOSE 20001-20050

# 运行入口脚本
CMD ["/app/entrypoint.sh"]

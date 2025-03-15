# Proxy Pool Docker 部署与使用指南

## 项目介绍

这是一个基于 Clash Meta (mihomo) 实现的代理池管理系统，通过 Docker 容器化部署。该系统可以自动从订阅源获取代理节点，并为每个代理节点分配独立的端口，使用户能够根据需要连接到不同的代理服务器。

### 主要功能

- **代理节点自动获取**：从订阅 URL 获取最新的代理节点列表
- **多端口代理分发**：每个代理节点分配独立端口，提高可用性和灵活性
- **定时自动更新**：按设定的时间间隔自动更新代理配置
- **API 接口支持**：提供 HTTP 接口查询可用节点和刷新配置
- **基本认证保护**：所有接口和管理页面都有用户名密码保护

## 部署步骤

### 前置要求

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 获取代码

```bash
git clone https://github.com/Crpto999/proxy_pool_adrien.git
cd proxy_pool_adrien
```

### 配置环境变量

项目根目录下需要创建 `.env` 文件，配置以下环境变量：

```
# API和管理界面的用户名
USERNAME=

# API和管理界面的密码
PASSWORD=

# 代理节点订阅地址，系统会定期从这个URL获取最新的代理服务器列表
SUBSCRIBE_URL=

# 用于测试代理节点延迟的目标网址
LATENCY_TEST_URL=

# 容器时区设置
TZ=

# 代理端口分配的起始端口号
START_PORT=

# 代理端口分配的结束端口号
END_PORT=

# 代理节点列表自动更新间隔(小时)
UPDATE_INTERVAL=

# Clash Meta控制接口的访问密钥
CLASH_META_SECRET=
```

### 构建和启动容器

```bash
# 构建容器
docker-compose build

# 启动容器
docker-compose up -d
```

### 查看容器运行状态

```bash
docker-compose ps
```

## 使用方法

### API 接口

系统提供以下 API 接口，所有接口都需要 HTTP 基本认证：

1. **获取代理节点列表**

   ```
   GET http://your-server-ip:20000/nodes
   ```

   返回示例：
   ```json
   [
     {"proxy": "节点名称1", "port": 20001},
     {"proxy": "节点名称2", "port": 20002},
     {"proxy": "节点名称3", "port": 20003}
   ]
   ```

2. **手动刷新配置**

   ```
   GET http://your-server-ip:20000/refresh
   ```

   返回示例：
   ```json
   {"message": "配置已刷新。"}
   ```

3. **检查 API 状态**

   ```
   GET http://your-server-ip:20000/
   ```

   返回示例：
   ```json
   {"message": "API 正在运行。"}
   ```

### 代理使用方法

系统会为每个代理节点分配一个独立的端口，端口号从 `START_PORT` 开始递增。您可以通过 API 接口获取当前可用的代理节点及其对应的端口号。

使用示例：

1. **SOCKS5 代理**：
   - 主机：`your-server-ip`
   - 端口：`2000X`（根据 API 返回的端口）
   - 用户名：不需要
   - 密码：不需要

2. **HTTP 代理**：
   - 主机：`your-server-ip`
   - 端口：`2000X`（根据 API 返回的端口）
   - 用户名：不需要
   - 密码：不需要

### Clash Meta 控制面板

Clash Meta 提供了一个 Web UI 控制面板，可以查看代理状态、切换节点等：

```
http://your-server-ip:19999/ui
```

访问时需要输入在 `.env` 文件中设置的 `CLASH_META_SECRET` 值。

## 配置说明

主要环境变量说明：

| 环境变量 | 说明 |
|---------|------|
| USERNAME | API和管理界面的用户名 |
| PASSWORD | API和管理界面的密码 |
| SUBSCRIBE_URL | 代理节点订阅地址 |
| START_PORT | 代理端口分配的起始端口号 |
| END_PORT | 代理端口分配的结束端口号 |
| UPDATE_INTERVAL | 代理节点列表自动更新间隔(小时) |
| CLASH_META_SECRET | Clash Meta控制接口的访问密钥 |

## 更新代理配置

系统会根据 `UPDATE_INTERVAL` 设置的时间间隔自动更新代理配置。您也可以通过 API 手动触发更新：

```
GET http://your-server-ip:20000/refresh
```

## 常见问题

### 1. 无法连接到代理

- 确认服务器防火墙已开放代理端口范围（`START_PORT` 到 `END_PORT`）
- 确认容器正常运行：`docker-compose ps`
- 检查日志是否有错误信息：`docker-compose logs`

### 2. 代理速度慢或不稳定

- 通过 API 获取最新节点列表并尝试不同节点
- 手动刷新配置以获取最新代理：`GET http://your-server-ip:20000/refresh`

### 3. API 返回 401 错误

- 确认使用了正确的用户名和密码（在 `.env` 文件中设置）
- 检查认证头格式是否正确

## 日志查看

查看容器日志：

```bash
docker-compose logs -f
```

## 停止服务

```bash
docker-compose down
``` 

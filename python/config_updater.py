# config_updater.py

import requests
import yaml
import os
import time
import argparse

# 定义自定义字符串类
class QuotedString(str):
    pass

# 定义表示器，强制使用双引号
def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

# 注册自定义表示器
yaml.add_representer(QuotedString, quoted_presenter)

# 读取环境变量
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL")
START_PORT = int(os.getenv("START_PORT"))
END_PORT = int(os.getenv("END_PORT"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 12))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SECRET = os.getenv("CLASH_META_SECRET")

CONFIG_PATH_MULTI = "/app/mihomo/config/config_multi.yaml"
# 外部控制器配置
CLASH_EXTERNAL_CONTROLLER_MULTI = "http://0.0.0.0:19999"


def wait_for_external_controller(max_retries=30, delay=2):
    headers = {}
    if SECRET:  # 确保 SECRET 已设置
        headers["Authorization"] = f"Bearer {SECRET}"

    for _ in range(max_retries):
        try:
            response = requests.get(f"{CLASH_EXTERNAL_CONTROLLER_MULTI}/version", headers=headers)
            if response.status_code == 200:
                print("External controller 已就绪。")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print("等待 external controller 就绪...")
        time.sleep(delay)
    print("External controller 启动超时。")
    return False

def generate_config_multi():
    print("正在生成 config_multi 配置文件...")

    try:
        response = requests.get(SUBSCRIBE_URL)
        response.raise_for_status()
        yaml_data = yaml.safe_load(response.text)
        proxies = yaml_data.get("proxies", [])

        if not proxies:
            print("未获取到任何代理节点，检查订阅链接是否正确。")
            return

        # 公共部分配置
        config_multi = {
            "port": 7890,
            "socks-port": 7891,
            "mixed-port": 18313,
            "mode": "Global",
            "allow-lan": True,
            "external-controller": CLASH_EXTERNAL_CONTROLLER_MULTI.split("://")[1],
            "external-ui": "/app/mihomo/ui",
            "keep-alive-interval": 30,
            "log-level": "info",
            "global-client-fingerprint": "random",
            "secret": SECRET,
            "authentication": [QuotedString(f"{USERNAME}:{PASSWORD}")],
            "skip-auth-prefixes": [
                "127.0.0.1/8",     # 本地回环网络
                "10.0.0.0/8",       # 私有网络A类
                "172.16.0.0/12",    # 私有网络B类
                "192.168.0.0/16",   # 私有网络C类
                "172.18.0.0/16"     # Docker默认网段
            ],
            "profile": {
                "store-selected": True,
                "store-fake-ip": True
            },
            "dns": {
                "enable": True,
                "enhanced-mode": "fake-ip",
                "fake-ip-range": "198.18.0.1/16",
                "default-nameserver": ["8.8.8.8"],
                "nameserver": ["https://doh.pub/dns-query"]
            },
            "proxies": proxies,
            "listeners": []
        }

        # 为每个代理节点生成独立的监听器配置
        for i, proxy in enumerate(proxies):
            port = START_PORT + i
            if port > END_PORT:
                break
            listener = {
                "proxy": proxy.get("name", f"proxy_{i}"),
                "name": f"mixed{i}",
                "type": "mixed",
                "port": port,
            }
            config_multi["listeners"].append(listener)

        # 写入 config_multi 配置文件
        with open(CONFIG_PATH_MULTI, "w", encoding="utf-8") as f:
            yaml.dump(config_multi, f, allow_unicode=True, sort_keys=False)

        print("config_multi 配置文件生成成功。")

    except Exception as e:
        print(f"生成 config_multi 配置文件时出错：{e}")
        raise e


def reload_config_multi():
    headers = {}
    if SECRET:
        headers["Authorization"] = f"Bearer {SECRET}"

    # 设置请求体数据，将新的配置路径传递到 "path" 字段
    data = f'{{"path": "{CONFIG_PATH_MULTI}", "payload": ""}}'

    try:
        # 发送 PUT 请求以重载配置
        reload_response_multi = requests.put(
            f"{CLASH_EXTERNAL_CONTROLLER_MULTI}/configs?force=true",
            headers=headers,
            data=data
        )
        if reload_response_multi.status_code == 204:
            print("config_multi 配置重载成功。")
        else:
            print("config_multi 配置重载失败，状态码：", reload_response_multi.status_code)
            print("返回内容：", reload_response_multi.text)  # 输出返回的详细信息

    except Exception as e:
        print(f"重载 config_multi 配置时出错：{e}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="配置更新器")
    parser.add_argument('--generate', action='store_true', help='仅生成配置文件')
    parser.add_argument('--reload', action='store_true', help='仅重载配置文件')
    args = parser.parse_args()

    if args.generate:
        generate_config_multi()
    elif args.reload:
        reload_config_multi()

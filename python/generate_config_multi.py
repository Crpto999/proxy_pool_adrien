# generate_config_multi.py

import schedule
import time
import threading
from config_updater import generate_config_multi, reload_config_multi, UPDATE_INTERVAL

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def update_and_reload_config():
    # 先获取最新配置
    generate_config_multi()
    # 再重载配置
    reload_config_multi()

if __name__ == "__main__":

    # 定时任务：先执行配置获取，再执行配置更新
    schedule.every(UPDATE_INTERVAL).hours.do(update_and_reload_config)

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # 保持主线程运行
    while True:
        time.sleep(1)

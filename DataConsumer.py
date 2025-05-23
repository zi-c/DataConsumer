import os
import random
import requests
import time
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def clear_screen():
    # 清屏指令
    if os.name == 'nt':
        # Windows
        os.system('cls')
    else:
        # Mac和Linux
        os.system('clear')


def get_filename_from_url(url):
    # 使用 urlparse 解析 URL
    parsed_url = urlparse(url)
    # 从 URL 的 path 中提取文件名
    filename = os.path.basename(parsed_url.path)
    return filename


# 下载文件函数（去掉限速和单个文件统计）
def download_file(url, headers, chunk_size=5*1024*1024, timeout=30):
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()

        total_downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                total_downloaded += len(chunk)

        return total_downloaded

    except requests.exceptions.RequestException as e:
        print(f"下载错误 {url}: {e}")
        return 0


# 下载任务执行的函数，包含线程锁
def download_task(url, headers, chunk_size, timeout, total_downloaded_lock, total_downloaded, count):
    downloaded = download_file(url, headers, chunk_size, timeout)
    with total_downloaded_lock:
        total_downloaded[0] += downloaded
    
    print(f"Success {get_filename_from_url(url)} - {downloaded / 1024 / 1024:.2f} MB")
    with total_downloaded_lock:
        print(f"Count: {count} - Total: {total_downloaded[0] / 1024 / 1024:.2f} MB\n")


# 主程序，读取 target.txt 中的 URL 并下载
def main(target_file, user_agents, chunk_size, timeout, max_threads=5, repeat_count=5):

    # 设置请求头
    headers = { "User-Agent": random.choice( user_agents ) }

    # 读取文件中的 URL
    try:
        with open(target_file, "r") as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"错误: {target_file} 文件不存在！")
        return

    total_downloaded = [0]  # 总下载量，使用列表是为了在多线程中共享
    total_downloaded_lock = threading.Lock()  # 锁，用于多线程中同步访问总下载量

    # 使用线程池执行下载任务
    with ThreadPoolExecutor(max_threads) as executor:
        futures = []
        count = 1  # 下载计数
        for _ in range(repeat_count):  # 按照 repeat_count 重复提交任务
            for url in urls:
                futures.append(executor.submit(download_task, url, headers, chunk_size, timeout, total_downloaded_lock, total_downloaded, count))
                count += 1

        # 等待所有线程完成
        for future in as_completed(futures):
            future.result()  # 获取线程的执行结果
    
    print("所有任务已完成！\n")


if __name__ == "__main__":
    # 配置参数部分
    target_file = "target.txt"      # 包含 URL 的文件路径
    chunk_size = 5 * 1024 * 1024    # 每次下载的块大小 5MB
    timeout = 30                  # 设置超时时间为 30 秒（请根据文件大小、网络速度、线程数量进行调整）
    max_threads = 5                 # 并发下载任务数
    repeat_count = 5                # 提交下载任务次数

    # UA库
    user_agents1 = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.4 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36 Edg/113.0.1774.50",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.130 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16_4 Mobile/15E148 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/18.0 Chrome/113.0.5672.130 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36 OPR/99.0.4788.72",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36 Edg/113.0.1774.50",
        "Mozilla/5.0 (iPad; CPU OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16_4 Mobile/15E148 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.130 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:113.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36 Edg/113.0.1774.50",
        "Mozilla/5.0 (iPad; CPU OS 16_3_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-F936U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.130 Mobile Safari/537.36 OPR/63.0.3216.58696",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15C153 Safari/604.1"
    ]


    # Info部分
    print(" --------------------------------------------------\n ")
    print("     欢迎使用 ZiChen's Data Consumer\n")
    print("     本工具旨在通过多线程下载指定文件测试当前")
    print("     宽带/流量的稳定性，以及途径相关设备的稳定性。\n")
    print("     Release Version: 1.1.0")
    print("     Release Date: 202050523\n")
    print(" --------------------------------------------------\n ")

    # EULA部分
    print(" 本工具仅供测试使用，确保有权进行下载测试，任何不良后果均由使用者承担。\n")
    input(" 按任意键即视为同意上述内容，如不同意请停止使用")

    clear_screen()

    # 运行主程序
    main(target_file, user_agents1, chunk_size, timeout, max_threads, repeat_count)

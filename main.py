import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome import service as fs
import pytz
import yaml
import concurrent.futures
from urllib.parse import urlparse

# タイムゾーンを環境変数から取得する
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")

# ChromeDrive のディレクトリ
# CHROMEDRIVER = os.environ.get("CHROMEDRIVER", "/opt/chrome/chromedriver")


def load_config() -> List[Dict]:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)

    # 設定ファイルの形式が正しいかどうかを確認する
    if not isinstance(config, list):
        raise ValueError('Invalid format: The configuration file should be a list of dictionaries.')

    for c in config:
        if not isinstance(c, dict):
            raise ValueError('Invalid format: Each configuration should be a dictionary.')

        # URL と保存パスが設定されているかどうかを確認する
        if 'url' not in c:
            raise ValueError('Invalid format: URL is not specified in the configuration.')
        if 'path' not in c:
            raise ValueError('Invalid format: Save path is not specified in the configuration.')

        # URL の書式が正しいかを確認する
        url = c['url']
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f'Invalid URL: {url}')

        # 保存パスが存在するかどうかを確認する
        path = c['path']
        if not os.path.isdir(path):
            try:
                # 存在しなかったら作成
                os.makedirs(path)
            except OSError as e:
                raise ValueError(f'Failed to create directory "{path}": {str(e)}')

    return config

def get_screenshot(url: str, path: str, interval) -> None:
    """
    指定された URL のスクリーンショットを定期的に取得する。

    Args:
        url (str): スクリーンショットを取得する Web ページの URL。
        path (str): スクリーンショットを保存するディレクトリのパス。
        interval (int): スクリーンショットを取得する間隔（秒数）。
    """
    # ブラウザを起動する
    # chrome_service = fs.Service(executable_path=CHROMEDRIVER) 
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--incognito')
    # options.add_argument('--enable-automation')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--disable-browser-side-navigation')
    # options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    print(f"start thread. {url}, {path}, {interval}")
        
    # スクリーンショットを定期的に取得する
    while True:
        # スクリーンショットを保存するファイルパスを作成する
        now = datetime.now(pytz.timezone(TIME_ZONE))
        filename = f"{now:%Y%m%d_%H%M%S}.png"
        filepath = os.path.join(path, filename)
        
        # スクリーンショットを取得して保存する
        driver.get(url)

        page_width = driver.execute_script('return document.body.scrollWidth')
        page_height = driver.execute_script('return document.body.scrollHeight')        
        driver.set_window_size(page_width, page_height)

        driver.implicitly_wait(10)

        driver.save_screenshot(filepath)
        print(f"Screenshot saved to {filepath}")
        
        # 指定された秒数待つ
        time.sleep(interval)


def main() -> None:
    """
    設定ファイルを読み込んで、指定されたURLのスクリーンショットを定期的に取得する。
    """

    # 保存先のパスを設定ファイルから取得する
    config = load_config()

    # スクリーンショットを取得するジョブを作成する
    jobs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(config)) as executor:
        for c in config:
            url = c["url"]
            path = c["path"]
            interval = c.get("interval", 3600)
            job = executor.submit(get_screenshot, url, path, interval)
            jobs.append(job)

    # 全ジョブが終了するまで待つ
    for job in concurrent.futures.as_completed(jobs):
        try:
            job.result()
        except Exception as exc:
            print(f"Screenshot job failed with exception: {exc}")
        
        
if __name__ == "__main__":
    main()
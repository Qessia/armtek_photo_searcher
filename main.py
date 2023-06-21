import signal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from sys import exit
import requests
import pandas as pd
import random
import json
import keyboard


with open('config.json', encoding='utf-8') as f:
    data = json.load(f)

API_KEY = data['Imgbb_API_key']
CSV_TABLE = data['Table']['Path_to_file']
COL_NAME = data['Table']['Column_names']
COL_MANUF = data['Table']['Column_manufacturer']
COL_URL = data['Table']['Column_urls']

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
]


def publish(url, name):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    pload = {'image': url}
    r = requests.post(f'https://api.imgbb.com/1/upload?key={API_KEY}&name={name}', data=pload, headers=headers)
    return ('success', r.json()['data']['url']) if r.status_code == 200 else ('BAD_URL', 'BAD_URL')


class Picfinder:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-xss-auditor')
        chrome_options.add_argument('--log-level=1')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.waiter = webdriver.support.wait.WebDriverWait(self.driver, 10)

    def __del__(self):
        self.driver.quit()

    def find_picture(self, query):
        self.driver.get("https://www.google.com/imghp")
        search_box = self.driver.find_element(by=By.NAME, value="q")
        search_box.send_keys(query)
        search_box.submit()

        first_image = self.driver.find_element(by=By.CSS_SELECTOR, value=".rg_i")
        first_image.click()

        self.waiter.until(
            ec.visibility_of_element_located((By.XPATH, "//c-wiz/div/div/div/div/div/a/img[contains(@src, 'https')]")))
        full_size_image = self.driver.find_element(by=By.XPATH,
                                                   value="//c-wiz/div/div/div/div/div/a/img[contains(@src, 'https')]")
        url = full_size_image.get_attribute('src')
        return url


def main():
    df = pd.read_csv(CSV_TABLE, sep=';', encoding='utf-8', low_memory=False)
    len_df = len(df)

    finder = Picfinder()

    signal.signal(signal.SIGINT, signal.default_int_handler)

    for index, row in df.iterrows():
        if keyboard.is_pressed("x"):
            df.to_csv(CSV_TABLE, sep=';', encoding='utf-8', index=False)
            del finder
            print('Work stopped')
            exit(0)
        try:
            if isinstance(row[COL_URL], str):
                print(f'filled: ', end='')
                continue
            response, text = publish(finder.find_picture(f'{row[COL_NAME]} {row[COL_MANUF]}'), row[COL_NAME])
            df.at[index, COL_URL] = text
        except KeyboardInterrupt:
            df.to_csv(CSV_TABLE, sep=';', encoding='utf-8', index=False)
            del finder
            print('Work stopped')
            exit(0)
        except Exception:
            df.at[index, COL_URL] = 'BAD_URL'
            print(f'BAD_URL: ', end='')
        else:
            print(f'{response}: ', end='')
        finally:
            print(f'[{index + 1} / {len_df}] {row[COL_NAME]} {row[COL_MANUF]}')

    df.to_csv(CSV_TABLE, sep=';', encoding='utf-8', index=False)
    del finder
    print('COMPLETED')


if __name__ == '__main__':
    main()

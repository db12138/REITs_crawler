from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import ujson
from tqdm import tqdm
import time, base64

def get_driver():
    url = "http://www.sse.com.cn/reits/announcements/"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_driver = './chromedriver.exe'              #chromedriver的文件位置, 自行百度配置
    driver = webdriver.Chrome(executable_path=chrome_driver,
                            chrome_options=chrome_options)

    driver.get(url)
    return driver


def get_files_infos_in_cur_page(page_num,driver):
    cmd = f"javascript:showReitsAs({page_num});"
    driver.execute_script(cmd)
    print("sleeping 8s")
    time.sleep(8)
    trs = driver.find_elements(By.TAG_NAME,'tr')
    all_file_infos = []
    for each_file_info in trs:
        try:
            cur_tds = each_file_info.find_elements(By.TAG_NAME,'td')
            # print(cur_tds)
            cur_file_info = {}

            code_info = cur_tds[0]
            file_info = cur_tds[1].find_element(By.TAG_NAME,'div').find_element(By.TAG_NAME,'a')
            date_info = cur_tds[2]

            cur_file_info["code"] = code_info.text
            cur_file_info["file_name"] = file_info.get_attribute('text')
            cur_file_info["file_href"] = file_info.get_attribute('href')
            cur_file_info["release_date"] = date_info.text
            print(cur_file_info)
            all_file_infos.append(cur_file_info)
        except Exception as e:
            print(f"error:{e}")
        
        print("---------")
    return all_file_infos

def read_json():
    files_info = ujson.load(open("上交所REITs信息.json",'r'))
    ujson.dump(files_info,open("上交所REITs信息_2.json",'w'),ensure_ascii=False)
    # print(files_info)
if __name__ == "__main__":
    # driver = get_driver()
    # all_result = []
    # for page_num in tqdm(range(1,16)):
    #     page_info = get_files_infos_in_cur_page(page_num,driver)
    #     all_result.append(page_info)

    # ujson.dump(all_result,open("上交所REITs信息.json",'w'))
    read_json()
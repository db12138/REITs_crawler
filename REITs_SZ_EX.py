import imp
from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import requests
import ujson
from tqdm import tqdm
import time, base64

def sleeping(seconds,purpose="waiting"):
    print(f"sleeping {seconds}s for {purpose} ")
    time.sleep(seconds)
def get_driver():
    url = "https://reits.szse.cn/disclosure/index.html"
    chrome_options = Options()
    chrome_options.headless = False
    # chrome_options.add_argument('--headless')
    chrome_driver = './chromedriver.exe'              #chromedriver的文件位置, 自行百度配置
    driver = webdriver.Chrome(executable_path=chrome_driver,
                            chrome_options=chrome_options)
    driver.get(url)
    sleeping(4,"waiting load page")
    return driver

def set_search_time(driver):
    start_date = "2015-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    driver.find_element(By.CLASS_NAME,"input-left").send_keys(start_date)
    driver.find_element(By.CLASS_NAME,"input-right").send_keys(end_date)

    driver.find_element(By.ID,"query-btn").click()
    sleeping(4,"fill date")


def get_files_infos_in_cur_page(page_num,driver):
    # cmd = f"javascript:showReitsAs({page_num});"
    # driver.execute_script(cmd)
    # print("sleeping 8s")
    # time.sleep(8)
    trs = driver.find_elements(By.TAG_NAME,'tr')
    all_file_infos = []
    for each_file_info in trs:
        try:
            cur_tds = each_file_info.find_elements(By.TAG_NAME,'td')
            print(len(cur_tds))
            cur_file_info = {}

            code_info = cur_tds[0]
            print(code_info.text)
            file_infos = cur_tds[1].find_element(By.TAG_NAME,'div').find_elements(By.TAG_NAME,"span")
            file_name = file_infos[0].text
            file_down_button = file_infos[2].click()
            print(f"len name:{len(file_infos)}")
            print(f"name.text:{file_name}")
            sleeping(2,"dowloading")
            
            date_info = cur_tds[2]
            print(date_info.text)
            assert 0
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
    driver = get_driver()
    set_search_time(driver)
    get_files_infos_in_cur_page(1,driver)

    sleeping(100000)
    # all_result = []
    # for page_num in tqdm(range(1,16)):
    #     page_info = get_files_infos_in_cur_page(page_num,driver)
    #     all_result.append(page_info)

    # ujson.dump(all_result,open("上交所REITs信息.json",'w'))
    #read_json()
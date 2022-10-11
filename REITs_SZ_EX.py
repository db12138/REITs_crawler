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
    try:
        page_buttons = driver.find_element(By.XPATH,f"//a[@data-pi={page_num-1}]")   
        page_buttons.click()
        sleeping(4,"page change")
        print(f"转到第{page_num}页")
    except Exception as e:
        print(f"error:{e}, no such page {page_num}")
        assert 0


    all_file_infos = []
    trs = driver.find_elements(By.TAG_NAME,'tr')
    
    for each_file_info in tqdm(trs):
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
            cur_file_info["file_name"] = file_name
            # cur_file_info["file_href"] = file_info.get_attribute('href')
            cur_file_info["release_date"] = date_info.text
            print(cur_file_info)
            all_file_infos.append(cur_file_info)
        except Exception as e:
            print(f"error:{e}")
        
        print("---------")
    return all_file_infos

def read_json():
    files_info = ujson.load(open("深交所REITs信息.json",'r'))
    ujson.dump(files_info,open("深交所REITs信息_2.json",'w'),ensure_ascii=False)
    # print(files_info)

def check_if_dumped(all_file_name="深交所REITs信息.json"):
    files_info = ujson.load(open(all_file_name,'r'))
    page_num = len(files_info)

    name_pagenum_map = {}

    for i in tqdm(range(page_num)):
        cur_page_info = files_info[i]
        # print(cur_page_info[0].keys()) #['code', 'file_name', 'file_href', 'release_date'])
        for each_file in tqdm(cur_page_info):
            save_file_name = f"发布日_{each_file['release_date']}_{each_file['file_name']}.pdf"
            if save_file_name not in name_pagenum_map:
                name_pagenum_map[save_file_name] = i 
            else:
                print(f"{save_file_name}  already in front page, cur page:{i} miss")
    page_set = []
    for name,page in name_pagenum_map.items():
        if page not in page_set:
            page_set.append(page)
    print(page_set)

if __name__ == "__main__":
    driver = get_driver()
    set_search_time(driver)
    all_result = []
    for page_num in tqdm(range(1,7)):
        page_info = get_files_infos_in_cur_page(page_num,driver)
        all_result.append(page_info)

    save_download_history_name = "深交所REITs信息.json"
    ujson.dump(all_result,open(save_download_history_name,'w'),ensure_ascii=False)
    check_if_dumped(save_download_history_name)
    sleeping(100)
    # all_result = []
    # for page_num in tqdm(range(1,16)):
    #     page_info = get_files_infos_in_cur_page(page_num,driver)
    #     all_result.append(page_info)

    # ujson.dump(all_result,open("上交所REITs信息.json",'w'))
    #read_json()
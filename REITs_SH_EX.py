from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import ujson
import os
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
    for i in range(5):
        driver.execute_script(cmd)
        print("sleeping 2s")
        time.sleep(2)
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
def download_from_url(cur_url,file_name,dir_path,already_downloaded_files):    
    if file_name in already_downloaded_files:
        print(f"在已经下载的 {len(already_downloaded_files)} 中")
        return
    response = requests.get(cur_url)
    # Save the PDF
    if response.status_code == 200:
        with open( os.path.join(dir_path,file_name), "wb") as f:
            f.write(response.content)
    else:
        print(response.status_code)
def download_all_files(all_file_name="上交所REITs信息_3.json",dir_path="上交所公告"):
    already_downloaded_files = []
    for _,_,filenames in os.walk(dir_path):
        already_downloaded_files.extend(filenames)

    files_info = ujson.load(open(all_file_name,'r'))
    page_num = len(files_info)
    for i in tqdm(range(page_num)):
        cur_page_info = files_info[i]
        # print(cur_page_info[0].keys()) #['code', 'file_name', 'file_href', 'release_date'])
        for each_file in tqdm(cur_page_info):
            save_file_name = f"发布日_{each_file['release_date']}_{each_file['file_name']}.pdf"
            download_from_url(each_file["file_href"],save_file_name,dir_path,already_downloaded_files)        
            # print(each_file["file_href"])
def test_glob():
    cnt = 0
    all_download_files = []
    for dir_path,dir_names,filenames in os.walk("./上交所公告/"):
        cnt+= 1
        print(filenames)
    print(cnt)

def check_if_dumped(all_file_name="上交所REITs信息_3.json"):
    files_info = ujson.load(open(all_file_name,'r'))
    page_num = len(files_info)

    name_pagenum_map = {}
    cnt = 0
    for i in tqdm(range(page_num)):
        cur_page_info = files_info[i]
        cnt += len(cur_page_info)
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
    print(f"all_file nums :{cnt}")

if __name__ == "__main__":
    # driver = get_driver()
    # all_result = []
    # for page_num in tqdm(range(1,16)):
    #     page_info = get_files_infos_in_cur_page(page_num,driver)
    #     all_result.append(page_info)

    # ujson.dump(all_result,open("上交所REITs信息_3.json",'w'),ensure_ascii=False)
    #check_if_dumped("上交所REITs信息_3.json")
    #test_glob()
    download_all_files("上交所REITs信息_3.json")
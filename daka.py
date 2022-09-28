from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import time, base64
# https://authserver.nju.edu.cn/authserver/login?service=http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do
service = 'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do'
url = f'https://authserver.nju.edu.cn/authserver/login?service={service}'
base_url = 'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do'
    
username = "MF20330001 " # ehall 账号
password = "" # ehall 密码
loc = "江苏省南京市栖霞区金大路" # 地点
from PIL import Image

def get_captcarCode(image_data):
    # encoding:utf-8
    # AK 为百度官网获取的AK， SK 为官网获取的SK
    AK = 'Yd475Q0nwRn8URUwZgTsyxw9'
    SK = 'WoTBsz3gvs4oTwTBQYdVpbS0GSVLyxKV'
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={AK}&client_secret={SK}'
    response = requests.get(host)
    if response:
        access_token = response.json()['access_token']
        params = {"image": image_data}
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response and 'words_result' in response.json():
            word = response.json()['words_result'][0]['words']
            return word.replace(' ', '')
    return None

def main():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_driver = './chromedriver.exe'              #chromedriver的文件位置, 自行百度配置
    b = webdriver.Chrome(executable_path=chrome_driver,
                         chrome_options=chrome_options)

    haveDone = False
    while not haveDone:
        b.get(url)
        b.find_element_by_id('username').send_keys(username)
        time.sleep(1)
        b.find_element_by_id('password').send_keys(password)
        image = b.find_element_by_id('captchaImg')
        image_data = image.screenshot_as_png
        with open('./tmp.png', 'wb') as f:
            f.write(image_data)
        # im = Image.open('./tmp.png')
        # im.show()
        captchaResponse = get_captcarCode(base64.b64encode(image_data))
        if captchaResponse and len(captchaResponse) == 4:
            haveDone = True
        print(f'识别的二维码：{captchaResponse}')
        # captchaResponse = input('请输入验证码')
        b.find_element_by_id('captchaResponse').send_keys(captchaResponse)
        b.find_element_by_css_selector("button[type='submit']").click()

    content = b.find_element_by_tag_name("pre")
    res = json.loads(content.text)
    time_formt = "%b %d, %Y %H:%M:%S %p"
    data = sorted(res['data'], key=lambda x: time.strptime(x['CJSJ'], time_formt), reverse=True)
    
    wid = data[0]['WID']

    print(wid)
    
    target_url = f'{base_url}?WID={wid}&CURR_LOCATION={loc}&IS_TWZC=1&IS_HAS_JKQK=1&JRSKMYS=1&JZRJRSKMYS=1'

    cookies = ';'.join(
        [item['name'] + '=' + item['value'] for item in b.get_cookies()])

    headers = {
        'Cookie':
        cookies
    }
    resp = requests.request("GET", target_url, headers=headers)
    print(json.loads(resp.text))
    b.quit()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(24*60*60)

    # import base64
    # f = open('./tmp.png', 'rb')
    # img = base64.b64encode(f.read())
    # get_captcarCode(img)
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

################################################
#################### Config ####################
################################################
with open("./config.json", "r") as cf:
    config = json.loads(cf.read())

    DISCORD_EMAIL = config["discord_email"]
    DISCORD_PASSWORD = config["discord_password"]

    GUILD_ID = config["guild_id"]
    CHANNEL_ID = config["channel_id"]

    GET_IMAGES_AMOUNT = int(input("請輸入預獲取的圖片數量: "))
    PATH_NAME = config["save_pathname"]
################################################


# Start code
program_start_time = time.time()

options = Options()
options.add_argument("--disable-notifications")  # 禁止瀏覽器跳出通知
options.add_argument("headless")  # 不啟動瀏覽器畫面, 在後台運行爬蟲

print("正在開啟虛擬瀏覽器中...")
chrome = webdriver.Chrome(r"C:\Users\soupm\OneDrive\文件\程式學習\Python\crawler\chromedriver.exe", options=options)
chrome.set_window_position(0, 0)
chrome.set_window_size(1920, 1080)
print("正在進入Discord登入頁面...")
chrome.get("https://discord.com/login")

email_input = chrome.find_element_by_name("email")
password_input = chrome.find_element_by_name("password")
login_button = chrome.find_element_by_css_selector("button.lookFilled-1Gx00P.colorBrand-3pXr91")
print("正在輸入帳號...")
email_input.send_keys(DISCORD_EMAIL)
print("正在輸入密碼...")
password_input.send_keys(DISCORD_PASSWORD)
print("正在登入中...")
login_button.click()

time.sleep(5)
print("已成功登入Discord!")

chrome.get(f"https://discord.com/channels/{GUILD_ID}/{CHANNEL_ID}")

print("正在跳轉至群組頻道頁面...")
time.sleep(8)
print("已成功進入群組頻道頁面!")

soup = BeautifulSoup(chrome.page_source, "html.parser")

message_body = chrome.find_element_by_css_selector(".scrollerInner-2YIMLh")
message_body.click()  # 點擊訊息視窗，以便可以使用 Arrow_up 進行頁面滾動
time.sleep(1)
print("開始獲取貼文資訊...")
start_time = time.time()

postSelect = "a.anchor-3Z-8Bb.anchorUnderlineOnHover-2ESHQB.imageWrapper-2p5ogY.imageZoom-1n-ADA.clickable-3Ya1ho.embedWrapper-lXpS3L"
postList = soup.select(postSelect)
postCount = len(postList)

postsSet = set()
noUpdateCount = 0
lastPostCount = postCount

while postCount < GET_IMAGES_AMOUNT:
    SCROLL_SPEED = 200
    for _ in range(SCROLL_SPEED):
        message_body.send_keys(Keys.ARROW_UP)
    soup = BeautifulSoup(chrome.page_source, "html.parser")
    postList = soup.select(postSelect)
    postsSet.update(postList)
    postCount = len(postsSet)
    print(f"({postCount}/{GET_IMAGES_AMOUNT}) 正在載入獲取更多貼文資訊...")

    if lastPostCount == postCount:
        noUpdateCount += 1
    else:
        noUpdateCount = 0
    lastPostCount = postCount

    if noUpdateCount >= 5:
        print(f"※已載入完該頻道的所有貼文資訊了，無法載入到目標量 {GET_IMAGES_AMOUNT}")
        break

end_time = time.time()
print(f"花費了 {end_time - start_time} 秒將所有貼文載入完畢，共獲取了 {postCount} 個貼文資訊\n開始儲存圖片...\n")

if PATH_NAME not in os.listdir("./"):
    os.mkdir(PATH_NAME)
    print(f"正在創建資料夾 {PATH_NAME}")
    time.sleep(1)

start_time = time.time()
postList = list(postsSet)
# postList.sort(key=lambda s: re.search(r"/\d+/(\d+)/.+\.\w+", s["href"]).group(1))
img_count = 0

for post in postList:
    img_url = post.get("href")
    search_result = re.search(r"/\d+/(\d+)/(.+)\.\w+", img_url)
    img_id = ""
    if search_result is not None:
        img_id = search_result.group(1)
    else:
        img_id = re.search(r".+/(.+)\.\w+", img_url).group(1).replace(".", "") + f"_{img_count}"

    file_name = f"{img_id}.png"

    with open(f"./{PATH_NAME}/{file_name}", "wb") as pf:
        pf.write(requests.get(img_url).content)
        pf.close()
    img_count += 1
    print(f"({img_count}/{postCount}) {img_url} 已成功儲存至 {file_name}!")

end_time = time.time()
print(f"花費了 {end_time - start_time} 秒將所有圖片儲存完畢!")

program_end_time = time.time()
print("=" * 60)
print(f"此程式總共執行了 {program_end_time - program_start_time} 秒")

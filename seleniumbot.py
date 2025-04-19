from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import random
import time
import pickle
import os

# 配置 ChromeDriver 路径
CHROMEDRIVER_PATH = r'D:\xiangmu\.venv\Scripts\chromedriver.exe'

# Cookies 文件路径
COOKIES_PATH = r'D:\xiangmu\cookies.pkl'

# 固定的 20 条英语话语
FIXED_MESSAGES = [
    "Hey, just checking in — how’s everyone’s Momentum streak going?",
    "Anyone else loving the new Momentum updates? They’re kinda cool!",
    "I’m just here to say Momentum is the best thing since sliced bread lol.",
    "Yo, anyone got tips for keeping up with Momentum daily challenges?",
    "Just a random thought — Momentum’s UI is so sleek, right?",
    "Hey team, let’s keep the Momentum vibes strong this week!",
    "I might be obsessed with Momentum’s leaderboards… anyone else?",
    "Quick shoutout to the Momentum crew for keeping things fun!",
    "Does anyone else check Momentum first thing in the morning or is that just me?",
    "I’m so pumped for the next Momentum event, whenever that is haha.",
    "Just saying, Momentum makes my day a bit brighter.",
    "Anyone else feel like Momentum is their daily motivation buddy?",
    "Hey, what’s your favorite Momentum feature? I’m curious!",
    "I keep forgetting to log my Momentum tasks… oops.",
    "Momentum’s notifications are lowkey my favorite part of the day.",
    "Just a random hi to all the Momentum fans in here!",
    "I’m loving the Momentum community — you guys rock!",
    "Anyone else think momentum should add more fun badges?",
    "Hey, let’s all share our Momentum progress — I’m at level 5!",
    "Not much to say, just wanted to spread some Momentum love!"
]

# 配置 Chrome 选项
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')

# 初始化浏览器
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 打开 Discord 频道
driver.get("https://discord.com/channels/948033443483254845/1027161980970205225")

# 尝试加载 Cookies
def load_cookies():
    if os.path.exists(COOKIES_PATH):
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        print("已加载 Cookies")
        return True
    return False

# 保存 Cookies
def save_cookies():
    pickle.dump(driver.get_cookies(), open(COOKIES_PATH, "wb"))
    print("已保存 Cookies")

# 检查登录状态
def check_login():
    try:
        # 检查是否加载到频道页面
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
        # 进一步检查当前 URL 是否为频道页面
        current_url = driver.current_url
        if "channels/948033443483254845/1027161980970205225" in current_url:
            print("已成功加载频道页面")
            return True
        else:
            print(f"未加载到频道页面，当前 URL: {current_url}")
            return False
    except:
        print("未找到聊天输入框，可能未登录或页面未加载")
        return False

# 登录 Discord
if not load_cookies() or not check_login():
    print("请登录 Discord（可能需要手动操作）...")
    driver.quit()
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://discord.com/channels/948033443483254845/1027161980970205225")
    print("请通过二维码或用户名/密码登录，登录后等待频道页面加载完成...")
    input("登录完成后按 Enter 继续...")
    # 确保频道页面加载完成
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
        print("频道页面已加载")
    except:
        print("频道页面未加载，请检查登录状态或网络")
        driver.quit()
        exit()
    save_cookies()
    # 移除此处的 driver.quit()
    # 继续使用当前浏览器，无需重新启动 headless 浏览器
    # driver.quit()
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.add_argument(
    #     '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver.get("https://discord.com/channels/948033443483254845/1027161980970205225")
    # load_cookies()

def send_message(sentence):
    """发送消息到 Discord 聊天框"""
    try:
        # 调试页面状态
        print(f"当前页面标题: {driver.title}")
        print(f"当前页面 URL: {driver.current_url}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        print("正在等待聊天输入框加载...")
        chat_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
        chat_input.send_keys(sentence)
        chat_input.send_keys(Keys.RETURN)
        print(f"后台发送了随机句子: {sentence}")
    except Exception as e:
        print(f"发送消息时出错: {e}")
        driver.save_screenshot("send_error_screenshot.png")
        print("已保存页面截图到 send_error_screenshot.png")

def main():
    print("开始后台发送固定随机话语到 Momentum 的 general-chat 频道（每 3 分钟一次）...")
    last_check_time = datetime.now()

    while True:
        current_time = datetime.now()
        # 每隔 3 分钟随机发送一条固定话语
        if (current_time - last_check_time) >= timedelta(minutes=3):
            selected_sentence = random.choice(FIXED_MESSAGES)
            send_message(selected_sentence)
            last_check_time = current_time

        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()

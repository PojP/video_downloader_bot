import re
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import requests as r
from selenium.webdriver.common.by import By
from datetime import datetime
import os
from src.send_video import send_video


async def is_instagram_reels_url(url) -> bool:
    pattern = r"https?://(?:www\.)?instagram\.com/reel/.*"
    match = re.match(pattern, url)
    if match:
        return True
    return False


def download_reels(url) -> bytes:
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 15)

    element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))

    reel_source = element.get_attribute('src')

    return r.get(reel_source).content

async def download_reel(msg,bot):
    await msg.answer("Ждите, видео скачивается:)")
    reel=download_reels(msg.text)
    a=msg.text[30:].split('?')[0].replace('/','_')+".mp4"
    with open(a, 'wb') as fd:
        fd.write(reel)
    b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
    os.rename(a,b)

    try:
        await send_video(bot,msg,b)
    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
    finally:
        os.remove(b)


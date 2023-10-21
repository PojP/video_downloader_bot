from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pyktok as pyk
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from datetime import datetime
import os

import validators

import pytube
from pytube.exceptions import VideoUnavailable
bot = None


async def start(msg: types.Message):
    await msg.answer("Привет! Это бот для загрузки видео из TikTok и YouTube. Просто введите ссылку и получите видео. Удачи:)")

async def downloader(msg: types.Message):
    print("work")
    try:
        if validators.url(msg.text):
            if "tiktok.com/" in msg.text:
                pyk.save_tiktok(msg.text,
                        True,
                        'video_data.csv',
                        'firefox')
                a=msg.text[23:].split('?')[0].replace('/','_')+".mp4"
                b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
                os.rename(a,b)
            
                print(f"B IS HERE: {b}")

                video_=FSInputFile(b)
                await bot.send_video(msg.from_user.id,video_)
                os.remove(b)

            elif msg.text[:19]=="https://youtube.com":

                yt = pytube.YouTube(msg.text)
                stream = yt.streams.get_highest_resolution()
                a=stream.download()
                b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
                os.rename(a,b)
                print(b)
                video_=FSInputFile(b)
                await bot.send_video(msg.from_user.id,video_)
                os.remove(b)
            else:
                await msg.answer("Неправильный url")
    
    except VideoUnavailable:
        await msg.answer("Видео недоступно для скачивания:(")

    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!! \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
def register_handlers(dp: Dispatcher, bot_: Bot):
    global bot
    bot =bot_
    dp.message.register(start, Command('start'))
    dp.message.register(downloader,F.text)

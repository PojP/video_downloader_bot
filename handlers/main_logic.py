from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
import validators

from src.tiktok import download_tiktok,is_tiktok_url
from src.youtube import download_youtube,is_youtube_url



async def start(msg: types.Message):
    await msg.answer("Привет! Это бот для загрузки видео из TikTok и YouTube. Просто введите ссылку и получите видео. Удачи:)")

async def downloader(msg: types.Message, bot: Bot):
    print("work")
    try:
        if msg.text is not None and validators.url(msg.text):
            if await is_tiktok_url(msg.text):
                await download_tiktok(msg,bot)
            elif await is_youtube_url(msg.text):
                await download_youtube(msg,bot)
            else:
                await msg.answer("Неправильный url")
    


    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")

def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command('start'))
    dp.message.register(downloader,F.text)

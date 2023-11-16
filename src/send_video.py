from aiogram import Bot,types
from aiogram.types import FSInputFile

async def send_video(bot: Bot,msg:types.Message,video, thumbnail_video=None):
    try:
        video_=FSInputFile(video)
        if thumbnail_video is not None:
            thumbnail_=FSInputFile(thumbnail_video)
            await bot.send_video(msg.chat.id,
                                         thumbnail=thumbnail_,
                                         video=video_,
                                         supports_streaming=True)
        else:
            await bot.send_video(msg.chat.id,
                                         video=video_,
                                         supports_streaming=True)
    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
    

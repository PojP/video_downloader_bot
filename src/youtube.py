import pytube
from pytube.exceptions import VideoUnavailable
from datetime import datetime
import os
import requests
from src.send_video import send_video

async def is_youtube_url(link: str) -> bool:
    return link[:19]=="https://youtube.com" or link[:17]=="https://youtu.be/"

async def download_youtube(msg,bot):
    try:
        await msg.answer("Ждите, видео скачивается:)")
        yt = pytube.YouTube(msg.text)
        stream = yt.streams.get_highest_resolution()

        thumbnail_url=requests.get(yt.thumbnail_url.split('?')[0])
                
        th_a=msg.text[23:].split('?')[0].replace('/','_')+".jpeg"
        with open(th_a, 'wb') as fd:
            fd.write(thumbnail_url.content)
                
        a=stream.download()
        b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
        os.rename(a,b)
                
        await send_video(bot,msg,b,th_a)
    except VideoUnavailable:
        await msg.answer("Видео недоступно для скачивания:(")
    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
    finally:
        os.remove(th_a)
        os.remove(b)


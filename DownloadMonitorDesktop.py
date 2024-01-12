import vk_audio
from kivymd.uix.list import ImageRightWidgetWithoutTouch
import asyncio
import aiohttp        
import aiofiles

class DownloadMonitorDesktop():
    def __init__(self):
        self.q = asyncio.Queue()
        self.exec = False

    async def downloads_monitor(self):
        self.exec = True
        while True:
            item = await self.q.get()
            await item
            if item is None:
                print('end')
                break
        self.exec = False
        
    async def download(self, tasks, key):
        # vk download task [0 artist, 1 song, 2 db_key, 3 img, 4 session, 5 audio_hash, 6 app, 7 track UI]
        if key == 'vk':
            await self.q.put(self.download_vk(tasks))
        elif key == 'ya':
            await self.q.put(self.download_ya(tasks))

        if not self.exec:
            await self.downloads_monitor()
        
    async def download_vk(self, tasks):
        for task in tasks:
            print(task)
            app_path = task[6].app_dir
            if task[3]!="./icons/track.png":
                img = app_path + f'/images/t/{task[2]}.jpg'
                async with aiohttp.ClientSession() as session:
                    async with session.get(task[3]) as response:
                        if response.status == 200:
                            async with aiofiles.open(img, mode='wb') as f:
                                await f.write(await response.read())

                            print('image saved')
                            
                        else:
                            img = "./icons/track.png"
            else:
                img = "./icons/track.png"
                    
            path = app_path + '/downloads/' + str(task[2]) + '.mp3'
            m3u8 = await task[4].get_link(task[5])
            await vk_audio.m3u8_parser(m3u8, path)

            # change left image widget to downloaded if ui still on screen
            try:
                task[7].progress.stop_anim()
                task[7].children[0].remove_widget(task[7].progress)
                task[7].add_widget(ImageRightWidgetWithoutTouch(source="./icons/done.png"))
            except:
                pass
            
            task[6].meta.add_new_track(path,img,task[2]) # DB class method
            print("Task done")

    async def download_ya(self, tasks):
        pass

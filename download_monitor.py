from kivymd.uix.list import ImageRightWidgetWithoutTouch
import asyncio
import aiohttp
import aiofiles
import datetime
import time
try:
    import pyobjus
    from pyobjus import autoclass
    from pyobjus import objc_arr, objc_str, objc_i
    NSString = autoclass('NSString')
    
except:
    pass

class AudioLoader:
    def __init__(self):
        self.task_list = []
        self.exec = False
        
    async def run(self,cmd):
        duration, progress = 0,0
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)

        while True:
            if proc.stdout.at_eof():
                self.task_list.pop(0)
                stdout, stderr = await proc.communicate()
                print('Task ends: ',self.task_list,f'[{cmd!r} exited with {proc.returncode}]')
                if self.task_list:
                    path, url = self.task_list[0]['path'], self.task_list[0]['link']
                    return await self.run(f'ffmpeg -http_persistent false -i {url} {path} -v 32 -progress pipe:1 -y')
                
                else:
                    self.exec = False
                    break

            stdout = (await proc.stdout.readline()).decode()
            if 'Duration:' in stdout:
                duration = time.strptime(stdout.split('.')[0].split(': ')[1],'%H:%M:%S')
                duration = datetime.timedelta(
                    hours=duration.tm_hour,
                    minutes=duration.tm_min,
                    seconds=duration.tm_sec).total_seconds()

                
            elif 'out_time_ms=' in stdout and 'N/A' not in stdout:
                progress = int((int(stdout.split('=')[1])/(10**6))/duration*100)
                self.task_list[0]['progress'] = progress if progress>self.task_list[0]['progress'] else self.task_list[0]['progress']
                
            print(f'[stdout] {stdout}, {duration}, {progress}')

        
        
        
    async def m3u8_parser(self,url, path, key):
        self.task_list.append({'key':key,'link': url, 'path': path, 'progress': 0})
        if not self.exec:
            self.exec = True
            await self.run(f'ffmpeg -http_persistent false -i {url} {path} -v 32 -progress pipe:1 -y')

    def get_info(self):
        return {task['key']:task['progress'] for task in self.task_list}


##    def python_m3u8_parser(url, path):
##        url = url.rstrip('?siren=1')
##        seg = []
##        response = requests.get(url)
##        if response.status_code>399:
##            return print('You are not logged in')
##    
##        m3u8_file = response.text
##        lines_m3u8_file = m3u8_file.replace('\n','').split('#')[1:]
##        i = 0
##        key_url = url.replace('index.m3u8','key.pub')
##        response = requests.get(key_url)
##        key = response.content
##        data= []
##        for line in lines_m3u8_file:
##        
##            if line.startswith('EXT-X-KEY'):
##                method = line.replace('EXT-X-KEY:', '')
##            if line.startswith('EXTINF'):
##                seg_url = url.replace('index.m3u8',line.split(',')[1])
##                response = requests.get(seg_url)
##                if method.startswith('METHOD=AES-128'):            
##                    seg.append(decrypt(response.content, key))
##
##
##                elif method.startswith('METHOD=NONE'):            
##                    seg.append(response.content)
##
##                i += 1
##            
##        raw_file = b''.join(seg)
##        with open(path, 'wb') as f:
##            f.write(raw_file)
##
##    def decrypt(seg, key):
##        iv = seg[:16]
##        cipher = seg[16:]
##        aes = pyaes.AESModeOfOperationCBC(key, iv = iv)
##        decrypted = b''
##        for i in range(16,len(cipher),16):
##            decrypted += aes.decrypt(seg[i-16:i])    
##
##        return decrypted
    
class DownloadMonitor:
    async def downloads_monitor(self):
        self.exec = True
        while self.task_list:
            await asyncio.sleep(0.5)
            progress_dict = self.get_info()
            print('progress dict',progress_dict)
            for task_key, track_obj in list(self.task_list.items()):
                if task_key in progress_dict: # update progress
                    track_obj.progress.value = progress_dict[task_key]
                else: # task ended
                    await self.task_end(self.task_list.pop(task_key),task_key)

        self.exec = False
        
    async def download(self, tasks, key):
        if key == 'vk':
            await self.download_vk(tasks)
        elif key == 'ya':
            await self.download_ya(tasks)

        if not self.exec:
            await self.downloads_monitor()
            
    async def save_img(self, track_obj,task_key):
        img = track_obj.app.app_dir + f'/images/t/{task_key}.jpg'
        session_timeout =   aiohttp.ClientTimeout(total=None,sock_connect=5,sock_read=5)
        async with aiohttp.ClientSession(timeout = session_timeout,connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(track_obj.img) as response:
                if response.status == 200:
                    async with aiofiles.open(img, mode='wb') as f:
                        await f.write(await response.read())

                    print('image saved')
        return img

    async def task_end(self,track_obj,task_key):
        # load image
        if track_obj.img != "./icons/track.png":
            img = await self.save_img(track_obj,task_key)
        else:
            img = "./icons/track.png"
        # change left image widget to downloaded if ui still on screen
        try:
            track_obj.progress.stop_anim()
            track_obj.children[0].remove_widget(track_obj.progress)
            track_obj.add_widget(ImageRightWidgetWithoutTouch(source="./icons/done.png"))
        except:
            pass
            
        track_obj.app.meta.add_new_track(
            track_obj.app.app_dir + '/downloads/' + str(task_key) + '.mp3',
            img,
            task_key
        ) # DB class method
        print("Task done")
    
class DownloadMonitorIOS(DownloadMonitor):
    def __init__ (self):
        audioLoader = autoclass('audioLoader') # obj-c class audioLoader
        self.loader = audioLoader.alloc().init()
        self.task_list = {}
        self.exec = False

    def get_info(self):
        tasks_arr = self.loader.get_info()
        # tasks_arr : [{'key': key, 'link': m3u8, 'path': path, 'progress': progress},...{}]
        print(tasks_arr)
        print(tasks_arr.count())
        progress_dict = {}
        for i in range(tasks_arr.count()):
            key = tasks_arr.objectAtIndex_(i).objectForKey_(objc_str('key')).UTF8String()
            if type(key) == bytes:
                key = key.decode('unicode_escape')
                
            progress = tasks_arr.objectAtIndex_(i).objectForKey_(objc_str('progress')).UTF8String()
            if type(progress) == bytes:
                progress = progress.decode('unicode_escape')
                
            progress_dict.update({int(key):int(progress)})

        return progress_dict
        
    async def download_vk(self, tasks):
        for task_key in tasks:
            track_obj = tasks[task_key]
            self.task_list.update({task_key:track_obj})
            print(track_obj)
                
            m3u8 = await track_obj.session.get_link(track_obj.id)
            path = NSString.alloc().initWithUTF8String_(
                track_obj.app.app_dir + '/downloads/' + str(task_key) + '.mp3'
            )
            m3u8 = NSString.alloc().initWithUTF8String_(m3u8)
            task_key = NSString.alloc().initWithUTF8String_(str(task_key))
            self.loader.loadVK_fileName_key_(m3u8,path,task_key) # obj-c method of class audioLoader

    async def download_ya(self, tasks):
        pass

    
class DownloadMonitorDesktop(DownloadMonitor):
    def __init__(self):
        self.loader = AudioLoader()
        self.exec = False
        self.task_list = {}

    def get_info(self):
        return self.loader.get_info()
        
    async def download_vk(self, tasks):
        for task_key in tasks:
            track_obj = tasks[task_key]
            self.task_list.update({task_key:track_obj})
            print(track_obj)
            
            m3u8 = await track_obj.session.get_link(track_obj.id)
            path = track_obj.app.app_dir + '/downloads/' + str(task_key) + '.mp3'
            asyncio.get_event_loop().create_task(self.loader.m3u8_parser(m3u8, path,task_key))
            

    async def download_ya(self, tasks):
        pass


from kivy.clock import Clock
from pyobjus import autoclass
audioLoader = autoclass('audioLoader') # obj-c class audioLoader
loader = audioLoader.alloc().init()
NSString = autoclass('NSString')

class DownloadMonitorIOS():
    def __init__ (self):
        self.to_download_list = []
        self.downloadEvent = Clock.schedule_interval(self.downloads_monitor,1)

    def add_download_task(self, task):
        self.to_download_list.append(task)
        if task[0] == 'vk':
            self.download_vk(task)
        else:
            pass
        
    def downloads_monitor(self, value):
        tasks_arr = loader.get_info()
        print(tasks_arr)
        print(dir(tasks_arr))
        print(tasks_arr.count())
        print(dir(tasks_arr.count()))

        path = []
        for i in range(tasks_arr.count()):
            path.append(tasks_arr.objectAtIndex_(i).UTF8String())

        if not path:
            print('no active tasks avaliable')
            return
        
        for task in self.to_download_list:
            if task[5] not in path:
                task[6].is_downloaded = True
                print(f"Task done: {self.to_download_list[0]}")
                del self.to_download_list[0]
            
    def download(self):
        task = self.to_download_list[0]
        # task [key, args]
        if task[0] == 'vk':
            self.download_vk(task)
        else:
            pass
        
    def download_vk(self, task):
        # vk download task [key, artist, song, db_key, url_m3u8, app_path, track UI]     
        path = NSString.alloc().initWithUTF8String_(task[5] + '/downloads/' + str(task[3]) + '.mp3')
        m3u8 = NSString.alloc().initWithUTF8String_(task[4])
        loader.loadVK_fileName_(m3u8,path) # obj-c method of class audioLoader



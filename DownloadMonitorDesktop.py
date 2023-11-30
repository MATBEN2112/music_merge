import threading as th
import time
import vk_audio

class DownloadMonitorDesktop():
    def __init__ (self):
        self.to_download_list = []
        self.event = th.Event()
        self.thread = th.Thread(target=self.downloads_monitor, name='Downloads monitor', args=())
        self.thread.start() # start background thread

    def add_download_task(self, task):
        self.to_download_list.append(task)
    def downloads_monitor(self):
        while True:
            if self.to_download_list:
                print("New download task arrived")
                self.download()
            time.sleep(1)
            
    def download(self):
        task = self.to_download_list[0]
        # task [key, args]
        if task[0] == 'vk':
            self.download_vk(task)
        else:
            pass
        
    def download_vk(self, task):
        # vk download task [key, artist, song, db_key, url_m3u8, app_path, track UI]
        
        path = task[5] + '/downloads/' + str(task[3]) + '.mp3'
        vk_audio.m3u8_parser(task[4], path)
        
        del self.to_download_list[0]
        # change left image widget to downloaded from main thread
        task[6].is_downloaded = True
        print("Task done")
        

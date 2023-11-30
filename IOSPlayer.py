import pyobjus
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE
from pyobjus import objc_arr, objc_str, objc_i
from utils import *
from kivy.clock import Clock
import time
from custom_widgets import AudioInfo, PlayerBack, Track, VKTrack
from kivy.uix.screenmanager import SlideTransition

NSMutableArray = autoclass("NSMutableArray")
NSString = autoclass('NSString')

class PlayerUI:
    def _start_player_session(self, track_obj):
        ''' Function starts music play. Cases '''
        # clean old player widgets if exists
        self.app.main_screen.remove_widget(self.audio_bar[0])
        self.app.album_screen.remove_widget(self.audio_bar[1])
        self.app.album_list_screen.remove_widget(self.audio_bar[2])

        # hilighte and save track as element of UI
        if self.current_track_obj:
            self.current_track_obj.unhilighte()
            
        self.current_track_obj = track_obj
        self.current_track_obj.hilighte()
        self.load()
        
        print('Play audio')

        self.play()
           
        self.app.main_screen.add_widget(self.audio_bar[0])
        self.app.album_screen.add_widget(self.audio_bar[1])
        self.app.album_list_screen.add_widget(self.audio_bar[2])
            
        # set events
        if 'progressbarEvent' in dir(self):
            self.progressbarEvent.cancel()
            
        self.progressbarEvent = Clock.schedule_interval(self._update_progressbar,1)
        
    def _update_progressbar(self,value):
        ''' Function to update progress bar and timer '''
        info_dict = self.get_info()
        if 'info_dict' not in dir(self) or self.info_dict != info_dict: # does track states changed

            if 'info_dict' not in dir(self) or self.info_dict['song_pos'] != info_dict['song_pos']: # progress bar and timers
                # progress bar
                [rsetattr(i, 'ids.song_progress.value', info_dict['song_pos']) for i in self.audio_bar]
                self.app.player_screen.ids.song_progress.value = info_dict['song_pos']
                print(f"Audio bar current value: {info_dict['song_pos']} Ends in: {info_dict['song_len']}")
                # timer
                current_time = time.strftime('%M:%S', time.gmtime(info_dict['song_pos']))
                [rsetattr(i, 'ids.song_timer.text', current_time) for i in self.audio_bar]
                self.app.player_screen.ids.song_timer.text = current_time  
                
            if 'info_dict' not in dir(self) or self.info_dict['file'] != info_dict['file']: # track
                #self.track = (info_dict['key'],info_dict['file'],info_dict['author'],info_dict['song'],info_dict['img'])
                # player image
                print(info_dict['img'])
                if 'img_back' in dir(self):
                    self.app.player_screen.remove_widget(self.img_back)
                self.img_back = PlayerBack(info_dict['img'])
                self.app.player_screen.add_widget(self.img_back)
                # track name
                track_name = info_dict['author'] + ' - ' + info_dict['song']
                [rsetattr(i, 'ids.song_name.text', track_name) for i in self.audio_bar]
                self.app.player_screen.ids.song_name.text = track_name
                # timer len
                [rsetattr(i, 'ids.song_progress.max', info_dict['song_len']) for i in self.audio_bar]
                self.app.player_screen.ids.song_progress.max = info_dict['song_len']
                self.app.player_screen.ids.song_len.text= time.strftime('%M:%S', time.gmtime(info_dict['song_len']))
                # hilighte
                try: # if UI element loaded try to hilighte element
                    for track_obj in self.current_track_obj.parent.children:
                        if track_obj.track[1] == info_dict['file']:
                            if self.current_track_obj:
                                self.current_track_obj.unhilighte()
                                
                            self.current_track_obj = track_obj
                            self.current_track_obj.hilighte()
                            break

                except (IndexError, AttributeError):
                    print('UI element is not loaded')
            
            if 'info_dict' not in dir(self) or self.info_dict['status'] != info_dict['status']: # play/stop button
                img = "./icons/stop60.png" if info_dict['status'] else "./icons/play60.png"
                f = self.pause if info_dict['status'] else self.play
                [rsetattr(i, 'ids.song_status.source', img) for i in self.audio_bar]
                [i.ids.song_status.reload() for i in self.audio_bar]
                [rsetattr(i, 'ids.action.on_release', f) for i in self.audio_bar]
                self.app.player_screen.ids.song_status.source = img
                self.app.player_screen.ids.song_status.reload()
                self.app.player_screen.ids.action.on_release = f

        self.info_dict = info_dict

    def _stop_player_session(self):
        if 'track' not in dir(self):
            return
        
        self.player.stop()
        self.progressbarEvent.cancel()
        self.main_screen.remove_widget(self.audio_bar[0])
        self.album_screen.remove_widget(self.audio_bar[1])
        self.album_list_screen.remove_widget(self.audio_bar[2])
        
    def switch_to_player(self, o):
        screen_to_return = self.app.manager.current
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'player'
        self.app.manager.get_screen('player').open_player(screen_to_return)


class IOSPlayer(PlayerUI):
    def __init__(self, app):
        self.current_track = None
        self.current_track_obj = None
        self.track_list = None
        self.album_key = None
        self.app = app
        self.audio_bar = [AudioInfo() for _ in range(3)]
        self.IOS_player = autoclass('IOS_player') # [obj-c class IOS_player]
        self.player = self.IOS_player.alloc().init() # [obj-c method of class IOS_player]
        
    def start_playback(self, track_obj):
        self.stop()
        # save album id if audio in album
        self.album_key = track_obj.album_key
        # save track data
        if isinstance(track_obj, Track):
            if self.album_key:
                self.track_list = self.app.album_screen.track_list
            else:
                self.track_list = self.app.main_screen.track_list
                    
        elif isinstance(track_obj, VKTrack):
            if self.album_key:
                self.track_list = self.app.album_screen.track_list
            else:
                self.track_list = self.app.main_screen.track_list
                
        self.current_track = track_obj.track
        # work with UI and load audio to player
        self._start_player_session(track_obj)

    def load(self):
        track_arr = NSMutableArray.arrayWithCapacity_(len(self.track_list))
        for track in self.track_list:
            if track == 'EOF':
                track_arr.addObject_(NSString.alloc().initWithUTF8String_(track))
            else:
                img = NSString.alloc().initWithUTF8String_(track[4])
                author = NSString.alloc().initWithUTF8String_(track[2])
                song = NSString.alloc().initWithUTF8String_(track[3])
                fn = NSString.alloc().initWithUTF8String_(track[1])
                track_arr.addObject_(objc_arr(fn, author, song, img))

        key = self.track_list.index(self.current_track[0:5])
        if isinstance(self.current_track_obj, Track):
            self.player.loadPlaylist_key_(track_arr,key) # obj-c method of class IOS_player
            
        elif isinstance(self.current_track_obj, VKTrack):
            uid = self.current_track[5].u_id
            cookies_list = self.current_track[5].cookies_list
            cookies_arr = NSMutableArray.arrayWithCapacity_(len(cookies_list))
            for cookie in cookies_list:
                name = NSString.alloc().initWithUTF8String_(cookie[0])
                value = NSString.alloc().initWithUTF8String_(cookie[1])
                domain = NSString.alloc().initWithUTF8String_(cookie[2])
                path = NSString.alloc().initWithUTF8String_(cookie[3])
                cookies_arr.addObject_(objc_arr(name, value, domain, path))

            self.player.loadVKPlaylist_key_cookies_uid(track_arr, key, cookies_arr,uid) # obj-c method of class IOS_player
            
        
    def play(self):
        self.player.play() # obj-c method of class IOS_player

    def pause(self):
        self.player.pause() # obj-c method of class IOS_player
        
    def stop(self):
        self.player.stop() # obj-c method of class IOS_player

    def play_next(self, n): 
        if n > 0:
            self.player.next() # obj-c method of class IOS_player
        elif n < 0:
            self.player.prev() # obj-c method of class IOS_player

    def seek(self, position):
        self.player.seek_(position) # obj-c method of class IOS_player

    def get_pos(self):
        return self.player.get_pos() # obj-c method of class IOS_player

    def get_length(self):
        return self.player.get_len() # obj-c method of class IOS_player

    def get_current_track(self):
        info = self.get_info()
        return (info['key'],info['file'],info['author'],info['song'],info['img']) else (None,)*5
        
    def get_info(self):
        info_dict = self.player.get_info() # obj-c method of class IOS_player
        key = info_dict.objectForKey_(objc_str('key')).intValue()       
        author = info_dict.objectForKey_(objc_str('author')).UTF8String()
        if type(author) == bytes:
            author = author.decode()
        if '\\' in author:
            author = author.encode().replace(b'U',b'u').decode('unicode_escape')

        song = info_dict.objectForKey_(objc_str('song')).UTF8String()
        if type(song) == bytes:
            song = song.decode('unicode_escape')
        if '\\' in song:
            song = song.encode().replace(b'U',b'u').decode('unicode_escape')
            
        file = info_dict.objectForKey_(objc_str('file')).UTF8String()
        if type(file) == bytes:
            file = file.decode('unicode_escape')
            
        img = info_dict.objectForKey_(objc_str('img')).UTF8String()
        if type(img) == bytes:
            img = img.decode('unicode_escape')
            
        song_len = info_dict.objectForKey_(objc_str('len')).floatValue()
        song_pos = info_dict.objectForKey_(objc_str('pos')).floatValue()
        status = info_dict.objectForKey_(objc_str('status')).boolValue()
        info_dict = {'key':key, 'author':author, 'song':song, 'file':file, 'img':img, 'song_len':song_len, 'song_pos':song_pos,'status':status}
        #print(info_dict)
        return info_dict

    def test(self):
        self.player.test_func() # obj-c method of class IOS_player
    

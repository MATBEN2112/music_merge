from kivy.core.audio import SoundLoader
from utils import *
from kivy.clock import Clock
import time
from custom_widgets import AudioInfo, PlayerBack, Track, VKTrack
from kivy.uix.screenmanager import SlideTransition

try:
    import pyobjus
    from pyobjus import autoclass
    from pyobjus.dylib_manager import load_framework, INCLUDE
    from pyobjus import objc_arr, objc_str, objc_i

    NSMutableArray = autoclass("NSMutableArray")
    NSString = autoclass('NSString')
except:
    pass

class PlayerUI:
    def start_playback(self, track_obj):
        self.pause()
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

        for i in range(len(self.track_list)):
            if self.track_list[i][1] == track_obj.track[1]:
                self.key = i
                break
            
        self.current_track = track_obj.track
        print('New track to play arrived: ', self.current_track)
        # work with UI and load audio to player
        self._start_player_session(track_obj)

    def _start_player_session(self, track_obj):
        ''' Function starts music playback. Cases '''

        # highlighte and save track as element of UI
        if self.current_track_obj:
            self.current_track_obj.unhighlighte()

        if self.app.manager.current == 'search':
            track_obj.highlighte()
            for child in self.app.main_screen.ids.container.children:
                if not isinstance(child, (Track,VKTrack)):
                    continue
                
                if child.path == self.current_track[1]:
                    self.current_track_obj = child
                    break
                    
        else:
            self.current_track_obj = track_obj
            
        self.current_track_obj.highlighte()

        self.load()
        print('audio loaded')
        if self.app.audio_bar.status == 'closed':
            self.app.audio_bar.show()
            
        # set events
        if 'progressbarEvent' in dir(self):
            self.progressbarEvent.cancel()
            
        self.progressbarEvent = Clock.schedule_interval(self._update_progressbar,1)
        
    def _update_progressbar(self,value):
        ''' Function to update progress bar and timer '''
        info_dict = self.get_info()
        if not info_dict:
            return
        
        if 'info_dict' not in dir(self) or self.info_dict != info_dict: # does track states changed

            if 'info_dict' not in dir(self) or self.info_dict['song_pos'] != info_dict['song_pos']: # progress bar and timers
                # progress bar
                self.app.audio_bar.ids.song_progress.value = info_dict['song_pos']
                self.app.player_screen.ids.song_progress.value = info_dict['song_pos']
                print(f"Audio bar current value: {info_dict['song_pos']} Ends in: {info_dict['song_len']}")
                # timer
                current_time = time.strftime('%M:%S', time.gmtime(info_dict['song_pos']))
                self.app.audio_bar.ids.song_timer.text = current_time
                self.app.player_screen.ids.song_timer.text = current_time  
                
            if 'info_dict' not in dir(self) or self.info_dict['file'] != info_dict['file']: # track
                # player image
                if 'img_back' in dir(self):
                    self.app.player_screen.remove_widget(self.img_back)
                self.img_back = PlayerBack(info_dict['img'])
                self.app.player_screen.add_widget(self.img_back)
                # track name
                track_name = info_dict['author'] + ' - ' + info_dict['song']
                self.app.audio_bar.ids.ticker.stop_animation()
                self.app.audio_bar.ids.ticker.data = {'text': track_name, 'font_size':'24sp'}
                self.app.audio_bar.ids.ticker.start_animation(-1)
                self.app.player_screen.ids.ticker.stop_animation()
                self.app.player_screen.ids.ticker.data = {'text': track_name, 'font_size':'32sp'}
                self.app.player_screen.ids.ticker.start_animation(-1)
                # timer len
                self.app.audio_bar.ids.song_progress.max = info_dict['song_len']
                self.app.player_screen.ids.song_progress.max = info_dict['song_len']
                self.app.player_screen.ids.song_len.text= time.strftime('%M:%S', time.gmtime(info_dict['song_len']))
                # highlighte
                try: # if UI element loaded try to highlighte element
                    for track_obj in self.current_track_obj.parent.children:
                        if not isinstance(track_obj, (Track,VKTrack)):
                            continue
                        if track_obj.track[1] == info_dict['file']:
                            if self.current_track_obj:
                                self.current_track_obj.unhighlighte()
                                
                            self.current_track_obj = track_obj
                            self.current_track_obj.highlighte()
                            break

                except (IndexError, AttributeError) as e:
                    print('UI element is not loaded:', e)
            
            if 'info_dict' not in dir(self) or self.info_dict['status'] != info_dict['status']: # play/stop button
                img = "./icons/stop.png" if info_dict['status'] else "./icons/play.png"
                f = self.pause if info_dict['status'] else self.play
                self.app.audio_bar.ids.song_status.source = img
                self.app.audio_bar.ids.song_status.reload()
                self.app.audio_bar.ids.action.on_release = f
                self.app.player_screen.ids.song_status.source = img
                self.app.player_screen.ids.song_status.reload()
                self.app.player_screen.ids.action.on_release = f

        self.info_dict = info_dict


    def _stop_player_session(self):
        self.progressbarEvent.cancel()
        if self.app.audio_bar.status == 'open':
            self.app.audio_bar.hide()

    def get_current_track(self):
        info = self.get_info()
        return info['file'] if info else None


class DesktopPlayer(PlayerUI):
    def __init__(self, app):
        self.key = 0
        self.current_track = None
        self.current_track_obj = None
        self.track_list = None
        self.album_key = None
        self.app = app
        self.player = None

    def load(self):
        if not self.current_track_obj:
            return

        try:
            if isinstance(self.current_track_obj, Track):
                self.player = SoundLoader.load(self.current_track[1])
            
            elif isinstance(self.current_track_obj, VKTrack):
                pass
                #m3u8 = await self.current_track[5].get_link(self.current_track[1])
                #self.player = SoundLoader.load(m3u8)   [FIX unable to play m3u8 links (mp3 too :( )]

            self.play()
        except:
            print('No such file')
            
    def play(self):
        if self.player:
            print("play")
            pos = self.get_pos()  
            self.player.play()
            self.seek(pos)

    def pause(self):
        if self.player:
            print("pause")
            self.player.stop()
        
    def stop(self):
        if self.player:
            print("stop")
            self.pause()
            self._stop_player_session()
            #self.player.unload()   [FIX crashes when it's loading audio after unloading another (audio plug mb)]
            self.player = None
            self.current_track = None
            self.current_track_obj = None
            self.track_list = None
            self.album_key = None
        
    def play_next(self, n):
        print(self.key)
        def _():
            if self.track_list[n+self.key] == 'EOL':
                print("List out of range.")
                self.pause()
                self.seek(0.1)
                return
            else:
                self.current_track = self.track_list[n+self.key]
                self.key += n
                
        if n+self.key < 0:
            print("List out of range.")
            self.pause()
            self.seek(0.1)
            return
        
        try:
            _()
                        
        except IndexError:
            print('Track data has not loaded yet')
            if isinstance(self.current_track_obj, VKTrack):
                self.track_list += self.current_track[5].load_more_t()
                                 
            _()

        self.pause()
        self.seek(0.1)
        self.load()
        self.play()

    def seek(self, *args):
        if self.player:
            print('seek audio')
            if type(args[0]) is float or type(args[0]) is int:
                self.player.seek(args[0])
            else:
                slider, touch = args[0][0:2]
                if slider.collide_point(touch.x, touch.y):
                    slider.active = False
                    self.player.seek(slider.value)

    def get_pos(self):
        return self.player.get_pos() if self.player else 0

    def get_length(self):
        return self.player.length if self.player else 0

    def get_info(self):
        if not self.current_track_obj:
            return

        status = True if self.player and self.player.state == 'play' else False
        info_dict = {
            'key':self.current_track[0],
            'author':self.current_track[2],
            'song':self.current_track[3],
            'file':self.current_track[1],
            'img':self.current_track[4],
            'song_len':self.get_length(),
            'song_pos':self.get_pos(),
            'status': status}

        if self.player and int(info_dict['song_len'] - 1) <= int(info_dict['song_pos']):
            self.end_of_track()
            
        return info_dict

    def end_of_track(self):
        self.pause()
        self.play_next(1)
    

class IOSPlayer(PlayerUI):
    def __init__(self, app):
        self.current_track = None
        self.current_track_obj = None
        self.track_list = None
        self.album_key = None
        self.app = app
        self.IOS_player = autoclass('IOS_player') # [obj-c class IOS_player]
        self.player = self.IOS_player.alloc().init() # [obj-c method of class IOS_player]

    def load(self):
        if not self.current_track_obj:
            return
        
        track_arr = NSMutableArray.arrayWithCapacity_(len(self.track_list))
        for track in self.track_list:
            if track == 'EOL':
                track_arr.addObject_(NSString.alloc().initWithUTF8String_(track))
            else:
                img = NSString.alloc().initWithUTF8String_(track[4])
                author = NSString.alloc().initWithUTF8String_(track[2])
                song = NSString.alloc().initWithUTF8String_(track[3])
                fn = NSString.alloc().initWithUTF8String_(track[1])
                track_arr.addObject_(objc_arr(fn, author, song, img))

        key = self.track_list.index(self.current_track)
        if isinstance(self.current_track_obj, Track):
            self.player.loadPlaylist_key_(track_arr,key) # obj-c method of class IOS_player
            
        elif isinstance(self.current_track_obj, VKTrack):
            uid = self.current_track[5].u_id
            if self.current_track_obj.album_key:
                section_id,next_from = None,None
            else:
                section_id,next_from = self.current_track[5].section_id_t, self.current_track[5].next_from_t
                
            cookies_list = self.current_track[5].cookies_list
            cookies_arr = NSMutableArray.arrayWithCapacity_(len(cookies_list))
            for cookie in cookies_list:
                name = NSString.alloc().initWithUTF8String_(cookie[0])
                value = NSString.alloc().initWithUTF8String_(cookie[1])
                domain = NSString.alloc().initWithUTF8String_(cookie[2])
                path = NSString.alloc().initWithUTF8String_(cookie[3])
                cookies_arr.addObject_(objc_arr(name, value, domain, path))

            self.player.loadVKPlaylist_key_cookies_uid_sectionID_nextFrom_(track_arr, key, cookies_arr,uid,section_id,next_from) # obj-c method of class IOS_player
            
        
    def play(self):
        if not self.current_track_obj:
            return
        
        self.player.play() # obj-c method of class IOS_player

    def pause(self):
        if not self.current_track_obj:
            return
        
        self.player.pause() # obj-c method of class IOS_player
        
    def stop(self):
        if not self.current_track_obj:
            return
        
        self.player.stop() # obj-c method of class IOS_player

    def play_next(self, n):
        if n > 0:
            self.player.next() # obj-c method of class IOS_player
        elif n < 0:
            self.player.prev() # obj-c method of class IOS_player

    def seek(self, *args):
        if isinstance(args[0],(float,int)):
            self.player.seek_(int(args[0]))
        else:
            slider, touch = args[0][0:2]
            if slider.collide_point(touch.x, touch.y):
                slider.active = False
                self.player.seek_(int(slider.value)) # obj-c method of class IOS_player

    def get_pos(self):
        if not self.current_track_obj:
            return
        
        return self.player.get_pos() # obj-c method of class IOS_player

    def get_length(self):
        if not self.current_track_obj:
            return
        
        return self.player.get_len() # obj-c method of class IOS_player
        
    def get_info(self):
        info_dict = self.player.get_info() # obj-c method of class IOS_player
        print(info_dict)
        if not info_dict:
            return
        
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
        return info_dict

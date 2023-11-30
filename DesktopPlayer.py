from kivy.core.audio import SoundLoader
from utils import *
from kivy.clock import Clock
import time
from custom_widgets import AudioInfo, PlayerBack, Track, VKTrack
from kivy.uix.screenmanager import SlideTransition

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


class DesktopPlayer(PlayerUI):
    def __init__(self, app):
        self.current_track = None
        self.current_track_obj = None
        self.track_list = None
        self.album_key = None
        self.app = app
        self.audio_bar = [AudioInfo() for _ in range(3)]
        self.player = None

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
        if not self.current_track_obj:
            return
        
        if isinstance(self.current_track_obj, Track):
            self.player = SoundLoader.load(self.current_track[1])
            
        elif isinstance(self.current_track_obj, VKTrack):
            self.player = SoundLoader.load(self.current_track[5].get_link(self.current_track[1]))
            
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
        if 'player' in dir(self) and self.player:
            print("stop")
            self.pause()
            self._stop_player_session()
            #self.player.unload()
        
    def play_next(self, n):
        for track in self.track_list: 
            if track[0:5] == self.current_track[0:5]:
                i = self.track_list.index(track)
                break
                
        if n+i < 0:
            print("List out of range.")
            self.pause()
            self.seek(0.1)
            return
        
        try:
            if self.track_list[n+i] == 'EOF':
                print("List out of range.")
                self.pause()
                self.seek(0.1)
                return
            else:
                self.current_track = self.track_list[n+i]
                        
        except IndexError:
            print('Track data is not loaded')
            if isinstance(self.current_track_obj, VKTrack):
                self.track_list += self.current_track[5].load_more_t()
                                 
            if self.track_list[n+i] == 'EOF':
                print("List out of range.")
                self.pause()
                self.seek(0.1)
                return
            else:
                self.current_track = self.track_list[n+i]

        self.stop()
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
    
    def get_current_track(self):
        return self.current_track if self.current_track else (None,)*5

    def get_info(self):

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
        self.stop()
        self.play_next(1)
    

    

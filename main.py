import kivy
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, ImageLeftWidget, IRightBodyTouch, TwoLineAvatarListItem, ImageLeftWidgetWithoutTouch, ImageRightWidgetWithoutTouch, TwoLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu

import sys
import time
import pickle
import timeit
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivymd.uix.relativelayout import MDRelativeLayout
import os
import shutil
from utils import *

from kivy.uix.textinput import TextInput



from kivymd.uix.button import MDIconButton
from kivy.core.window import Window
from kivy.utils import platform

if kivy.utils.platform not in ['android','ios']:
    Window.size = (540, 1170)


from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.clock import Clock
from kivymd.uix.slider import MDSlider
from kivy.properties import ObjectProperty

from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
import vk_methods as vk
from custom_widgets import *


from CustomSoundLoader import IOSPlayer

#################
### Main Screen  ###
#################
class Start(Screen):
    def downloaded_audios(self):
        self.ids.nav_drawer.set_state('close')
        self.app = MDApp.get_running_app()
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
        )
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
        )
        self.ids.container.clear_widgets()
        self.ids.album_container.clear_widgets()
        album_list = self.app.meta.album_list() ###
        for album in album_list:
            self.ids.album_container.add_widget(AlbumButton(self.app, album))

        track_list = self.app.meta.track_list() ###
        for track in track_list:
            self.ids.container.add_widget(Track(self.app, track))

    ### EDIT TOOLS ### 
    def edit_menu(self):
        menu_items = [{"viewclass": "OneLineListItem","text": f"Selection","on_release": self.open_selection_menu}, ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=4
        )
        self.drop_down_menu.open()
        
    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self))
        
    ### VK METHODS ###
    def vk_audios(self, session):
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
        )
        self.session = session
        # load tracks
        self.ids.container.clear_widgets()
        self.audio_list = self.session.load_user_audios() 
        for key in self.audio_list.keys():
            self.ids.container.add_widget(
                VKTrack(
                    self.session,
                    self.app,
                    ID = key,
                    artist = self.audio_list[key]['artist'],
                    song = self.audio_list[key]['song'],
                    img = self.audio_list[key]['img_link'])
            )

        #load albums     
        self.ids.album_container.clear_widgets()
        self.album_list = self.session.load_playlists()  
        for key in self.album_list.keys():
            self.ids.album_container.add_widget(
                VKAlbumButton(
                    self.session,
                    self.app,
                    ID = key,
                    name = self.album_list[key]['playlist_name'],
                    img = self.album_list[key]['img_link']
                )
            )

        
    def search_audio(self, q):
        pass

class Player(Screen):
    def open_player(self,screen_to_return):
        self.screen_to_return=screen_to_return
        self.app = MDApp.get_running_app()
        
    def loop_audio(self):
        pass
    def close_player(self):
        print('closed')
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = self.screen_to_return
        self.manager.get_screen(self.screen_to_return)

##################
### Album Screen ###
##################         
class Album(Screen):
    ### BASE METHODS ###
    def open_album(self, album, screen_to_return):
        self.album = album
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
        )
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album())
        )

        self.path = album[1]
        self.ids.album_name.text = album[2]
        self.ids.album_image.source = album[3]
        self.ids.container.clear_widgets()
        self.key = album[0]
        self.screen_to_return = screen_to_return
        self.app = MDApp.get_running_app()
        track_list = self.app.meta.track_list(key = self.key) ###
        for track in track_list:
            self.ids.container.add_widget(Track(self.app, track))
        
    def close_album(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = self.screen_to_return
        if self.screen_to_return == 'start':
            self.manager.get_screen(self.screen_to_return).downloaded_audios()
        elif self.screen_to_return == 'album_list':
            self.manager.get_screen(self.screen_to_return).open_album_list()

    def edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": f"Selection","on_release": self.open_selection_menu},
            {"viewclass": "OneLineListItem","text": f"Delete album","on_release": self.delete_album},
            {"viewclass": "OneLineListItem","text": f"Rename album","on_release": self.rename_album},
            {"viewclass": "OneLineListItem","text": f"Add track","on_release": self.add_track},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=4
        )
        self.drop_down_menu.open()

    def delete_album(self, state=None):
        self.drop_down_menu.dismiss()
        if state == "Confirm":
            try:
                self.app.meta.delete_album(self.key) ###
            except PermissionError: # if file loaded to player 
                self.app.unload_audio()
                self.app.meta.delete_album(self.key) ###
                
            self.confirmation_popup.dismiss()
            return self.close_album()
        
        elif state == "Cancel":
            return self.confirmation_popup.dismiss()
            
        self.confirmation_popup = ConfirmationPopup()
        func = lambda :self.delete_album(state = "Confirm")
        btn1 = PopupActionButton("Confirm", func, 0.2)
        func = lambda :self.delete_album(state = "Cancel")
        btn2 = PopupActionButton("Cancel", func, 0.8)
        self.confirmation_popup.ids.action.clear_widgets()
        self.confirmation_popup.ids.action.add_widget(btn1)
        self.confirmation_popup.ids.action.add_widget(btn2)
        self.confirmation_popup.open()
    
    def rename_album(self, album_name=None):
        self.drop_down_menu.dismiss()
        if album_name:
            self.app.meta.edit_album(self.key, album_name) ###
            self.rename_album_popup.dismiss()
            self.ids.menu_row.title = album_name
            return
        
        self.rename_album_popup = RenameAlbumPopup()

        func = lambda :self.rename_album(album_name=self.rename_album_popup.ids.album_name.text)
        btn = PopupActionButton("Enter", func, 0.5)
        self.rename_album_popup.ids.action.clear_widgets()
        self.rename_album_popup.ids.action.add_widget(btn)
        self.rename_album_popup.open()

    def add_track(self):
        self.drop_down_menu.dismiss()

    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self))

    ### VK METHODS ###
    def vk_open_album(self, session, ID, name, img, screen_to_return):
        self.session = session
        self.audio_list = self.session.load_playlist_content(ID)
        
        self.ids.container.clear_widgets()
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/load.png", [0.9, 0.35], func = lambda x: print(123))
        )
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/back.png", [0.1, 0.35], func = lambda x: self.vk_close_album())
        )
        self.ids.album_image.source = img
        self.screen_to_return = screen_to_return

        self.app = MDApp.get_running_app()
        
        for key in self.audio_list.keys():
            self.ids.container.add_widget(
                VKTrack(
                    self.session,
                    self.app,
                    ID = key,
                    artist = self.audio_list[key]['artist'],
                    song = self.audio_list[key]['song'],
                    img = self.audio_list[key]['img_link'])
            )

    def vk_close_album(self):
        app = MDApp.get_running_app()
        app.album_name=''
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = self.screen_to_return

#####################
### Album List Screen ###
#####################  
class AlbumList(Screen):
    ### BASE METHODS ###
    def open_album_list(self):
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/add.png", [0.9, 0.35], func = lambda x: self.add_album())
        )
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album_list())
        )
        self.app = MDApp.get_running_app()
        self.ids.album_container.clear_widgets()
        album_list = self.app.meta.album_list() ###
        for album in album_list:
            self.ids.album_container.add_widget(AlbumButton(self.app, album))
                
    def close_album_list(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'start'
        self.manager.get_screen('start').downloaded_audios()

    def add_album(self, album_name=None):
        if album_name:
            self.app.meta.add_album(album_name, img=None) ###
            self.create_album_popup.dismiss()
            return self.open_album_list()
            
        self.create_album_popup = CreateAlbumPopup()
        func = lambda :self.add_album(album_name=self.create_album_popup.ids.album_name.text)
        btn = PopupActionButton("Enter", func, 0.5)
        self.create_album_popup.ids.action.clear_widgets()
        self.create_album_popup.ids.action.add_widget(btn)
        self.create_album_popup.open()
        
    ### VK METHODS ### 
    def vk_open_album_list(self, session):
        self.session = session
        self.app = MDApp.get_running_app()
        self.ids.menu_row.right_action_items = [
            ["back.png", lambda x: self.vk_close_album_list()]
        ]
        #load albums     
        self.ids.album_container.clear_widgets()
        if 'album_list' not in dir(self):
            self.album_list = self.session.load_playlists()
        for key in self.album_list.keys():
            self.ids.album_container.add_widget(
                VKAlbumButton(
                    self.session,
                    self.app,
                    ID = key,
                    name = self.album_list[key]['playlist_name'],
                    img = self.album_list[key]['img_link']
                )
            )

            
    def vk_close_album_list(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'start'
        

#################
### Login Screen ###
#################
class Login(Screen):
    def close_login_page(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'start'

    def open_login_page(self,media):
        self.app = MDApp.get_running_app()
        if media == "./icons/vk.png": 
            self.secure_code_popup = SecureCodePopup()
            self.captcha_popup = CaptchaPopup()
            
            self.ids.login_img.source = './icons/vk.png'
            self.ids.login_img.reload()

            self.ids.action.clear_widgets()
            func = lambda : self.do_login_vk(self.ids.login.text, self.ids.password.text)
            self.ids.action.add_widget(LoginButton(func))

            self.captcha_sid = ''
            self.captcha_key = ''
            
            self.reset_forms()

        elif media == "./icons/ya.png":
            self.ids.login_img.source = './icons/ya.png'
            self.ids.login_img.reload()
            
            self.ids.action.clear_widgets()
            func = lambda : print(123)
            self.ids.action.add_widget(LoginButton(func))
            
            self.reset_forms()

        
    def reset_forms(self):
        # reset forms
        self.ids.login.text = ''
        self.ids.password.text = ''
        self.ids.error.text = ''
        
    ### VK ###
    def do_login_vk(self, login, password, captcha_sid='', captcha_key=''):
        self.login = login
        self.password = password

        self.session, captcha_sid, status, auth_hash = vk.login_request(login, password,
            captcha_sid=captcha_sid,
            captcha_key=captcha_key
        )
        print(self.session, captcha_sid, status, auth_hash)

        if status == 'Logged in':# done no 2fa case ??????
            self.end_login_vk()
        
        elif status == 'Secure code':
            self.captcha_popup.dismiss()
            #popup with secure code appear

            func = lambda : self.do_login_vk_secure_code(
                self.secure_code_popup.ids.secure_code.text,
                auth_hash
            )
            btn = PopupActionButton("Enter",func, 0.5)
            self.secure_code_popup.ids.action.clear_widgets()
            self.secure_code_popup.ids.action.add_widget(btn)
            self.secure_code_popup.open()
            
        elif status == 'Captcha needed':
            if captcha_key:
                self.captcha_popup.ids.error.text = 'Incorrect captcha'
            vk.captcha(self.session, self.captcha_sid)# load captcha img
            #popup with captcha appear
            func = lambda : self.do_login_vk(
                login,
                password,
                captcha_sid=captcha_sid,
                captcha_key=self.captcha_popup.ids.captcha_key.text)
            btn = PopupActionButton("Enter",func, 0.5)
            
            self.captcha_popup.ids.action.clear_widgets()
            self.captcha_popup.ids.action.add_widget(btn)
            
            self.captcha_popup.ids.captcha.source = 'captcha.jpg'
            self.captcha_popup.ids.captcha.reload()# provide img up to date
            self.captcha_popup.open()
            
        elif status in ['Could not connect', 'Wrong password', 'Unknow error', 'Fields should not be empty']: # errors
            # show error
            self.ids.error.text = status
            # close all popups
            self.captcha_popup.dismiss()
            self.secure_code_popup.dismiss()
           
    def do_login_vk_secure_code(self, secure_code, auth_hash, captcha_sid='', captcha_key=''):
        self.session, captcha_sid, status = vk.two_fa(self.session, secure_code,
            auth_hash = auth_hash,
            captcha_sid = captcha_sid,
            captcha_key = captcha_key
        )
        print(self.session, captcha_sid, status)
        print(secure_code)
        if status == 'Logged in':# done
            print('Logged in')
            self.end_login_vk()
            
        elif status == 'Captcha needed':
            if captcha_key:
                self.captcha_popup.ids.error.text = 'Incorrect captcha'
                
            self.secure_code_popup.dismiss()
            vk.captcha(self.session, self.captcha_sid) # load captcha img
            #popup with captcha appear
            func = lambda : self.do_login_vk_secure_code(
                secure_code,
                auth_hash,
                captcha_sid=captcha_sid,
                captcha_key=self.captcha_popup.ids.captcha_key.text
            )
            btn = PopupActionButton("Enter",func, 0.5)
            self.captcha_popup.ids.action.clear_widgets()
            self.captcha_popup.ids.action.add_widget(btn)
            
            self.captcha_popup.ids.captcha.source = 'captcha.jpg'
            self.captcha_popup.ids.captcha.reload()# provide img up to date
            self.captcha_popup.open()
            
        elif status == 'Secure code':
            # show error
            self.secure_code_popup.ids.error.text = 'Incorrect secure code'
            #popup with secure code appear
            func = lambda : self.do_login_vk_secure_code(
                self.secure_code_popup.ids.secure_code.text,
                auth_hash
            )
            btn = PopupActionButton("Enter",func, 0.5)
            self.secure_code_popup.ids.action.clear_widgets()
            self.secure_code_popup.ids.action.add_widget(btn)
            
            self.secure_code_popup.open()
            
        elif status in ['Could not connect', 'Unknow error']: # errors
            # show error
            self.ids.error.text = status
            # close all popups
            self.captcha_popup.dismiss()
            self.secure_code_popup.dismiss()
            
            
    def end_login_vk(self):
        self.captcha_popup.dismiss()
        self.secure_code_popup.dismiss()
        self.reset_forms()
        print('ends')
        
        if vk.pass_security_check(self.session, self.login):
            vk.save_session(self.app.app_dir, self.session)
            self.app.load_session()
            self.manager.transition = SlideTransition(direction="up")
            self.manager.current = 'start'
                       
    ### VK ###

    ### YA ###
    def login_ya(self):
        pass
    ### YA ###

      
class LoginApp(MDApp):
    def switch_to_login(self, media, popup):
        popup.dismiss()
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'login'
        self.manager.get_screen('login').open_login_page(media)    
    
    def build(self): # screen loader
        self.app_dir = getattr(self, 'user_data_dir')

        try:
            os.mkdir(self.app_dir +'/downloads/')
        except FileExistsError:
            pass
        try:
            os.mkdir(self.app_dir +'/sessions/')
        except FileExistsError:
            pass
        try:
            os.mkdir(self.app_dir +'/images/')
        except FileExistsError:
            pass
        try:
            os.mkdir(self.app_dir +'/images/a/')
        except FileExistsError:
            pass
        try:
            os.mkdir(self.app_dir +'/images/t/')
        except FileExistsError:
            pass
        self.manager = ScreenManager()
        self.manager.add_widget(Start(name='start'))
        self.manager.add_widget(Player(name='player'))
        self.manager.add_widget(Album(name='album'))
        self.manager.add_widget(AlbumList(name='album_list'))
        self.manager.add_widget(Login(name='login'))

        return self.manager

    def on_start(self):
        self.meta = Meta(self.app_dir)
        self.audio_bar = [AudioInfo() for _ in range(3)]

        self.main_screen = self.root.screens[0]
        self.player_screen = self.root.screens[1]
        self.album_screen = self.root.screens[2]
        self.album_list_screen = self.root.screens[3]
        self.main_screen.downloaded_audios()
        self.load_session()


    def load_session(self):
        session_list = DrawerList()
        session_dir_list = os.listdir(self.app_dir + '/sessions/')
        self.main_screen.ids.session_container.clear_widgets()
        for elem in session_dir_list:
            self.main_screen.ids.session_container.add_widget(SessionListElement(self, elem))
            self.main_screen.ids.accounts.text = 'Connected accounts'
    
    def audio_play(self, *args, track=None):
        print(track)
        if args:
            slider, touch = args[0][0:2]
            
        self.main_screen.remove_widget(self.audio_bar[0])
        self.album_screen.remove_widget(self.audio_bar[1])
        self.album_list_screen.remove_widget(self.audio_bar[2])
        if track: # Play new audio
            print('Play new audio')
            if track[4] != './icons/track.png':
                self.player_screen.ids.song_image.source=track[4]
                self.player_screen.ids.song_image.reload()
            if 'sound' in dir(self):
                #self.sound.pause()
                self.progressbarEvent.cancel()
                self.settimeEvent.cancel()
                
            self.track = track
            self.album_key = self.album_screen.key if self.manager.current=='album' else None

            self.track_list = self.meta.track_list(key = self.album_key) ###

            track_name = self.track[2] + ' - ' + self.track[3]
            if len(track_name)> 35:
                [rsetattr(i, 'ids.song_name.text', track_name[0:36] + '...') for i in self.audio_bar]
                self.player_screen.ids.song_name.text = track_name[0:36] + '...'

            else:
                [rsetattr(i, 'ids.song_name.text',track_name) for i in self.audio_bar]
                self.player_screen.ids.song_name.text = track_name
                print(self.audio_bar[0].ids.song_name.text)
            self.sound = IOSPlayer(self.track[1],author = self.track[2], song=self.track[3])
            self.sound.play()
            
            [rsetattr(i, 'ids.song_progress.max', self.sound.length) for i in self.audio_bar]
            [rsetattr(i, 'ids.song_progress.value', 0) for i in self.audio_bar]

            # needed conversion from obj  c double to float
            self.player_screen.ids.song_progress.max = self.sound.length
            self.player_screen.ids.song_progress.value = 0
            #
            self.player_screen.ids.song_len.text = time.strftime('%M:%S', time.gmtime(self.sound.length))

        elif 'sound' in dir(self) and args: # Seek audio row
            if True: #slider.collide_point(touch.x, touch.y):
                slider.active = False
                print('seek audio')
                self.audio_pos = slider.value
                self.sound.seek(slider.value)
                [rsetattr(i, 'ids.song_progress.value', self.audio_pos) for i in self.audio_bar]
                self.main_screen.add_widget(self.audio_bar[0])
                self.album_screen.add_widget(self.audio_bar[1])
                self.album_list_screen.add_widget(self.audio_bar[2])
            return
            
        elif 'sound' in dir(self): # Unpause already loaded audio
            print('Unpause already loaded audio')

            ###self.sound.seek(self.audio_pos) no need
            self.sound.play()
            [rsetattr(i, 'ids.song_progress.value',self.audio_pos) for i in self.audio_bar]
            self.player_screen.ids.song_progress.value = self.audio_pos
            
        if 'sound' in dir(self):
            [rsetattr(i, 'ids.song_status.source', "./icons/stop60.png") for i in self.audio_bar]
            [rsetattr(i, 'ids.action.on_release', self.audio_stop) for i in self.audio_bar]
            self.player_screen.ids.song_status.source = "./icons/stop60.png"
            self.player_screen.ids.song_status.reload()
            self.player_screen.ids.action.on_release = self.audio_stop
            # set events
            self.progressbarEvent = Clock.schedule_interval(self.update_progressbar,1)
            self.settimeEvent = Clock.schedule_interval(self.settime,1)
            
        self.main_screen.add_widget(self.audio_bar[0])
        self.album_screen.add_widget(self.audio_bar[1])
        self.album_list_screen.add_widget(self.audio_bar[2])
        
        
    def update_progressbar(self,value):
        [rsetattr(i, 'ids.song_progress.value', self.sound.get_pos()) for i in self.audio_bar]
        self.player_screen.ids.song_progress.value = self.sound.get_pos()
        if self.sound.status == 'stop':
            self.progressbarEvent.cancel()
            self.settimeEvent.cancel()
            self.next_to_play()


    def settime(self, t):
        current_time = time.strftime('%M:%S', time.gmtime(self.audio_bar[0].ids.song_progress.value))
        [rsetattr(i, 'ids.song_timer.text', current_time) for i in self.audio_bar]
        self.player_screen.ids.song_timer.text = current_time
        

    def next_to_play(self):
        print('next to play')
        try:
            next_track = self.track_list[self.track_list.index(self.track)+1]
        except:
            print('list out')
        else:
            self.audio_play(track=next_track)

    def prev_to_play(self):
        print('prev to play')
        try:
            next_track = self.track_list[self.track_list.index(self.track)-1]
        except:
            print('list out')
        else:
            self.audio_play(track=next_track)

            
    def audio_stop(self):
        self.audio_pos = self.player_screen.ids.song_progress.value
        self.progressbarEvent.cancel()
        self.settimeEvent.cancel()

        [rsetattr(i, 'ids.song_status.source', "./icons/play60.png") for i in self.audio_bar]
        [rsetattr(i, 'ids.action.on_release', self.audio_play) for i in self.audio_bar]
        self.player_screen.ids.song_status.source = "./icons/play60.png"
        self.player_screen.ids.song_status.reload()
        self.player_screen.ids.action.on_release = self.audio_play
        
        self.sound.pause()

    def unload_audio(self):
        if 'sound' not in dir(self):
            return
        
        if self.sound.status != 'stop':
            self.audio_stop()
            
        ###self.sound.unload()
        self.main_screen.remove_widget(self.audio_bar[0])
        self.album_screen.remove_widget(self.audio_bar[1])
        self.album_list_screen.remove_widget(self.audio_bar[2])
        
    def switch_to_player(self, o):
        screen_to_return = self.manager.current
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'player'
        self.manager.get_screen('player').open_player(screen_to_return)


if __name__ == '__main__':
    #try:
    LoginApp().run()
    #except:
        #CustomSnackBar("upsy daisy :(").open())
    

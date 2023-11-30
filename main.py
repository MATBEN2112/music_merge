import kivy
from kivy.app import async_runTouchApp
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, ImageLeftWidget, IRightBodyTouch, TwoLineAvatarListItem, ImageLeftWidgetWithoutTouch, ImageRightWidgetWithoutTouch, TwoLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu

import sys
import time
import pickle
import timeit
import csv
import asyncio
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

def force_screen_update(screen):
    pass

async def load_music(screen, track_list = [], offset = 0, album_key = None, session = None, search_query='', global_search=False):
    app = MDApp.get_running_app()
    loading_obj = LoadingTracks()
    screen.ids.container.add_widget(loading_obj)
    number_to_load = 50
    isend = False
    if app.audio_listing_key == 'user':
        if search_query: # search audio
            track_list = search_audio(app.main_screen.track_list,q=search_query)
            
        elif not track_list: # load all
            track_list = app.meta.track_list(key = album_key) # [DB class method]

        for track in track_list[offset:offset + number_to_load]:   
            if track == 'EOF':
                isend = True
            else:
                track_obj = Track(app, track)
                if album_key == app.player.album_key and app.player.get_current_track()[0:5] == track[0:5]: # Now playing UI update
                    track_obj.hilighte()
                    app.player.current_track_obj = track_obj
                        
                screen.ids.container.add_widget(track_obj)
                
    elif app.audio_listing_key == 'vk': # vk api
        if album_key: # load album
            track_list = await session.load_playlist_content(album_key)

        elif search_query: # search audio
            track_list = await session.search(global_search,q = q)

        elif track_list and len(track_list[offset:offset+50]) < 50: # load more
            track_list = await session.load_more_t()
            
        else: # load user audios
            track_list = await session.load_user_audios()
            
        for track in track_list[offset:offset + number_to_load]:
            if track == 'EOF': # list is ended
                isend = True
            else:
                track_obj = VKTrack(session,app,track)
                if album_key == app.player.album_key and app.player.get_current_track()[0:5] == track[0:5]: # Now playing UI update
                    track_obj.hilighte()
                    app.player.current_track_obj = track_obj
                        
                screen.ids.container.add_widget(track_obj)
                
    elif app.audio_listing_key == 'ya':
        pass
                    
    elif app.audio_listing_key == 'selection':
        if not track_list: # load all
            track_list = app.meta.track_list(key = album_key) # [DB class method]
            
        for track in track_list[offset:offset + number_to_load]:
            if track == 'EOF': # list is ended
                isend = True
            else:
                screen.ids.container.add_widget(TrackWithCheckBox(app, track))

    if not track_list: # list container is empty
        screen.ids.container.add_widget(NoAvailableTracks())
    
    print(
        f''''Load user audios.\n
Screen: {screen.name}
Listing_key: {app.audio_listing_key}
Album key: {album_key}
Offset: {offset}
Search query: {search_query}
Global search: {global_search}
Count: {len(track_list)}'''
        )

    screen.track_list = track_list
    screen.isend = isend
    screen.ids.container.remove_widget(loading_obj)

async def load_albums(screen, album_list = [], offset = 0, session = None, search_query='', global_search=False):
    app = MDApp.get_running_app()
    if app.audio_listing_key == 'user':
        album_list = app.meta.album_list() # [DB class method]
        for album in album_list:
            screen.ids.album_container.add_widget(AlbumButton(app, album))

    elif app.audio_listing_key == 'vk':
        album_list = await session.load_playlists()
        for album in album_list:
            screen.ids.album_container.add_widget(
                VKAlbumButton(
                    session,
                    app,
                    album
                )
            )

    elif app.audio_listing_key == 'selection':
        album_list = app.meta.album_list() # [DB class method]
        for album in album_list:
            screen.ids.album_container.add_widget(AlbumButton(app, album))
#################
### Main Screen  ###
#################
class Start(Screen):
    def audios_listing(self, session = None):
        self.isend = False
        if 'lock_updates' not in dir(self):
            self.lock_updates = False
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()
        
        if 'session' and 'track_list' in dir(self): # prevent loading same twise
            if self.session == session:
                print(123)
                return
            if  'session_name' in dir(session) and 'session_name' in dir(self.session) and self.session.session_name == session.session_name:
                print(333333333333)
                return
             
        self.ids.scrollable_container.scroll_y = 1 # return to the top of scrollview
        self.session = session
        self.ids.nav_drawer.set_state('close') # close side menu
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        if self.app.audio_listing_key == 'user':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
            )
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
            )
            
        elif self.app.audio_listing_key == 'vk':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
            )
            
        elif self.app.audio_listing_key == 'selection':
            pass
            
        # prepare tools
        self.ids.tools_container.clear_widgets()
        self.ids.tools_container.add_widget(
            OneLineAvatarIconListItem(
                ImageLeftWidgetWithoutTouch(source="./icons/search.png"),
                text="Search",
                on_release=self.switch_to_search,
                bg_color = "#81BEF7"
            )
        )
        self.ids.tools_container.add_widget(
            OneLineAvatarIconListItem(
                ImageLeftWidgetWithoutTouch(source="./icons/song.png"),
                text="List of Albums",
                on_release=self.switch_to_album_list,
                bg_color = "#81BEF7"
            )
        )
        if self.app.audio_listing_key == 'user':
            pass
        elif self.app.audio_listing_key == 'vk':
            pass
        elif self.app.audio_listing_key == 'selection':
            pass
        
        # prepare list of tracks
        self.ids.container.clear_widgets()
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.app.web_tasks_loop.create_task(
            load_music(self, session = self.session)
        ) # [async music loader]

        print(dir(self.app.web_tasks_loop))
        print(self.app.web_tasks_loop.is_running())
    ### EDIT TOOLS ### 
    def edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": f"Selection","on_release": self.open_selection_menu},
            {"viewclass": "OneLineListItem","text": f"Delete all","on_release": self.app.meta.delete_all},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=4
        )
        self.drop_down_menu.open()
        
    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self))

    def load_more(self):
        self.lock_updates = True
        c = len(self.ids.container.children)
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.app.web_tasks_loop.create_task(load_music(
            self,
            track_list = self.track_list,
            offset = c,
            session = self.session
        )) # [async music loader]

    def unlock(self):
        self.lock_updates = False
        
    def switch_to_album_list(self, o):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album_list'
        self.app.manager.get_screen('album_list').open_album_list(session = self.session)

    def switch_to_search(self,o):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'search'
        self.app.manager.get_screen('search').open_search(session = self.session)

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
        if self.screen_to_return == 'album':
            self.manager.get_screen(self.screen_to_return).open_album(
                self.app.album_screen.album,
                session=self.app.album_screen.session
            )
            
        elif self.screen_to_return == 'album_list':
            self.manager.get_screen(self.screen_to_return).open_album_list(
                session=self.app.album_list_screen.session
            )
            
        elif self.screen_to_return == 'start':
            self.manager.get_screen(self.screen_to_return).audios_listing(
                session=self.app.main_screen.session
            )

##################
### Album Screen ###
##################         
class Album(Screen):
    ### BASE METHODS ###
    def open_album(self, album, session = None):
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()

        if 'session' and 'track_list' in dir(self): # prevent loading same twise
            if self.session == session and self.album == album:
                print(123)
                #self.ids.container.children
                return
            if  'session_name' in dir(session) and 'session_name' in dir(self.session) and self.session.session_name == session.session_name and self.album == album:
                print(33333333333)
                return
            
        self.session = session
        self.album = album
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album())
        )
        if self.app.audio_listing_key == 'user':

            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
            )
        elif self.app.audio_listing_key == 'vk':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/load.png", [0.9, 0.35], func = lambda x: print(123))
            )

        elif self.app.audio_listing_key == 'selection':
            pass
        
        # prepare album info
        self.ids.album_name.text = album[1]
        self.ids.album_image.source = album[2]
        if self.app.audio_listing_key == 'user':
            pass

        elif self.app.audio_listing_key == 'vk':
            pass

        elif self.app.audio_listing_key == 'selection':
            pass
        # prepare track listing
        self.ids.container.clear_widgets()
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.app.web_tasks_loop.create_task(load_music(
            self,
            album_key = self.album[0],
            session = self.session
        )) # [async music loader]
        
    def close_album(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'album_list'
        self.manager.get_screen('album_list').open_album_list(session = self.session)

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
                self.app.meta.delete_album(self.key) # [DB class method]
            except PermissionError: # if file loaded to player 
                self.app.player.stop()
                self.app.meta.delete_album(self.key) # [DB class method]
                
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
            self.app.meta.edit_album(self.key, album_name) # [DB class method]
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
        self.add_widget(SelectionBottomMenu(self.app, self, album = self.album))
 

#####################
### Album List Screen ###
#####################  
class AlbumList(Screen):
    ### BASE METHODS ###
    def open_album_list(self,session=None):
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()
            
        if 'session' and 'album_list' in dir(self): # prevent loading same twise
            if self.session == session:
                print(123)
                return
            if  'session_name' in dir(session) and 'session_name' in dir(self.session) and self.session.session_name == session.session_name:
                print(333333333333)
                return
            
        self.session = session
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem("./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album_list())
        )
        if self.app.audio_listing_key == 'user':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem("./icons/add.png", [0.9, 0.35], func = lambda x: self.add_album())
            )
            
        elif self.app.audio_listing_key == 'vk':
            pass
        
        elif self.app.audio_listing_key == 'selection':
            pass
        #load albums
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.ids.album_container.clear_widgets()
        self.app.web_tasks_loop.create_task(
            load_albums(self,session = self.session)
        ) # [async album loader]
                
    def close_album_list(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'start'
        self.manager.get_screen('start').audios_listing(session = self.session)

    def add_album(self, album_name=None):
        if album_name:
            self.app.meta.add_album(album_name, img=None) # [DB class method]
            self.create_album_popup.dismiss()
            return self.open_album_list()
            
        self.create_album_popup = CreateAlbumPopup()
        func = lambda :self.add_album(album_name=self.create_album_popup.ids.album_name.text)
        btn = PopupActionButton("Enter", func, 0.5)
        self.create_album_popup.ids.action.clear_widgets()
        self.create_album_popup.ids.action.add_widget(btn)
        self.create_album_popup.open()
        
#################
### Search Screen ###
#################
class Search(Screen):
    def close_search(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'start'
        self.manager.get_screen('start').audios_listing(session = self.session)

    def open_search(self,session=None):
        self.session = session
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()

        if not 'search_field' in dir(self):
            self.search_field = SearchFieldLayout(self)
            self.ids.text_input_box.add_widget(self.search_field)


        # prepare track listing
        self.ids.container.clear_widgets()
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.app.web_tasks_loop.create_task(
            load_music(self, session = self.session)
        ) # [async music loader]
        
    def search(self,q=''):
        self.ids.container.clear_widgets()
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
            
        self.app.task = self.app.web_tasks_loop.create_task(load_music(
            self,
            session = self.session,
            search_query=q,
            global_search=self.search_field.search_box.global_mode
        )) # [async music loader]
  
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
        self.manager.add_widget(Search(name='search'))

        return self.manager

    def on_start(self):
        self.task = None
        self.web_tasks_loop = asyncio.get_event_loop()
        with open(self.app_dir + '/resent.csv', 'a', newline='') as _:
            pass
        
        self.platform = kivy.utils.platform
        if self.platform not in ['android','ios']:
            Window.size = (540, 1170)
            from DesktopPlayer import DesktopPlayer
            self.player = DesktopPlayer(self)
    
        elif self.platform == 'ios':
            from IOSPlayer import IOSPlayer
            self.player = IOSPlayer()
    
        elif self.platform == 'android':
            pass
        
        self.meta = Meta(self)
        self.audio_bar = [AudioInfo() for _ in range(3)]

        self.main_screen = self.root.screens[0]
        self.player_screen = self.root.screens[1]
        self.album_screen = self.root.screens[2]
        self.album_list_screen = self.root.screens[3]

        self.audio_listing_key = 'user'
        self.main_screen.audios_listing()
        self.load_session()
        
        if self.platform not in ['android','ios']:
            Window.size = (540, 1170)
            from DownloadMonitorDesktop import DownloadMonitorDesktop
            self.downloader = DownloadMonitorDesktop()
    
        elif self.platform == 'ios':
            from DownloadMonitorIOS import DownloadMonitorIOS
            self.downloader = DownloadMonitorIOS()
    
        elif self.platform == 'android':
            pass

    def load_session(self):
        self.sessions = []
        session_list = DrawerList()
        session_dir_list = os.listdir(self.app_dir + '/sessions/')
        self.main_screen.ids.session_container.clear_widgets()
        for elem in session_dir_list:
            session_obj = SessionListElement(self, elem)
            self.sessions.append(session_obj)
            self.main_screen.ids.session_container.add_widget(session_obj)
            self.main_screen.ids.accounts.text = 'Connected accounts'
    
if __name__ == '__main__':
    if True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(LoginApp().async_run(async_lib='asyncio'))
        loop.close()
    else:
        LoginApp().run()

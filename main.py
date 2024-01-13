import kivy
from kivy.app import async_runTouchApp
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, ImageLeftWidget, IRightBodyTouch, TwoLineAvatarListItem, ImageLeftWidgetWithoutTouch, ImageRightWidgetWithoutTouch, TwoLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu

import asyncio
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivymd.uix.relativelayout import MDRelativeLayout
import os
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
from kivy.properties import ObjectProperty, ColorProperty

from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage

import vk_methods as vk
from custom_widgets import *
### TODO list ###
# 1) make on player bar offset [FIXED] make offset appear only if audio_bar is open 
# 2) fix overscroll [FIXED] block on loading
# 3) make loading indicator for track [FIXED]
# 4) new loading indicator for scrollview [FIXED]
# 5) fix vk search [FIXED]
# 6) track count in album
# 7) make reload of screen on any change (delete, edit, add tracks)
# 8) close audio_bar on side menu open
# 9) track highlight does not work properly sometimes
# 10) side menu touch event should not trigger scrollview and scrollview elements

async def load_music(
    screen,
    track_list = None,
    offset = 0,
    album_key = None,
    session = None,
    search_query='',
    global_search=False
    ):
    
    app = MDApp.get_running_app()

    number_to_load = 50
    isend = False
    state = ''
    if app.audio_listing_key == 'user':
        if search_query: # search audio
            app.load_event_start()
            track_list = search_audio(app.main_screen.track_list,q=search_query)
            state = 'search user audio'
            
        elif not track_list: # load all
            app.load_event_start()
            track_list = app.meta.track_list(key = album_key) # [DB class method]
            state = 'load user audio'

        for track in track_list[offset:offset + number_to_load]:
            if 'temp' in track:
                continue
            if track == 'EOF':
                isend = True

            else:
                track_obj = Track(app, track)
                if album_key == app.player.album_key and app.player.get_current_track()[0:5] == track[0:5]: # Now playing UI update
                    track_obj.highlighte()
                    app.player.current_track_obj = track_obj
                        
                screen.ids.container.add_widget(track_obj)
                
    elif app.audio_listing_key == 'vk': # vk api
        if album_key: # load album
            app.load_event_start()
            track_list = await session.load_playlist_content(album_key)
            state = 'load vk album audio'

        elif search_query: # search audio
            app.load_event_start()
            track_list = await session.search(global_search,q = search_query)
            state = 'search vk audio'

        elif track_list and len(track_list[offset:offset+number_to_load]) < number_to_load: # load more
            track_list += await session.load_more_t()
            state = 'lode more vk audio'
            
        elif not track_list: # load user audios
            app.load_event_start()
                
            track_list = await session.load_user_audios()
            state = 'load vk audio'
            
        for track in track_list[offset:offset + number_to_load]:
            if track == 'EOF': # list is ended
                isend = True
                
            else:
                track_obj = VKTrack(session,app,track)
                if album_key == app.player.album_key and app.player.get_current_track()[0:5] == track[0:5]: # Now playing UI update
                    track_obj.highlighte()
                    app.player.current_track_obj = track_obj
                        
                screen.ids.container.add_widget(track_obj)
                
    elif app.audio_listing_key == 'ya':
        pass
                    
    elif app.audio_listing_key == 'selection':
        if not track_list: # load all
            track_list = app.meta.track_list(key = album_key) # [DB class method]
            
        for track in track_list[offset:offset + number_to_load]:
            if 'temp' in track:
                continue
            if track == 'EOF': # list is ended
                isend = True

            else:
                screen.ids.container.add_widget(TrackWithCheckBox(app, track))

    if len(track_list)==1: # list container is empty
        screen.ids.container.add_widget(NoAvailableTracks())
        
    elif isend:
        screen.ids.container.add_widget(EndOfTheList())
        
    print(
        f''''Load user audios.\n
State: {state}
Screen: {screen.name}
Listing_key: {app.audio_listing_key}
Album key: {album_key}
Offset: {offset}
Search query: {search_query}
Global search: {global_search}
Count: {len(track_list)}'''
        )
    if screen.name == 'album':
        screen.ids.count.text = str(len(track_list)) + " track in album"
    screen.track_list = track_list
    screen.isend = isend
    app.load_event_stop()

async def load_albums(
    screen,
    album_list = None,
    offset = 0,
    session = None,
    search_query='',
    global_search=False
    ):
    
    app = MDApp.get_running_app()

    number_to_load = 12
    isend = False
    
    if app.audio_listing_key == 'user':
        if search_query: # search audio
            pass

        elif not album_list: # load all
            app.load_event_start()
            album_list = app.meta.album_list() # [DB class method]
            
        for album in album_list[offset:offset + number_to_load]:
            if 'temp' in album:
                continue

            if album == 'EOF':
                isend = True
                
            else:
                screen.ids.container.add_widget(AlbumButton(app, album))


    elif app.audio_listing_key == 'vk':
        if search_query: # search album
            pass

        elif album_list and len(album_list[offset:offset+number_to_load]) < number_to_load: # load more
            album_list += await session.load_more_a()
            
        elif not album_list: # load user albums
            app.load_event_start()
            album_list = await session.load_playlists()
            
        for album in album_list[offset:offset + number_to_load]:
            if album == 'EOF': # list is ended
                isend = True
                
            else:
                album_obj = VKAlbumButton(session, app, album)
                screen.ids.container.add_widget(album_obj)

    elif app.audio_listing_key == 'ya':
        pass

    elif app.audio_listing_key == 'selection':
        app.load_event_start()
        album_list = app.meta.album_list() # [DB class method]
        for album in album_list:
            screen.ids.container.add_widget(AlbumButton(app, album))

    screen.album_list = album_list
    screen.isend = isend
    print(
        f''''Load user albums.\n
Screen: {screen.name}
Offset: {offset}
Search query: {search_query}
Global search: {global_search}
Count: {len(album_list)}'''
        )
    app.load_event_stop()


def task_manager(root):
    if root.app.task and not root.app.task.done():
        root.app.task.cancel()
                
        for screen in root.app.manager.screens:
            if 'session' in dir(screen) and screen.name != root.name:
                delattr(screen,'session')

                       
    root.ids.container.clear_widgets()


def prevent_loading_same(screen,album,session = None):
    if 'app' not in dir(screen):
        screen.app = MDApp.get_running_app()
                
    if 'session' in dir(screen) and 'track_list' in dir(screen): # prevent loading same twise
        if album:
            if screen.session == session and screen.album == album:
                return True

        else:
            if screen.session == session:
                return True
            
    return False

class CustomScreen(Screen):
    async def force_screen_update(self,scroll_view):
        if 'session' not in dir(self):
            return

        if self.name == 'start':
            scroll_view.loading_container_up.load_sign.start_anim()
            self.ids.container.clear_widgets()
            await load_music(self, session = self.session)
            scroll_view.loading_container_up.load_sign.stop_anim()
        
        elif self.name == 'album':
            scroll_view.loading_container_up.load_sign.start_anim()
            self.ids.container.clear_widgets()
            await load_music(self, album_key = self.album[0], session = self.session)
            scroll_view.loading_container_up.load_sign.stop_anim()

        elif self.name == 'album_list':
            scroll_view.loading_container_up.load_sign.start_anim()
            self.ids.container.clear_widgets()
            await load_albums(self, session = self.session)
            scroll_view.loading_container_up.load_sign.stop_anim()

#################
### Main Screen  ###
#################
class Start(CustomScreen):
    def audios_listing(self, session = None):
        if prevent_loading_same(self, None, session=session):
            print('Already loaded')
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
        task_manager(self) # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
            load_music(self, session = self.session)
        ) # [async music loader]


    ### EDIT TOOLS ### 
    def edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": f"Selection","on_release": self.open_selection_menu},
            {"viewclass": "OneLineListItem","text": f"Delete all","on_release": self.delete_all},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=4
        )
        self.drop_down_menu.open()
        
    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self))

    def delete_all(self):
        self.app.meta.delete_all() # DB class method
        for screen in self.app.manager.screens:
            if 'session' in dir(screen):
                delattr(screen,'session')
                
        self.audios_listing()

    async def load_more(self,scroll_view):
        scroll_view.loading_container_down.load_sign.start_anim()
        c = len(self.ids.container.children)
   
        await load_music(
            self,
            track_list = self.track_list,
            offset = c,
            session = self.session
        ) # [async music loader]
        scroll_view.loading_container_down.load_sign.stop_anim()
        
    def switch_to_album_list(self, o):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album_list'
        self.app.manager.get_screen('album_list').open_album_list(session = self.session)

    def switch_to_search(self,o):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'search'
        self.app.manager.get_screen('search').open_search(session = self.session)

class Player(CustomScreen):  
    def loop_audio(self):
        pass

##################
### Album Screen ###
##################         
class Album(CustomScreen):
    def open_album(self, album, session = None):
        if prevent_loading_same(self, album, session = session):
            print('Already loaded')
            return

        self.session = session
        self.album = album

        self.ids.scrollable_container.scroll_y = 1 # return to the top of scrollview
        
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
        task_manager(self) # cancel previously initiated tasks
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
            self.app.meta.delete_album(self.album[0]) # [DB class method]
                
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
            self.app.meta.edit_album(self.album[0], album_name) # [DB class method]
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

    async def load_more(self,scroll_view):
        scroll_view.loading_container_down.load_sign.start_anim()
        c = len(self.ids.container.children)
   
        await load_music(
            self,
            track_list = self.track_list,
            offset = c,
            session = self.session
        ) # [async music loader]
        scroll_view.loading_container_down.load_sign.stop_anim()
 

#####################
### Album List Screen ###
#####################  
class AlbumList(CustomScreen):
    ### BASE METHODS ###
    def open_album_list(self,session=None):
        if prevent_loading_same(self, None, session=session):
            print('Already loaded')
            return
        
        self.session = session

        self.ids.scrollable_container.scroll_y = 1 # return to the top of scrollview
        
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
        task_manager(self) # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
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

    async def load_more(self,scroll_view):
        scroll_view.loading_container_down.load_sign.start_anim()
        c = len(self.ids.container.children)
   
        await load_albums(
            self,
            album_list = self.album_list,
            offset = c,
            session = self.session
        ) # [async music loader]
        scroll_view.loading_container_down.load_sign.stop_anim()
        
#################
### Search Screen ###
#################
class Search(CustomScreen):
    def close_search(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'start'
        self.manager.get_screen('start').audios_listing(session = self.session)

    def open_search(self,session=None):
        self.global_mode = False
        self.session = session
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()

        # prepare track listing
        task_manager(self) # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
            load_music(self, session = self.session)
        ) # [async music loader]
        
    def search(self,q):
        self.dd.search(q)
        task_manager(self) # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(load_music(
            self,
            session = self.session,
            search_query=q,
            global_search=self.global_mode
        )) # [async music loader]

    def clean_search(self):
        self.ids.search_input.text = ''

    def switch_search(self, *args):
        if True: #self.session:
            self.global_mode = not self.global_mode
            if self.global_mode:
                self.ids.mode_btn_img.source = "./icons/glob_search.png"
            else:
                self.ids.mode_btn_img.source = "./icons/search.png"

            self.ids.search_input.focus = True
            self.show_resent(self.ids.search_input.text)
                

    def show_resent(self,q):
        print('show resent')
        if 'dd' in dir(self):
            self.dd.dismiss()
        if self.ids.search_input.focus:
            self.dd = DropDownResent(self, self.ids.search_row,q)
        
    

  
#################
### Login Screen ###
#################
class Login(CustomScreen):
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
    # colors
    load_clr = ColorProperty(defaultvalue=(255/255, 255/255, 255/255, 1))
    # white color scheam
    main_clr = ColorProperty(defaultvalue=(59/255, 85/255, 158/255, 1))
    main_clr2 = ColorProperty(defaultvalue=(129/255, 190/255, 247/255, 1))
    secondary_clr1 = ColorProperty(defaultvalue=(179/255, 164/255, 111/255, 1))
    secondary_clr2 = ColorProperty(defaultvalue=(184/255, 169/255, 101/255, 1))
    text_clr = ColorProperty()
    interactive_text_clr = ColorProperty()
    btn_hitbox_clr = ColorProperty(defaultvalue=(1,1,1,.1))
    
    loading_list = ObjectProperty(LoadingBar(
        anim_mode = 'fill',
        size_hint = (None,None),
        label_clr = (0,0,1,1),
        filling_clr = (59/255, 85/255, 158/255, 0.4),
        height = "800dp",body_clr = (1,0,0,1)))
    

    def load_event_start(self):
        self.load_event_stop()
        self._current = self.manager.current
        anim = Animation(
            load_clr=(59/255, 85/255, 158/255, 0.1),
            t="linear",
            duration=1,
        )
        anim += Animation(
            load_clr=(255/255, 255/255, 255/255, 1),
            t="linear",
            duration=1,
        )
        anim.repeat = True
        anim.start(self)

    def load_event_stop(self):
        Animation.cancel_all(self, "load_clr")
        self.load_clr = (1,1,1,1)

    def on_load_clr(self,*args):
        if self._current != self.manager.current:
            pass
            #self.load_event_stop()
        
        
    def switch_to_login(self, media, popup):
        popup.dismiss()
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'login'
        self.manager.get_screen('login').open_login_page(media)    
    
    def build(self): # screen loader
        self.ls_up_start, self.ls_down_start, \
        self.ls_up_album, self.ls_down_album, \
        self.ls_up_albumlist, self.ls_down_albumlist = \
        [LoadSign(
            body_clr = (0,0,0,0),
            dot1_clr=(59/255, 85/255, 158/255, 1),
            dot2_clr=(129/255, 190/255, 247/255, 1),
            dot3_clr=(59/255, 85/255, 158/255, 1),
            dot_spacing="50dp"
        ) for _ in range(6)]
        
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
        self.screen_container = DraggableScreenLayout(direction = 'bottom', border = 0)
        
        self.main_screen = Start(name='start')
        self.player_screen = Player(name='player')
        self.album_screen = Album(name='album')
        self.album_list_screen = AlbumList(name='album_list')
        self.login_screen = Login(name='login')
        self.search_screen = Search(name='search')
        self.audio_bar = AudioInfo()
        
        self.manager.add_widget(self.main_screen)
        self.manager.add_widget(self.album_screen)
        self.manager.add_widget(self.album_list_screen)
        self.manager.add_widget(self.login_screen)
        self.manager.add_widget(self.search_screen)
        
        
        self.screen_container.add_widget(self.manager)
        self.screen_container.add_widget(self.player_screen)
        self.screen_container.add_widget(self.audio_bar)
        self.screen_container.fbind('isopen',lambda *args: self.audio_bar.hide() if self.screen_container.isopen else self.audio_bar.show())

        self.platform = kivy.utils.platform
        if self.platform not in ['android','ios']:
            Window.size = (540, 1170)
            from download_monitor import DownloadMonitorDesktop
            self.downloader = DownloadMonitorDesktop()
            
            from player import DesktopPlayer
            self.player = DesktopPlayer(self)
    
        elif self.platform == 'ios':
            from download_monitor import DownloadMonitorIOS
            self.downloader = DownloadMonitorIOS()

            from player import IOSPlayer
            self.player = IOSPlayer(self)
    
        elif self.platform == 'android':
            pass


        return self.screen_container

    def on_start(self):
        self.task = None
        self.web_tasks_loop = asyncio.get_event_loop()
        with open(self.app_dir + '/resent.csv', 'a', newline='') as _:
            pass
        
        self.meta = Meta(self)

        self.audio_listing_key = 'user'
        self.main_screen.audios_listing()
        self.load_session()
        
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

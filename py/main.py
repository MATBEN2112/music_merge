from kivy.app import async_runTouchApp
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform

import vk_methods as vk
from custom_widgets import *
### TODO list ###
# 1) make on player bar offset [FIXED] make offset appear only if audio_bar is open 
# 2) fix overscroll [FIXED] block on loading
# 3) make loading indicator for track [FIXED]
# 4) new loading indicator for scrollview [FIXED]
# 5) fix vk search [FIXED]
# 6) track count in album [FIXED]
# 7) make reload of screen on any change (delete, edit, add tracks) [FIXED] almost done secondary text update problem
# 8) close audio_bar on side menu open
# 9) track highlight does not work properly sometimes [FIXED]
# 10) side menu touch event should not trigger scrollview and scrollview elements
# 11) rebuild login scheam
# 12)


class CustomScreen(Screen):        
    def prevent_loading_same(self,album,session = None):
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()

        def _():
            if self.app.player.get_current_track():
                for child in self.ids.container.container.children:
                    if not isinstance(child, (Track,VKTrack)):
                        continue
                    
                    if self.app.player.get_current_track() == child.track[1]:
                        child.highlighte()
                        self.app.player._highlighted.append(child)
                        break
                
        if 'session' in dir(self): # prevent loading same twise
            if album:
                if self.session == session and self.album == album:
                    _()
                    return True

            else:
                if self.session == session:
                    _()
                    return True
            
        return False

    def task_manager(self):
        if self.app.task and not self.app.task.done():
            self.app.task.cancel()
                
            for screen in self.app.manager.screens:
                if 'session' in dir(screen) and screen.name != self.name:
                    delattr(screen,'session')
    
    async def load_music(self,album_id = None,search_query= '',global_search=False,reload = False):
        self.ids.container.clear()
        if self.app.audio_listing_key == 'user':
            if search_query: # search audio
                self.app.load_event_start()
                track_list = search_audio(self.app.main_screen.ids.container.get_listing()[2],q=search_query)
                
            else: # load all
                self.app.load_event_start()
                track_list = self.app.meta.track_list(key = album_id) # [DB class method]

            self.ids.container.set_listing(
                child_class = Track,
                child_args=(None, self.app,),
                child_kwargs = track_list,
                album_id = album_id
            ) # [listing method]
                    
        elif self.app.audio_listing_key == 'vk': # vk api
            if album_id: # load album
                self.app.load_event_start()
                track_list = await self.session.load_user_audios(
                    reload=reload,
                    album_id=album_id,
                )
                
            elif search_query: # search audio
                self.app.load_event_start()
                track_list = await self.session.search(global_search,q = search_query)

            else: # load user audios
                self.app.load_event_start()
                track_list = await self.session.load_user_audios(reload=reload)
                
            self.ids.container.set_listing(
                child_class = VKTrack,
                child_args=(self.session, self.app,),
                child_kwargs = track_list,
                album_id = album_id
            ) # [listing method]
                    
        elif self.app.audio_listing_key == 'ya':
            pass
                        
        elif self.app.audio_listing_key == 'selection':
            track_list = self.app.meta.track_list(key = album_id) # [DB class method]
                
            self.ids.container.set_listing(
                child_class = TrackWithCheckBox,
                child_args=(None, self.app,),
                child_kwargs = track_list,
                album_id = album_id
            ) # [listing method]
            

        if self.name == 'album':
            self.ids.count.text = str(len(track_list)-1) + " track in album"

        self.app.load_event_stop()

    async def load_albums(self, offset = 0, search_query='', global_search=False, reload=False):
        if self.app.audio_listing_key == 'user':
            if search_query: # search 
                pass

            else: # load all
                self.app.load_event_start()
                album_list = self.app.meta.album_list() # [DB class method]

            self.ids.container.set_listing(
                child_class = AlbumButton,
                child_args=(None, self.app,),
                child_kwargs = album_list
            ) # [listing method]

        elif self.app.audio_listing_key == 'vk':
            if search_query: # search album
                pass
                
            else: # load user albums
                self.app.load_event_start()
                album_list = await self.session.load_playlists(reload=reload)
                
            self.ids.container.set_listing(
                child_class = AlbumButton,
                child_args=(self.session, self.app,),
                child_kwargs = album_list
            ) # [listing method]

        elif self.app.audio_listing_key == 'ya':
            pass

        elif self.app.audio_listing_key == 'selection':
            self.app.load_event_start()
            album_list = self.app.meta.album_list() # [DB class method]
            self.ids.container.set_listing(
                child_class = AlbumButton,
                child_args=(self.session, self.app,),
                child_kwargs = album_list
            ) # [listing method]


        self.app.load_event_stop()
        
    async def force_screen_update(self,scroll_view):
        if 'session' not in dir(self):
            return

        if self.name in ['start','search']:
            await self.load_music(reload=True)
        
        elif self.name == 'album':
            await self.load_music(album_id = self.album[0],reload=True)

        elif self.name == 'album_list':
            await self.load_albums(reload=True)

#################
### Main Screen  ###
#################
class Start(CustomScreen):
    def audios_listing(self, session = None):
        if self.prevent_loading_same(None, session=session):
            print('Already loaded')            
            return
             
        self.ids.container.scroll_view.scroll_y = 1 # return to the top of scrollview
        self.ids.accounts_list.scroll_y = 1
        self.session = session
        self.ids.nav_drawer.set_state('close') # close side menu
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        if self.app.audio_listing_key == 'user':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
            )
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
            )
            
        elif self.app.audio_listing_key == 'vk':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/menu.png", [0.1, 0.35], func = lambda x: self.ids.nav_drawer.set_state('toggle'))
            )
            
        elif self.app.audio_listing_key == 'selection':
            pass
            
        # prepare tools
        if self.app.audio_listing_key == 'user':
            self.ids.main_screen_header.clear_widgets()
            self.ids.main_screen_header.add_widget(
                Tool(
                    self.ids.menu_row,
                    title="./icons/search.png",
                    text="Search",
                    action=self.switch_to_search,
                    bg_color = "#81BEF7"
                )
            )
            self.ids.main_screen_header.add_widget(
                Tool(
                    self.ids.menu_row,
                    title="./icons/song.png",
                    text="List of Albums",
                    action=self.switch_to_album_list,
                    bg_color = "#81BEF7"
                )
            )
        
        elif self.app.audio_listing_key == 'vk':
            self.ids.main_screen_header.clear_widgets()
            self.ids.main_screen_header.add_widget(
                Tool(
                    self.ids.menu_row,
                    title="./icons/search.png",
                    text="Search",
                    action=self.switch_to_search,
                    bg_color = "#81BEF7"
                )
            )
            self.ids.main_screen_header.add_widget(
                Tool(
                    self.ids.menu_row,
                    title="./icons/song.png",
                    text="List of Albums",
                    action=self.switch_to_album_list,
                    bg_color = "#81BEF7"
                )
            )
        elif self.app.audio_listing_key == 'selection':
            pass
        
        # prepare list of tracks
        self.task_manager() # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
            self.load_music()
        ) # [async music loader]

    def edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": "Selection",  "height": dp(50),
             "on_release": self.open_selection_menu},
            {"viewclass": "OneLineListItem","text": "Delete all", "height": dp(50),
             "on_release": self.delete_all},
            {"viewclass": "OneLineListItem","text": "", "height": dp(20)},
            # dev purpose{"viewclass": "OneLineListItem","text": f"Popup debug","on_release": self.show_popup},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=4
        )
        self.drop_down_menu.open()
        
    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self))

    def delete_all(self, state=None):
        self.drop_down_menu.dismiss()
        if state:
            self.popup.dismiss()
            self.app.meta.delete_all() # DB class method
            self.app.change_appear()
            delattr(self,'session')
            return self.audios_listing()
        
        self.popup = ConfirmationPopup()
        self.popup.ids.info.text = 'Are you sure want to delete all'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_all(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()

    def show_popup(self):
        if 'popup_list' not in dir(self):
            self.popup_list = [
                CaptchaPopup,SecureCodePopup,CreateAlbumPopup,
                ConfirmationPopup,RenameAlbumPopup,
                AddToAlbumPopup,RenameTrackPopup]

        if 'popup_index' not in dir(self):
            self.popup_index = 0

        self.popup_list[self.popup_index]().open()
        self.popup_index += 1 if self.popup_index < len(self.popup_list)-1 else -self.popup_index
        
    def switch_to_album_list(self):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album_list'
        self.app.manager.get_screen('album_list').open_album_list(session = self.session)

    def switch_to_search(self):
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'search'
        self.app.manager.get_screen('search').open_search(session = self.session)

class Player(CustomScreen):
    def open_player(self, *args, app = None):
        app.audio_bar.hide() if app.screen_container.isopen else app.audio_bar.show()
        app.main_screen.ids.nav_drawer.enable_swiping = not app.main_screen.ids.nav_drawer.enable_swiping

    def loop_audio(self):
        pass

##################
### Album Screen ###
##################         
class Album(CustomScreen):
    def open_album(self, album, session = None):
        if self.prevent_loading_same(album, session = session):
            print('Already loaded')
            return

        self.session = session
        self.album = album

        self.ids.container.scroll_view.scroll_y = 1 # return to the top of scrollview
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        
        if self.app.audio_listing_key == 'user':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album())
            )
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/edit.png", [0.9, 0.35], func = lambda x: self.edit_menu())
            )
        elif self.app.audio_listing_key == 'vk':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album())
            )
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/load.png", [0.9, 0.35], func = lambda x: print(123))
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
        self.task_manager() # cancel previously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(self.load_music(
            album_id = self.album[0]
        )) # [async music loader]
        
    def close_album(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'album_list'
        self.manager.get_screen('album_list').open_album_list(session = self.session)

    def edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": f"Selection",  "height": dp(50),
             "on_release": self.open_selection_menu},
            {"viewclass": "OneLineListItem","text": f"Delete album",  "height": dp(50),
             "on_release": self.delete_album},
            {"viewclass": "OneLineListItem","text": f"Rename album",  "height": dp(50),
             "on_release": self.rename_album},
            {"viewclass": "OneLineListItem","text": "", "height": dp(20)},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self.ids.menu_row, items=menu_items,position="center",width_mult=3
        )
        self.drop_down_menu.open()

    def delete_album(self, state=None):
        self.drop_down_menu.dismiss()
        if state:
            self.app.meta.delete_album(self.album[0]) # [DB class method]
            self.popup.dismiss()
            self.app.change_appear()
            return self.close_album()
        
        self.popup = ConfirmationPopup()
        self.popup.ids.info.text = 'Are you sure want to delete album'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_album(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
    
    def rename_album(self, album_name=None):
        self.drop_down_menu.dismiss()
        if album_name:
            self.app.meta.edit_album(self.album[0], album_name) # [DB class method]
            self.popup.dismiss()
            self.ids.album_name.text = album_name
            self.app.change_appear()
            return
        
        elif isinstance(album_name,str):
            return
        
        self.popup = RenameAlbumPopup()

        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.album_name.text = self.ids.album_name.text
        self.popup.ids.action.bind(
            on_release= lambda *args:self.rename_album(
                album_name=self.popup.ids.album_name.text
            )
        )
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()

    def open_selection_menu(self):
        self.drop_down_menu.dismiss()
        self.add_widget(SelectionBottomMenu(self.app, self, album = self.album))
 

#####################
### Album List Screen ###
#####################  
class AlbumList(CustomScreen):
    ### BASE METHODS ###
    def open_album_list(self,session=None):
        if self.prevent_loading_same(None, session=session):
            print('Already loaded')
            return
        
        self.session = session

        self.ids.container.scroll_view.scroll_y = 1 # return to the top of scrollview
        
        # prepare top app bar
        self.ids.menu_row.clear_widgets()
        self.ids.menu_row.add_widget(
            TopAppBarMenuElem(self.app, "./icons/back.png", [0.1, 0.35], func = lambda x: self.close_album_list())
        )
        if self.app.audio_listing_key == 'user':
            self.ids.menu_row.add_widget(
                TopAppBarMenuElem(self.app, "./icons/add.png", [0.9, 0.35], func = lambda x: self.add_album())
            )
            
        elif self.app.audio_listing_key == 'vk':
            pass
        
        elif self.app.audio_listing_key == 'selection':
            pass
        #load albums
        self.task_manager() # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
            self.load_albums()
        ) # [async album loader]
                
    def close_album_list(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = 'start'
        self.manager.get_screen('start').audios_listing(session = self.session)

    def add_album(self, album_name=None, img = None):
        if album_name:
            self.app.meta.add_album(album_name, img=img) # [DB class method]
            self.popup.dismiss()
            delattr(self,'session')
            return self.open_album_list()
        
        elif isinstance(album_name,str):
            self.popup.dismiss()
               
        self.popup = CreateAlbumPopup()
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(
            on_release= lambda *args:self.add_album(
                album_name=self.popup.ids.album_name.text
            )
        )
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()

        
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
        self.ids.mode_btn_img.source = "./icons/search.png"
        self.session = session
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()

        if self.app.audio_listing_key == 'user':
            self.ids.search_input.hint_text = 'Search loaded audios'
            
        elif self.app.audio_listing_key == 'vk':
            self.ids.search_input.hint_text = 'Search VK audios'

        elif self.app.audio_listing_key == 'ya':
            pass
        
        elif self.app.audio_listing_key == 'selection':
            pass

        self.task_manager() # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(
            self.load_music()
        ) # [async music loader]
        
    def search(self,q):
        self.dd.search(q)
        self.task_manager() # cancel priviously initiated tasks
        self.app.task = self.app.web_tasks_loop.create_task(self.load_music(
            search_query=q,
            global_search=self.global_mode
        )) # [async music loader]

    def clean_search(self):
        self.ids.search_input.text = ''

    def switch_search(self, *args):
        if self.app.audio_listing_key != 'user':
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
### Has not yet tested use careful 
class Login(CustomScreen):
    
    def close_login_page(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = 'start'

    def open_login_page(self,media):
        if 'app' not in dir(self):
            self.app = MDApp.get_running_app()
            self.action_func = None

        self.app.player.stop()
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
            self.ids.error.text = ''
            self.captcha_popup.dismiss()
            #popup with secure code appear
            self.secure_code_popup.ids.error.text = ''
            self.secure_code_popup.ids.action.unbind(on_release= self.action_func)
            self.action_func = lambda *args: self.do_login_vk_secure_code(
                self.secure_code_popup.ids.secure_code.text,
                auth_hash
            )
            self.secure_code_popup.ids.action.ids.text.text = "Confirm"
            self.secure_code_popup.ids.action.bind(on_release= self.action_func)
            self.secure_code_popup.ids.cancel.ids.text.text = "Cancel"
            self.secure_code_popup.open()
            
        elif status == 'Captcha needed':
            self.ids.error.text = ''
            if captcha_key:
                self.captcha_popup.ids.error.text = 'Incorrect captcha'
            else:
                self.captcha_popup.ids.error.text = ''
            vk.captcha(self.app.app_dir,self.session, self.captcha_sid)# load captcha img
            #popup with captcha appear
            self.captcha_popup.ids.action.unbind(on_release= self.action_func)
            self.action_func = lambda *args: self.do_login_vk(
                login,
                password,
                captcha_sid=captcha_sid,
                captcha_key=self.captcha_popup.ids.captcha_key.text)
            self.captcha_popup.ids.action.ids.text.text = "Confirm"
            self.captcha_popup.ids.action.bind(on_release= self.action_func)
            self.captcha_popup.ids.cancel.ids.text.text = "Cancel"
            
            self.captcha_popup.ids.captcha.source = self.app.app_dir+'captcha.jpg' #[FIX] provide app full path
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
            self.ids.error.text = ''
            if captcha_key:
                self.captcha_popup.ids.error.text = 'Incorrect captcha'
            else:
                self.captcha_popup.ids.error.text = ''
                
            self.secure_code_popup.dismiss()
            vk.captcha(self.session, self.captcha_sid) # load captcha img
            #popup with captcha appear
            self.captcha_popup.ids.action.unbind(on_release= self.action_func)
            self.action_func = lambda *args: self.do_login_vk_secure_code(
                secure_code,
                auth_hash,
                captcha_sid=captcha_sid,
                captcha_key=self.captcha_popup.ids.captcha_key.text
            )
            self.captcha_popup.ids.action.ids.text.text = "Confirm"
            self.captcha_popup.ids.action.bind(on_release= self.action_func)
            self.captcha_popup.ids.cancel.ids.text.text = "Cancel"
            
            self.captcha_popup.ids.captcha.source = self.app.app_dir+'captcha.jpg'
            self.captcha_popup.ids.captcha.reload()# provide img up to date
            self.captcha_popup.open()
            
        elif status == 'Secure code':
            self.ids.error.text = ''
            # show error
            self.secure_code_popup.ids.error.text = 'Incorrect secure code'
            #popup with secure code appear
            self.secure_code_popup.ids.action.unbind(on_release= self.action_func)
            self.action_func = lambda *args: self.do_login_vk_secure_code(
                self.secure_code_popup.ids.secure_code.text,
                auth_hash
            )
            self.secure_code_popup.ids.action.ids.text.text = "Confirm"
            self.secure_code_popup.ids.action.bind(on_release= self.action_func)
            self.secure_code_popup.ids.cancel.ids.text.text = "Cancel"
            
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
    secondary_clr1 = ColorProperty(defaultvalue=(222/255, 222/255, 222/255, 1))
    secondary_clr2 = ColorProperty(defaultvalue=(184/255, 184/255, 184/255, 1))
    text_clr = ColorProperty(defaultvalue=(0,0,0,1))
    err_text_clr = ColorProperty(defaultvalue=(1,0,0,1))
    interactive_text_clr = ColorProperty()
    btn_hitbox_clr = ColorProperty(defaultvalue=(1,0,0,0))
    
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
        self.screen_container = DraggableScreenLayout(
            direction = 'bottom',
            border = 0,
            low_priority=(Button,ScrollView,SideMenu),
            swipe_threshold = 0.7)
        
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
        self.screen_container.fbind('isopen',self.player_screen.open_player,app=self)

        self.platform = platform
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
        if not session_dir_list:
            pass
            
        for elem in session_dir_list:
            session_obj = SessionListElement(self, elem)
            if session_obj.is_session:
                self.sessions.append(session_obj)
                self.main_screen.ids.session_container.add_widget(session_obj)

    def change_appear(self):
        for screen in self.manager.screens:
                if 'session' in dir(screen) and screen.name != self.manager.current:
                    delattr(screen,'session')
    
if __name__ == '__main__':
    if True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(LoginApp().async_run(async_lib='asyncio'))
        loop.close()
    else:
        LoginApp().run()

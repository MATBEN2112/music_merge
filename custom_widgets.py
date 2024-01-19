from kivymd.uix.behaviors import TouchBehavior
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivymd.uix.list import (OneLineAvatarIconListItem,
                             IconRightWidget,
                             IRightBodyTouch,
                             ImageLeftWidgetWithoutTouch,
                             ImageRightWidgetWithoutTouch,
                             TwoLineAvatarIconListItem,
                             TwoLineIconListItem)

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.image import Image, AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDIconButton
from kivy.core.text import Label as CoreLabel
from kivy.metrics import sp, dp
import os
from vk_methods import VK_session
import shutil
import pickle
from kivy.clock import Clock
from utils import *
import re
import asyncio

from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.animation import Animation
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty)

from drop_down_resent import DropDownResent
from ticker import Ticker
from updatable_scrollview import UpdatableScrollView
from draggablescreenlayout import DraggableScreenLayout
from animations import LoadSign, CircularProgressBar, LoadingBar
from album import AlbumButton
#from sidemenu import SideMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.properties import ListProperty, OptionProperty, DictProperty, NumericProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

    
class PopupBody(BoxLayout):
    pass

class PopupActionButton(MDRelativeLayout, ButtonBehavior, TouchBehavior):
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.dispatch('on_release')
            return True
            
class LoginButton(MDRelativeLayout, TouchBehavior):
    def __init__(self, func):
        super(LoginButton, self).__init__()
        self.add_widget(MDLabel(text='Connect', font_size = '36sp', pos_hint={"center_x": .5, "center_y": 0.5}, halign="center"))

        #self.background_color= 0,0,0,0
        self.pos_hint={'center_x':0.5, 'center_y':0.1}
        self.size=("300dp","80dp")
        self.size_hint=(None,None)
        self.func = func
        with self.canvas.before:
                Color((.4,.4,.4,1), mode='rgba')
                RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
                
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.func()

class PlayerBack(MDRelativeLayout):
    def __init__(self, img):
        super(PlayerBack, self).__init__()
        self.size_hint=(None,None)
        self.pos_hint={'center_x':0.5, 'center_y':0.65}
        self.size=("400dp","400dp")
        img = './icons/player_back.png' if img == './icons/track.png' else img
        with self.canvas:
            Color((1,1,1,1), mode='rgba')
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)], source = img)
        
class ContentNavigationDrawer(MDRelativeLayout):
    pass

class DrawerList(ThemableBehavior, MDList):
    pass

class CaptchaPopup(Popup):
    pass

class SecureCodePopup(Popup):
    pass

class CreateAlbumPopup(Popup):
    pass

class ConfirmationPopup(Popup):
    pass

class RenameAlbumPopup(Popup):
    pass

class AddToAlbumPopup(Popup):
    pass

class RenameTrackPopup(Popup):
    pass

class AudioInfo(MDBoxLayout):
    anim_to_hint = NumericProperty(0.05)

    status = OptionProperty('closed',options=("open", "closed"))
    
    ''' The animation kwargs used to construct the animation '''
    anim_kwargs = DictProperty({'d': .5, 't': 'in_quad'})

    def __init__(self,**kwargs):
        super(AudioInfo,self).__init__(**kwargs)
        self.pos_hint= {'center_x':0.5}
        status = kwargs.get('status')
        
        if status == "closed" or not status:
            self.y = -self.height*3
            self.opacity = 0
            
        elif status == "open":
            self.y = self.height/3.5
            self.opacity = 1

    def hide(self):
        print(self.pos_hint)
        if self.status == "closed":
            return
        
        self.status = "closed"
        Animation(y = -self.height*3, opacity = 0,**self.anim_kwargs).start(self)

    def show(self):
        print(self.pos_hint)
        if self.status == "open":
            return

        self.status = "open"
        Animation(y = self.height/3.5, opacity = 1, **self.anim_kwargs).start(self)

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    pass
    
class NoAvailableTracks(OneLineAvatarIconListItem):
    def __init__(self):
        super(NoAvailableTracks, self).__init__()     
        self.add_widget(ImageLeftWidgetWithoutTouch(source="./icons/sadness.png"))
        self.text = 'No available tracks'
        
class LoadingTracks(OneLineAvatarIconListItem):
    def __init__(self):
        super(LoadingTracks, self).__init__()     
        self.add_widget(ImageLeftWidgetWithoutTouch(source="./icons/load.gif"))
        self.text = 'Loading...'
        
class EndOfTheList(Widget):
    def __init__(self):
        super(EndOfTheList, self).__init__()     
        self.size_hint_y = None
        self.height = "150dp"
        
class Track(TwoLineAvatarIconListItem):
    def __init__(self, app, track):
        super(Track, self).__init__()
        self.add_widget(IconRightWidget(
            icon="./icons/more.png",
            on_release=lambda x: self.track_edit_menu())
        )

        self.app = app
        self.track = track
        self.key=track[0]
        self.path=track[1]
        self.text = track[2]
        self.secondary_text = track[3]
        self.img = track[4]
        self.album_key = app.album_screen.album[0] if app.manager.current=='album' else None
        self.isplaying = False
        
        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.img))
        self.on_release = self.play
        
    ### TRACK METHODS ###
    def play(self):
        self.app.player.start_playback(self)

    def highlighte(self):
        print(f"Track: {self.text} - {self.secondary_text} highlighted")
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhighlighte(self):
        print(f"Track: {self.text} - {self.secondary_text} unhighlighted")
        self.bg_color = [0,0,0,0]
        self.isplaying = False
        
    def track_edit_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": "Add to album","on_release":
             lambda : self.add_to_album()
             },
            {"viewclass": "OneLineListItem","text": "Rename","on_release":
             lambda : self.rename_track()
             },
            {"viewclass": "OneLineListItem","text": "Delete","on_release":
             lambda : self.delete_track()
             },
        ]
##        self.drop_down_menu = MDDropdownMenu(
##            caller=self, items=menu_items,position="center",width_mult=3, max_height=150
##        )
        self.drop_down_menu = MDDropdownMenu(
            caller=self, items=menu_items,position="center",width_mult=3
        )
        self.drop_down_menu.open()
        
    def add_to_album(self):
        self.drop_down_menu.dismiss()
        self.popup = AddToAlbumPopup()

        self.popup.ids.container.clear_widgets()
        album_list = self.app.meta.album_list() # DB class method
        for album in album_list:
            self.popup.ids.container.add_widget(
                AlbumListItem( self.app, album, self.track, self.popup)
            )
        self.popup.open()
        
    def rename_track(self, new_artist=None, new_song=None):
        if new_artist and new_song:
            self.app.meta.edit_track(self.key, new_artist, new_song) # DB class method
            self.secodary_text = new_song
            self.text = new_artist
            return self.popup.dismiss()
        
        elif isinstance(new_artist,str):
            return
            
        self.drop_down_menu.dismiss()
        self.popup = RenameTrackPopup()
        func = lambda *args: self.rename_track(
            new_artist=self.popup.ids.author.text,
            new_song=self.popup.ids.song.text
        )
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.song.text = self.secondary_text
        self.popup.ids.author.text = self.text
        self.popup.ids.action.bind(on_release=func)
        self.popup.open()
        
    def delete_track(self, state=None):
        if state == "Confirm":
            self.app.meta.delete_track(self.key, key_album=self.album_key) # DB class method
            self.parent.remove_widget(self)    
            return self.popup.dismiss()
                    
        elif state == "Cancel":
            return self.popup.dismiss()

        self.drop_down_menu.dismiss()

        self.popup = ConfirmationPopup()

        self.popup.ids.info.text = 'Are you sure want to delete track'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_track(state = "Confirm"))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.ids.cancel.bind(on_release=lambda *args:self.delete_track(state = "Cancel"))
        self.popup.open()

class AlbumListItem(OneLineAvatarIconListItem):
    def __init__(self, app, album, track, popup=None):
        super(AlbumListItem, self).__init__()
        self.app = app
        self.popup = popup
        self.album = album
        self.track = track
        self.text = self.album[1]
        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.album[2]))
        
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.app.meta.add_to_album(self.track[0], self.album[0]) # [DB class method]
            return self.popup.dismiss()
            
        
class SelectionBottomMenu(MDBoxLayout):
    def __init__(self, app, screen, album=None):
        super(SelectionBottomMenu, self).__init__()
        self.app = app
        self.app.player.stop()
        self.screen = screen
        self.album = album
        # remove tools list
        if 'outer_tools_container' in self.screen.ids:
            self.tools_container = self.screen.ids.outer_tools_container
            self.screen.ids.box.remove_widget(self.screen.ids.outer_tools_container)
        # disable menu
        if 'nav_drawer' in self.screen.ids:
            self.screen.ids.nav_drawer.enable_swiping=False
        
        self.app.audio_listing_key = 'selection'
        if self.album:
            self.screen.open_album(self.album, session = 1)

        else:
            self.screen.audios_listing(session = 1)

    def delete_selected(self, state=None):
        if state == "Confirm":
            children = [*self.screen.ids.container.children]
            for child in children:
                if isinstance(child, TrackWithCheckBox):
                    child.delete_track()
                
            self.popup.dismiss()
            return self.close_selection()
                    
        elif state == "Cancel":
            return self.popup.dismiss()
        
        self.popup = ConfirmationPopup()

        self.popup.ids.info.text = 'Are you sure want to delete selected tracks'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_selected(state = "Confirm"))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.ids.cancel.bind(on_release=lambda *args:self.delete_selected(state = "Cancel"))
        self.popup.open()

        
    def create_album(self, album_name=None):
        if album_name:
            album_key = self.app.meta.add_album(album_name, img=None) # [DB class method]
            children = [*self.screen.ids.container.children]
            for child in children:
                if isinstance(child, TrackWithCheckBox):
                    child.add_to_album(album_key=album_key)

            self.popup.dismiss()          
            return self.close_selection()
        
        elif isinstance(album_name,str):
            return
            
        self.popup = CreateAlbumPopup()
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(
            on_release=lambda *args:self.create_album(album_name=self.popup.ids.album_name.text)
        )
        self.popup.open()
        
    def close_selection(self):
        self.screen.remove_widget(self)
        self.app.audio_listing_key = 'user'
        if self.screen.name == 'start':
            self.screen.ids.box.add_widget(self.tools_container,1)
            self.screen.ids.nav_drawer.enable_swiping=True
            self.screen.audios_listing()
            
        else:
            self.screen.open_album(self.album)
            
    ### SELECTION MENU METHODS ###

class SessionListElement(TwoLineAvatarIconListItem):
    def __init__(self, app, session_name):
        super(SessionListElement, self).__init__()
        self.app = app
        self.bg_color = (1,0.8,0.8,1)
        self.add_widget(IconRightWidget(
            icon="./icons/more.png",
            on_release=lambda x: self.mange_session())
        )

        if 'vk_' in session_name:
            self.session = VK_session(self,session_name)
            
        self.text = self.session.u_name
        self.secondary_text ='Connecting...'
        

        self.load_title = CircularProgressBar(
                thickness = '3dp',
                widget_size="46dp",
                progress_clr = self.app.main_clr,
                hint_clr = self.app.main_clr2,
                label_clr = (0,0,0,0),
                body_clr = (0.56, 0.56, 0.56, 1))
        self.title = ImageLeftWidgetWithoutTouch()
        self.problem_title = ImageLeftWidgetWithoutTouch(source="./icons/problem.png")

        self.ids._left_container.add_widget(self.load_title)
            
        self.size_hint_y=None
    
    def mange_session(self):
        menu_items = [
            {"viewclass": "OneLineListItem","text": "Delete session",
             "on_release":lambda : self.delete_session()},
        ]
        self.drop_down_menu = MDDropdownMenu(
            caller=self, items=menu_items,position="center",width_mult=3, max_height=100
        )
        self.drop_down_menu.open()

    def open_session(self):
        #self.app.player.stop()
        self.app.audio_listing_key = 'vk'
        self.app.main_screen.ids.nav_drawer.set_state('toggle')        
        self.app.main_screen.audios_listing(session = self.session)
        
    def session_unavalible(self):
        if isinstance(self.session,VK_session):
            self.session = VK_session(self,session_name)
            
        self.secondary_text ='Connecting...'
        self.session_obj.ids._left_container.clear_widgets()
        self.ids._left_container.add_widget(self.load_title)
        
    def delete_session(self):
        pass

class TrackWithCheckBox(TwoLineAvatarIconListItem):
    def __init__(self, app, track):
        super(TrackWithCheckBox, self).__init__()
        self.check_box = RightCheckbox(size_hint = (1,None),pos_hint = {'center_y':0.5})
        self.add_widget(self.check_box)
        self.on_release=lambda : self.select(self.check_box)

        self.app = app
        self.album_key = app.album_screen.album[0] if app.manager.current=='album' else None
        self.track = track
        self.key=track[0]
        self.path=track[1]
        self.text = track[2]
        self.secondary_text = track[3]
        self.img = track[4]

        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.img))
        
    def select(self, obj):
        obj.active=not obj.active

    def delete_track(self):
        if self.check_box.active:
            self.app.meta.delete_track(self.key, key_album=self.album_key) # [DB class method]
             
    def add_to_album(self, album_key=None):
         if album_key and self.check_box.active:
            self.app.meta.add_to_album(self.key, album_key) # [DB class method]      


class VKTrack(TwoLineAvatarIconListItem):
    def __init__(self, session, app, track):
        super(VKTrack, self).__init__()
        self.img = track[4] or "./icons/track.png"
        self.text = track[2] or 'artist'
        self.secondary_text = track[3] or 'song'
        self.id = track[1]
        self.app = app
        self.session = session
        self.track = track
        self.on_release = self.play
        self.album_key = app.album_screen.album[0] if app.manager.current=='album' else None
        self.isplaying = False
        
        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.img))
        self.add_widget(IconRightWidget(
            icon="./icons/load.png",
            on_release=lambda x: self.download())
        )
        self.is_downloaded = False
        self.progress = None
        

    def play(self):
        self.app.player.start_playback(self)

    def highlighte(self):
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhighlighte(self):
        self.bg_color = [0,0,0,0]
        self.isplaying = False
        
    def download(self):
        self.children[0].remove_widget(self.children[0].children[0])

        self.progress = CircularProgressBar(
                thickness = '3dp',
                widget_size="46dp",
                progress_clr = self.app.main_clr,
                hint_clr = self.app.main_clr2,
                label = CoreLabel(text="{}%", font_size=sp(14)),
                label_clr = (0,0,0,1),
                body_clr = (0.56, 0.56, 0.56, 1))
        self.ids._right_container.add_widget(self.progress)
        
        key = self.app.meta.new_track(self.text, self.secondary_text) # DB class method
        task = {key:self}
        #task = [(self.text,self.secondary_text,key,self.img,self.session, self.id,self.app,self)]
        asyncio.get_event_loop().create_task(self.app.downloader.download(task,'vk'))


class TopAppBarMenuElem(MDRelativeLayout):
    def  __init__(self,app, img, pos, func=None):
        super(TopAppBarMenuElem, self).__init__()
        self.pos_hint = {'center_x':pos[0], 'center_y':pos[1]}
        self.size_hint = (None,None)
        self.size = ("40dp","40dp")
        self.md_bg_color= app.btn_hitbox_clr
        btn = Button(background_color=[0,0,0,0],
                     pos_hint = {'center_x':.5, 'center_y':.5},
                     size = ("60dp","60dp"),
                     size_hint = (None,None),
                     on_release = func)
        self.add_widget(btn)
        icon = Image(pos_hint = {'center_x':.5, 'center_y':.5},
                     size = ("40dp","40dp"),
                     size_hint = (None,None),
                     source = img)
        self.add_widget(icon)

class SideMenu(MDNavigationDrawer):
    # FIX on opening clicking children
    pass

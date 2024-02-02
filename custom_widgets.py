from kivy.uix.gridlayout import GridLayout
from kivymd.uix.behaviors import TouchBehavior
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivymd.uix.list import (OneLineAvatarIconListItem,
                             IconRightWidget,
                             ImageLeftWidgetWithoutTouch,
                             TwoLineAvatarIconListItem)

from kivymd.uix.relativelayout import MDRelativeLayout
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
from kivy.graphics.vertex_instructions import RoundedRectangle, Line, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import Label as CoreLabel
from kivy.metrics import sp, dp
import os
from vk_methods import VK_session
import shutil
import pickle
from kivy.clock import Clock
from utils import *
import shutil
import re
from math import exp
import asyncio

from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty,ColorProperty,ObjectProperty)

from drop_down_resent import DropDownResent
from ticker import Ticker
from draggablescreenlayout import DraggableScreenLayout
from animations import LoadSign, CircularProgressBar, LoadingBar
from album import AlbumButton
#from sidemenu import SideMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.properties import ListProperty, OptionProperty, DictProperty, NumericProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.effects.dampedscroll import DampedScrollEffect
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

class PlayerBack(Widget):
    def __init__(self, img):
        super(PlayerBack, self).__init__()
        self.fbind('pos',self._draw,'size',self._draw)
        self.img = AsyncImage(
            size_hint=(None,None),
            fit_mode = 'fill',
            size=("320dp","320dp"),
            source = './icons/player_back.png' if (img == './icons/player_back.png' or not img) else img
        )
        self.size_hint=(None,None)
        self.pos_hint={'center_x':0.5, 'center_y':0.65}
        self.size=("320dp","320dp")
        
    def _draw(self,*args):
        with self.canvas:
            self.canvas.clear()
            Color((0,0,0,0.2), mode='rgba')
            RoundedRectangle(texture = self.img.texture, pos=self.pos, size=self.size, radius=[dp(20)])
            
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
        # remove header
        self.screen.ids.container._selection_start()
        # disable menu
        if 'nav_drawer' in self.screen.ids:
            self.screen.ids.nav_drawer.enable_swiping=False
        
        self.app.audio_listing_key = 'selection'
        if self.album:
            self.screen.open_album(self.album, session = 1)

        else:
            self.screen.audios_listing(session = 1)

    def delete_selected(self, state=None):
        if state:
            children = [*self.screen.ids.container.children[0].children[0].children]
            for child in children:
                if isinstance(child, TrackWithCheckBox):
                    child.delete_track()
                
            self.popup.dismiss()
            return self.close_selection()
        
        self.popup = ConfirmationPopup()

        self.popup.ids.info.text = 'Are you sure want to delete selected tracks'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_selected(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
        
    def create_album(self, album_name=None):
        if album_name:
            album_key = self.app.meta.add_album(album_name, img=None) # [DB class method]
            children = [*self.screen.ids.container.children[0].children[0].children]
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
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
        
    def close_selection(self):
        self.screen.remove_widget(self)
        self.app.audio_listing_key = 'user'
        self.app.manager.current_screen.ids.container._selection_end()
        if self.screen.name == 'start':
            self.screen.ids.nav_drawer.enable_swiping=True
            self.screen.audios_listing()
            
        else:
            self.screen.open_album(self.album)
            
    ### SELECTION MENU METHODS ###

class SessionListElement(TwoLineAvatarIconListItem):
    def __init__(self, app, session_name):
        super(SessionListElement, self).__init__()
        self.is_session = True
        self.app = app
        self.bg_color = (1,0.8,0.8,1)
        self.add_widget(IconRightWidget(
            icon="./icons/more.png",
            on_release=lambda x: self.mange_session())
        )

        if 'vk_' in session_name:
            self.session = VK_session(self,session_name)
        elif 'ya_' in session_name:
            pass
        else:
            self.is_session = False
            return
            
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
        
    def delete_session(self,state=None):
        if state:
            shutil.rmtree(self.session.path)
            self.parent.remove_widget(self)    
            return self.popup.dismiss()

        self.drop_down_menu.dismiss()
        self.popup = ConfirmationPopup()
        self.popup.ids.info.text = 'Are you sure want to delete session'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_session(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()


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
    
class ToolBase(ButtonBehavior):

    offset =NumericProperty("10dp")
    
    bg_color = ColorProperty(None)

    title = StringProperty()

    action = ObjectProperty()

    text = StringProperty()
    
    def __init__(self, overlapping_obj, **kwargs):
        super(ToolBase, self).__init__()
        self.overlapping_obj = overlapping_obj
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        self.fbind('bg_color',self._draw)
        
        self.title = kwargs['title']
        self.text = kwargs['text']
        self.action = kwargs['action']
        self.bg_color = kwargs['bg_color']
        
        
        self.size_hint_y = None
        self.height = "65dp"

    def _draw(self,*args):
        color = self.bg_color if self.bg_color else (0,0,0,0)
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*color, mode='rgba')
            Rectangle(pos=self.pos, size=self.size)

    def on_touch_down(self, touch):
        self._touch = touch
        return super(ToolBase, self).on_touch_down(touch)
    
    def _do(self):
        if self.action and not self.overlapping_obj.collide_point(*self._touch.pos):
            self.action()

class Tool(ToolBase, FloatLayout):
    pass
            
class TrackImage(Widget):
    
    source = StringProperty()

    def __init__(self,**kwargs):
        super(TrackImage, self).__init__(**kwargs)
        self.image = None
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        
    def on_source(self,instance,source=None):
        self.image = AsyncImage(
            size_hint=(None,None),
            fit_mode = 'fill',
            size=("50dp","50dp"),
            source = source
        )
        self.image.fbind('texture',self._draw)
        self._draw()

    def _draw(self,*args):
        if not self.image:
            return
        
        with self.canvas.after:
            self.canvas.after.clear()
            Color(1,1,1,1, mode='rgba')
            RoundedRectangle(texture= self.image.texture,pos=self.pos, size=self.size, radius=[dp(5)])
  
class TrackBase(ButtonBehavior):
    
    offset =NumericProperty("10dp")
    
    artist = StringProperty()
    
    song = StringProperty()
    
    title = StringProperty()
    
    bg_color = ColorProperty(None)

    isplaying = BooleanProperty(False)
    
    def __init__(self, session, app, track = (None, '', 'Artist', 'Song', './icons/player_back.png',)):
        super(TrackBase, self).__init__()
        self.session = session
        self.app = app
        self.track = track
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        self.fbind('bg_color',self._draw)
        
        self.title = track[4] or './icons/player_back.png'
        self.artist = track[2] or 'Artist'
        self.song = track[3] or 'Song'
        try:
            self.album_key = app.album_screen.album[0] if app.manager.current=='album' else None
        except:
            pass

        self.size_hint_y = None
        self.height = "72dp"
        
    def play(self):
        self.app.player.start_playback(self)

    def highlighte(self):
        print(f"Track: {self.artist} - {self.song} highlighted")
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhighlighte(self):
        print(f"Track: {self.artist} - {self.song} unhighlighted")
        self.bg_color = [0,0,0,0]
        self.isplaying = False

    def _draw(self,*args):
        color = self.bg_color if self.bg_color else (0,0,0,0)
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*color, mode='rgba')
            Rectangle(pos=self.pos, size=self.size)

    def select(self, check_box):
        check_box.active=not check_box.active

    def delete_track(self):
        if self.ids.action.active:
            self.app.meta.delete_track(self.track[0], key_album=self.album_key) # [DB class method]
             
    def add_to_album(self, album_key=None):
        print(213)
        if album_key and self.ids.action.active:
            self.app.meta.add_to_album(self.track[0], album_key) # [DB class method]
        
class ActionBase(ButtonBehavior):

    action_texture = ObjectProperty()

    active = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(ActionBase, self).__init__(**kwargs)
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        self.fbind('action_texture',self._draw)
        
    def open_edit_menu(self):
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
        self.drop_down_menu = MDDropdownMenu(
            caller=self, items=menu_items,position="center",width_mult=3
        )
        self.drop_down_menu.open()

    def download(self):
        if not self.active:
            return
        
        self.canvas.after.clear()
        self.active = False

        self.parent.progress = CircularProgressBar(
                pos= (self.parent.x + self.parent.width - self.parent.height,self.parent.y + self.parent.offset),
                thickness = '3dp',
                widget_size="46dp",
                progress_clr = self.parent.app.main_clr,
                hint_clr = self.parent.app.main_clr2,
                label = CoreLabel(text="{}%", font_size=sp(14)),
                label_clr = (0,0,0,1),
                body_clr = (0.56, 0.56, 0.56, 1))
        self.parent.add_widget(self.parent.progress)
        
        key = self.parent.app.meta.new_track(self.parent.artist, self.parent.song) # DB class method
        task = {key:self.parent}
        asyncio.get_event_loop().create_task(self.parent.app.downloader.download(task,'vk'))

    def download_end(self):
        self.action_texture = Image(
            size_hint=(None,None),
            size=("50dp","50dp"),
            source = "./icons/done.png"
        ).texture

    def _draw(self,*args):
        with self.canvas.after:
            self.canvas.after.clear()
            Color(*(1,1,1,1), mode='rgba')
            Rectangle(
                texture = self.action_texture,
                pos=(self.x+self.width/4, self.y+self.height/4),
                size=(self.width/2, self.height/2))
        
class TrackAtion(ActionBase,Widget):
    def __init__(self, **kwargs):
        super(TrackAtion, self).__init__(**kwargs)
        self.action_texture = Image(
            size_hint=(None,None),
            size=("25dp","25dp"),
            source = "./icons/more.png"
        ).texture
        
    def add_to_album(self):
        self.drop_down_menu.dismiss()
        self.popup = AddToAlbumPopup()

        self.popup.ids.container.clear_widgets()
        album_list = self.parent.app.meta.album_list() # DB class method
        for album in album_list:
            self.popup.ids.container.add_widget(
                AlbumListItem( self.parent.app, album, self.parent.track, self.popup)
            )
        self.popup.open()
        
    def rename_track(self, new_artist=None, new_song=None):
        if new_artist and new_song:
            self.parent.app.meta.edit_track(self.parent.track[0], new_artist, new_song) # DB class method
            self.parent.song = new_song
            self.parent.artist = new_artist
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
        self.popup.ids.song.text = self.parent.song
        self.popup.ids.author.text = self.parent.artist
        self.popup.ids.action.bind(on_release=func)
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
        
    def delete_track(self, state=None):
        if state:
            self.parent.app.meta.delete_track(self.parent.track[0], key_album=self.parent.album_key) # DB class method
            self.parent.parent.remove_widget(self.parent)    
            return self.popup.dismiss()

        self.drop_down_menu.dismiss()

        self.popup = ConfirmationPopup()

        self.popup.ids.info.text = 'Are you sure want to delete track'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_track(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open() 
        
class Track(TrackBase, FloatLayout):
    pass
    
class VKTrackAtion(ActionBase,Widget):
    def __init__(self, **kwargs):
        super(VKTrackAtion, self).__init__(**kwargs)
        self.action_texture = Image(
            size_hint=(None,None),
            size=("25dp","25dp"),
            source = "./icons/load.png"
        ).texture
        
class VKTrack(TrackBase, FloatLayout):
    
    progress = ObjectProperty()


class TrackWithCheckBox(TrackBase, FloatLayout):
    pass

class NoAvailableTracks(FloatLayout):
    pass

class EndOfTheList(Widget):
    def __init__(self):
        super(EndOfTheList, self).__init__()     
        self.size_hint_y = None
        self.height = "150dp"

class HighPerformanceContainer(GridLayout):
    ''' HighPerformanceContainer class is a children class of UpdatableScrollView class it's always keep
     viewable only same amount of chunks represented in chunks_to_view property. Chunks is small
     pieces of listing data. When ever scroll goes out of bound new data dynamically generates and adds
     to scrollview chunk by chunk.

     HighPerformanceContainer class stored data represented by 3 properties:
     1. child_class: is class of children which istances will be added to scrollview;
     2. child_args: list property of default children init arguments;
     3. child_kwargs: list property which contains dictionaries of unique children init arguments.
     '''
    
    chunk_size = NumericProperty(10)

    chunks_to_view = NumericProperty(10)

    child_class = ObjectProperty(Track)

    child_args = ListProperty()

    child_kwargs = ListProperty()

    album_id = StringProperty(allownone=True)

    app = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(HighPerformanceContainer, self).__init__(**kwargs)
        self.load_more_loop = asyncio.get_event_loop()
        self._loading = False
        self._has_more = False
        
        self._index = 0
        self._child_quantity = 0
        self._child_height = 0

        self.dummy = None
        self.__exchange = 1

    def add_track(self,i, index = 0):
        track_obj = self.child_class(*self.child_args, **self.child_kwargs[i])
                    
        # Now playing UI update
        if self.app.player.get_current_track() == self.child_kwargs[i]['track'][1]:
            track_obj.highlighte()
            self.app.player._highlighted.append(track_obj)
            
        self.add_widget(track_obj, index = index)

    def add_album(self,i,index= 0):
        album_obj = self.child_class(*self.child_args, **self.child_kwargs[i])
        self.add_widget(album_obj,index = index)

    async def append(self):
        if self.child_class is VKTrack:

            track_list = await self.child_args[0].load_user_audios(album_id=self.album_id)
            
            if album_list[-1] == 'EOL':
                self._has_more = False
                
            for track in track_list:
                self.child_kwargs.append(track)
                
        if self.child_class is AlbumButton and self.child_args[0]:
            album_list = await self.child_args[0].load_playlists()
            
            if album_list[-1] == 'EOL':
                self._has_more = False
                
            for album in album_list:
                self.child_kwargs.append(album)

        self._loading = False
        
    def _listing(self):
        self._child_quantity = self.chunk_size*self.chunks_to_view if len(self.child_kwargs) > self.chunk_size*self.chunks_to_view else len(self.child_kwargs)
        self.clear_widgets()
        self._index = 0

        # check if list loaded fully
        if ('track' in self.child_kwargs[-1] and self.child_kwargs[-1]['track'] != 'EOL') or \
        ('album' in self.child_kwargs[-1] and self.child_kwargs[-1]['album'] != 'EOL'):
            print('Has more to load')
            self._has_more = True
        
        # empty list
        if self._child_quantity == 0:
            print('List is empty')
            self._empty_listing()

        # is album listing
        if self.child_class is AlbumButton:
            self.cols = 2
            self.padding = self.width*(1-2/2.5)/3
            self.spacing = self.width*(1-2/2.5)/3

        # is track listing
        else:
            self.cols = 1
            self.padding = 0
            self.spacing = 0
        
        for i in range(self._child_quantity):
            # skip tracks tif them still loading
            if 'track' in self.child_kwargs[i] and 'temp' in self.child_kwargs[i]['track']:
                continue
                
            # end of track list
            elif 'track' in self.child_kwargs[i] and self.child_kwargs[i]['track'] == 'EOL':
                print('End of the list appear')
                self.add_widget(EndOfTheList())
                
            # end of album list
            elif 'album' in self.child_kwargs[i] and self.child_kwargs[i]['album'] == 'EOL':
                print('End of the list appear')
                self.add_widget(EndOfTheList())
                self.add_widget(EndOfTheList())

            # list till 'EOL' doesn't appear
            else:
                if 'album' in self.child_kwargs[i]:
                    self.add_album(i)
                else:
                    self.add_track(i)

        self._child_height = self.children[-1].height

    def _empty_listing(self):
        if 'track' in self.child_kwargs[i]:
            self.add_widget(NoAvailableTracks())
        else:
            pass
            
    def load_down(self,*args):
        # lock header pos
        if self.dummy:
            self.remove_widget(self.dummy)
            
        if self._index + self._child_quantity < len(self.child_kwargs):

            # load more
            if not self._loading and self._has_more and \
            self._index + self._child_quantity > len(self.child_kwargs)/2:
                self._loading = True
                self.load_more_loop.create_task(self.exec_async(self.parent.overscroll_callback))
                
            to_list = self.chunk_size \
            if len(self.child_kwargs) - self._index - self._child_quantity >= self.chunk_size \
            else len(self.child_kwargs) - self._index - self._child_quantity
            
            # add new chunk and delete upper chunk
            for i in range(to_list):
                j = self._index+self._child_quantity
                # skip tracks tif them still loading
                if 'track' in self.child_kwargs[j] and 'temp' in self.child_kwargs[j]['track']:
                    continue
                
                # end of track list
                elif 'track' in self.child_kwargs[j] and self.child_kwargs[j]['track'] == 'EOL':
                    self.add_widget(EndOfTheList())
                
                # end of album list
                elif 'album' in self.child_kwargs[j] and self.child_kwargs[j]['album'] == 'EOL':
                    self.add_widget(EndOfTheList())
                    self.add_widget(EndOfTheList())

                # list till 'EOL' doesn't appear
                else:
                    if 'album' in self.child_kwargs[j]:
                        self.add_album(j)
                    else:
                        self.add_track(j)
                    
                self._index += 1
                self.remove_widget(self.children[-1])

            # rescroll
            self.parent.scroll_y = to_list*self._child_height/self.parent.viewport_size[1]
            
            # create and add dummy either dynamic load of elements works awful !!!
            # [ idk probable scrollview critical value appears ]
            self.dummy = Widget(size_hint_y = None, height = self.__exchange)
            self.__exchange *= -1
            self.add_widget(self.dummy)         
  
    def load_up(self,*args):       
        if self.dummy:
            self.remove_widget(self.dummy)
            
        if self._index > 0:
            to_list = self.chunk_size if self._index >= self.chunk_size else self._index
            # add new chunk and delete upper chunk
            for i in range(to_list):
                self._index -= 1
                self.remove_widget(self.children[0])
                
                # skip tracks tif them still loading
                if 'track' in self.child_kwargs[self._index] and \
                'temp' in self.child_kwargs[self._index]['track']:
                    continue
                
                # end of track list
                elif 'track' in self.child_kwargs[self._index] and \
                self.child_kwargs[self._index]['track'] == 'EOL':
                    pass
                
                # end of album list
                elif 'album' in self.child_kwargs[self._index] and \
                self.child_kwargs[self._index]['album'] == 'EOL':
                    pass
                
                else:
                    if 'album' in self.child_kwargs[self._index]:
                        self.add_album(self._index, index = len(self.children))
                    else:
                        self.add_track(self._index, index = len(self.children))

            # rescroll
            self.parent.scroll_y = 1 - self.chunk_size*self._child_height/self.parent.viewport_size[1]
            
            # create and add dummy either dynamic load of elements works awful
            # [ idk probable scrollview critical value appears ]
            self.dummy = Widget(size_hint_y = None, height = self.__exchange)
            self.__exchange *= -1
            self.add_widget(self.dummy)
            

class OverscrollUpdateEffect(DampedScrollEffect):
    def on_overscroll(self, instance_refresh_scroll_effect, overscroll):
        # load of listing widgets or if no callback specified
        if not self.target_widget.parent.overscroll_callback or \
        not self.target_widget.parent._is_human or \
        self.target_widget.parent.parent._hold:# or self.scroll_view.children[0].:
            return True
        
        if 'scroll_view' not in dir(self):
            self.scroll_view = self.target_widget.parent

        if overscroll<0 and not self.scroll_view._is_loading and self.scroll_view.children[0]._index == 0: # upper overscroll
            if not self.scroll_view._did_overscroll:
                self.scroll_view.move_load_sign(overscroll)
                
            if overscroll < self.min__overscroll:
                self.scroll_view._did_overscroll = True
                return True
            
            else:
                self.scroll_view._did_overscroll = False
                return True

class UpdatableScrollView(ScrollView):
    
    ''' Top minimum overscroll value to execute callback if any '''
    min__overscroll = NumericProperty("-100dp")

    ''' For proper work you should not edit this property '''
    do_scroll_x = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.task_loop = asyncio.get_event_loop()
        super(UpdatableScrollView, self).__init__(**kwargs)
        self.effect_cls= OverscrollUpdateEffect
        self.effect_cls.min__overscroll = self.min__overscroll
        self._is_loading = False
        self._did_overscroll = False
        # prevent screen load bug
        self._is_human = False
        # on load dummy widget
        self.w = Widget(size_hint_y = None, height = abs(float(self.min__overscroll)))
        self.ww = Widget(size_hint_y = None, height = abs(float(self.min__overscroll)))

    def on_scroll_y(self, *args):
        ''' Dynamically load scrollview content '''

        if self.scroll_y < 0:
            self.container.load_down()
           
        elif self.scroll_y > 1:
            self.container.load_up()

        else:
            self.parent._move_header(*args)

    def on_touch_down(self, *args):
        ''' Creates task if any callback specified '''

        if not self._did_overscroll:
            self._is_human = True
        return super().on_touch_down(*args)
    
    def on_touch_up(self, *args):
        ''' Creates task if any callback specified '''
            
        if self._did_overscroll and not self._is_loading and self._is_human:
            if self.overscroll_callback:
                if self.container.child_class is AlbumButton:
                    self.container.add_widget(self.w, index = len(self.container.children))
                    self.container.add_widget(self.ww, index = len(self.container.children))
                else:
                    self.container.add_widget(self.w, index = len(self.container.children))
                    
                self.task_loop.create_task(self.exec_async(self.parent.overscroll_callback))
                self._is_loading = True
                
            self._did_overscroll = False
            #return True [Blocks touch events]
        return super().on_touch_up(*args)
    
    async def exec_async(self, callback_with_parm):
        ''' Asynchronous callback execution goes here '''

        self.load_sign.start_anim()
        args = (self,) + callback_with_parm[1]
        kwargs = callback_with_parm[2]
        callback = callback_with_parm[0]
        await callback(*args, **kwargs)

        self._is_loading = False
        
        if self.container.child_class is AlbumButton:
            self.container.remove_widget(self.w)
            self.container.remove_widget(self.ww)
            
        else:
            self.container.remove_widget(self.w)
            
        self.move_load_sign(0)
        self.load_sign.stop_anim()
        self._is_human = False

    def move_load_sign(self, dy):
        # fading effect
        self.load_sign.opacity = exp(8*(abs(dy/self.min__overscroll) - 1))
        # move towards visible container field
        self.load_sign.y = self.load_sign.parent.y-self.min__overscroll+dy \
        if abs(dy)<=abs(self.min__overscroll) else self.load_sign.parent.y

class UpdatableListingContainer(FloatLayout):

    size_of_view = NumericProperty()

    header = ObjectProperty()
    
    container = ObjectProperty()
    
    load_sign = ObjectProperty()
    
    scroll_view = ObjectProperty()
    
    overscroll_callback = ListProperty()
    
    def __init__(self, **kwargs):
        self.task_loop = asyncio.get_event_loop()
        super(UpdatableListingContainer, self).__init__(**kwargs)
        self._switch = True
        self._hold = False
        
        self._header_max = 0
        self._header_min = 0
            
        self._scrollview_max = 0
        self._scrollview_min = 0
        
        self._prev_scroll_y = 0
        
        self.listing = []
        self.fbind('container',self._set_children_attrs)
        self.fbind('load_sign',self._set_children_attrs)
        self.fbind('scroll_view',self._set_children_attrs)
        self.fbind('overscroll_callback',self._set_children_attrs)

    def _move_header(self, scrollview_instance, scroll_y):
        # header should be static if the size of listing is lower than scrollview it self
        if scrollview_instance.height > scrollview_instance.viewport_size[1] or self._hold:
            return

        if self.header and self._prev_scroll_y and (bool(self._switch) == bool(self._prev_scroll_y - scroll_y > 0)):
            delta = (self._prev_scroll_y - scroll_y)*scrollview_instance.viewport_size[1]

            if (self.y + delta > self._scrollview_max or self.header.y + delta > self._header_max):
                self.header.y = self._header_max
                
            elif (self.y + delta < self._scrollview_min or self.header.y + delta < self._header_min):
                self.header.y = self._header_min
                
            else:
                self.y += delta/4
                self.header.y += delta/4

        elif self.header and not (self._header_max or self._header_min):
            # set movement limits
            self._header_max = self.header.top + dp(2)
            self._header_min = self.header.y
            
            self._scrollview_max = scrollview_instance.y + self.header.height
            self._scrollview_min = scrollview_instance.y

        # determice where does the scroll go
        self._switch = True if self._prev_scroll_y - scroll_y > 0 else False
        self._prev_scroll_y = scroll_y
        

    def _selection_start(self):
        print(312312)
        self._move_header(self.scroll_view,1)
        self._move_header(self.scroll_view,0)
        self._hold = True
        self.header.y = self._header_max
        self.y = self._scrollview_max
        
    def _selection_end(self):
        self.header.y = self._header_min
        self.y = self._scrollview_min
        self._hold = False
        
    
    def _set_children_attrs(self,*args):
        if self.container and self.load_sign and self.scroll_view:
            self.scroll_view.container = self.ids.container
            self.scroll_view.load_sign = self.ids.load_sign
            self.scroll_view.overscroll_callback = self.overscroll_callback or []

    def set_listing(self, child_class = None, child_args = None, child_kwargs = None, album_id = None):
        try:
            self.listing = child_kwargs
            self.container.album_id = str(album_id)
            
            if child_class:
                self.container.child_class = child_class
                
            if child_args:
                self.container.child_args = child_args
                
            if child_kwargs and child_class is AlbumButton:
                kwargs = []
                for album in child_kwargs:
                    kwargs.append({'album':album})
                self.container.child_kwargs = kwargs
                
            elif child_kwargs and child_class is not AlbumButton:
                kwargs = []
                for track in child_kwargs:
                    kwargs.append({'track':track})
                self.container.child_kwargs = kwargs

            if self.container.child_class and self.container.child_args and self.container.child_kwargs:
                print('Do listing')
                self.container._listing()

        except Exception as e:
                print(e)

    def get_listing(self):
        return (self.container.child_class, self.container.child_args, self.listing, self.container.album_id)

    def append_listing(self,child_kwargs):
        for child in child_kwargs:
            self.container.child_kwargs.append(child)

    def clear(self):
        self.container.clear_widgets()

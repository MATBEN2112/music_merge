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
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDIconButton
import os
from vk_methods import VK_session
import shutil
import pickle
from kivy.clock import Clock
from utils import *
import csv
import re


from kivymd.uix.snackbar.snackbar import BaseSnackbar

class CustomSnackBar(BaseSnackbar):
    def __init__(self, message):
        super(CustomSnackBar, self).__init__()

        self.add_widget(MDLabel(
            text=message,
            theme_text_color="Custom",
            text_color="#393231",
        ))

        self.y="24dp"
        self.pos_hint={"center_x": 0.5, "center_y": 0.5}
        self.size_hint_x=0.5
        self.md_bg_color="#E8D8D7"
        self.open()

class PopupActionButton(MDRelativeLayout, TouchBehavior):
    def __init__(self, text, func, x):
        super(PopupActionButton, self).__init__()
        self.add_widget(MDLabel(text=text, font_size = "18sp", pos_hint={"center_x": .5, "center_y": 0.5}, halign="center"))
        self.pos_hint={"center_x": x, "center_y": 0.2}
        self.size_hint=(None,None)
        self.size = ("160dp","65dp")
        self.func = func

        with self.canvas.before:
            Color(1, 0, 0, .5, mode='rgba')
            RoundedRectangle(pos=self.pos, size=self.size, radius = [8])
            Color(1, 0.5, 0, .5, mode='rgba')
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8))
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.func()

            
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
        self.pos_hint={'center_x':0.5, 'center_y':0.65}
        self.size=("400dp","400dp")
        self.size_hint=(None,None)
        img = './icons/player_back.png' if img == './icons/track.png' else img
        with self.canvas.before:
            Color((1,1,1,1), mode='rgba')
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20], source = img)
        
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
    pass

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    pass

class SearchFieldLayout(MDBoxLayout):
    def __init__(self, screen):
        super(SearchFieldLayout, self).__init__()
        
        self.size_hint = (1,None)
        self.size = (screen.app.root.size[0],"100dp")
        self.padding = ["10dp","10dp","10dp","10dp"]
        self.spacing = "10dp"
        btn = TopAppBarMenuElem("./icons/back.png",[.5,.5],lambda x: screen.close_search())
        self.add_widget(btn)
        self.search_box = SearchBox(screen)
        self.add_widget(self.search_box)

            
    
class SearchBox(MDRelativeLayout):
    def __init__(self, screen):
        super(SearchBox, self).__init__()
        self.size = (screen.app.root.size[0]*0.85,"70dp")
        self.size_hint = (None,None)
        self.screen = screen
        self.global_mode = False

        self.search_field = SearchTextField(self, screen)
        self.add_widget(self.search_field)
        
        self.search = MDIconButton(
            icon= "./icons/search.png",
            pos_hint= {"center_x": .05,"center_y": .5},
            on_release = self.switch_mode
        )
        self.add_widget(self.search)
        
        self.clean = MDIconButton(
            icon= "./icons/x.png",
            pos_hint= {"center_x": .95,"center_y": .5},
            opacity = 0,
            on_release = self.search_field.clean)
        self.add_widget(self.clean)
        
        with self.canvas.before:
            self.back_color = Color((1,1,1,1),mode='rgba')
            self.back = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.outline_color = Color(1, 0, 0, 1, mode='rgba')
            self.outline = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10))

    def switch_mode(self,o):
        if not self.screen.session:
            return
        
        self.global_mode = not self.global_mode
        if self.global_mode:
            self.search.icon = "./icons/glob_search.png"
        else:
            self.search.icon = "./icons/search.png"


class SearchTextField(TextInput):
    def __init__(self, search_box, screen):
        super(SearchTextField, self).__init__()
        self.multiline = False
        self.search_box = search_box
        self.screen = screen
        self.font_size = '28sp'
        self.padding_y = [self.height / 7, 0] # [fix] make input text centerend by text and texture metrics 
        self.pos_hint = {"center_x": .5,"center_y": .5}
        self.size_hint = (None,None)
        self.cursor_color = (1,0,0,1)
        self.hint_text = 'Search audio'
        self.hint_text_color = (1,0,0,1)
        self.background_color = (0,0,0,0)
        self.size = (screen.app.root.size[0]*0.7,"60dp")
        
        # actions
        self.bind(focus=self.on_focus)
        self.bind(text=self.on_text)
        self.on_text_validate = self.search

        
    def on_focus(self,obj,value):
        ''' Dynamic change of text input appearance '''
        if value: # focused
            self.hint_text_color = (1,0,0,0)
            self.dropdown = DropDownResent(self.screen.ids.search_row, self)
            self.search_box.back_color.rgba = (.9, .9, .9, 1)
            self.search_box.outline.width = 2
            self.search_box.outline_color.rgba = (0, 0, 1, 1)

        else:
            self.hint_text_color = (1,0,0,1)
            if 'dropdown' in dir(self):
                self.dropdown.dismiss()
                
            self.search_box.back_color.rgba = (1, 1, 1, 1)
            self.search_box.outline.width = 1
            self.search_box.outline_color.rgba = (1, 0, 0, 1)    
        
    def on_text(self,obj,value):
        if 'dropdown' in dir(self):
            self.dropdown.dismiss()

        self.dropdown = DropDownResent(self.screen.ids.search_row,self)
        if self.text:
            self.search_box.children[0].opacity = 1
        else:
            self.search_box.children[0].opacity = 0
            
    def clean(self, x):
        self.text=''

    def search(self):
        # save search query to search history
        if self.text not in self.dropdown.resent:
            with open(self.screen.app.app_dir + '/resent.csv', 'a', newline='') as f:
                writer = csv.writer(f, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([self.text])
        else:
            self.dropdown.resent.remove(self.text)
            self.dropdown.resent.append(self.text)
            with open(self.screen.app.app_dir + '/resent.csv', 'w', newline='') as f:
                writer = csv.writer(f, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in self.dropdown.resent:
                    writer.writerow([row])

        if 'dropdown' in dir(self):
            self.dropdown.dismiss()

        self.screen.search(q = self.text)        

class DropDownResent(DropDown):
    def __init__(self, achor_widget, text_field):
        super(DropDownResent, self).__init__()
        self.text_field = text_field
        self.dismiss_on_select = False
        self.achor_widget = achor_widget
        self.resent_path = text_field.screen.app.app_dir
        self.auto_width = False
        self.width = self.text_field.screen.app.root.size[0]
        self.dd_layout = MDBoxLayout(
            md_bg_color = [0.8,0.9,1,1],
            orientation = "vertical",
            size_hint_y=None,
            height="500dp",      
        )
        self._create_resent_list()     

    def _create_resent_list(self):
        self.resent = []
        count = 0
        q = ''
        for i in self.text_field.text:# escape re meta symbols
            q += f'[{i}]'

        q_regexp = re.compile(rf'(.*){q}(.*)', re.IGNORECASE)
        self._create_header()
        with open(self.resent_path + '/resent.csv', newline='') as f:
            reader = csv.reader(f, delimiter=' ', quotechar='|')
            for row in reversed(list(reader)):
                self.resent.append(row[0])
                s = q_regexp.search(row[0])
                if s and count<9:
                    btn = Button(text=f'{row[0]}', size_hint_y=None, height=44)
                    btn.bind(on_release=self.select_resent)
                    self.dd_layout.add_widget(btn)
                    count += 1

        if count:
            self.dd_layout.add_widget(Widget())
            if self.text_field.screen.session:
                self._create_ending()

            self.add_widget(self.dd_layout)
            self.open(self.achor_widget)
            
        
        
    def _create_header(self):
        resent_header = MDBoxLayout(
            md_bg_color = self.dd_layout.md_bg_color,
            size_hint_y=None,
            height="50dp"
        )
        label = MDLabel(
            text='Resent',
            size_hint_y=None,
            font_size = '26sp',
            height="50dp",
            padding = [20,0,0,0]
        )
        resent_header.add_widget(label)
        clean_btn_box = MDRelativeLayout(size_hint=(None,1), width="150dp",height="50dp")
        label = MDLabel(
            text='[color=ff3333]Clean resent[/color]',
            markup = True,
            height="50dp",
            size_hint_y=None,
            font_size = '26sp',
            padding = [0,0,20,0],
            halign= "right"
        )
        clean_btn_box.add_widget(label)
        btn = Button(background_color=[0,0,0,0.1], size_hint_y=None, size = label.size)
        btn.bind(on_release=self.clean_resent)
        clean_btn_box.add_widget(btn)
        resent_header.add_widget(clean_btn_box)
        self.add_widget(resent_header)
        
    def _create_ending(self):
        resent_ending = MDBoxLayout(
            md_bg_color = self.dd_layout.md_bg_color,
            size_hint_y=None,
            height="50dp"
        )
        switch_btn_box = MDRelativeLayout(size_hint=(None,1), width="150dp",height="50dp")
        label = MDLabel(
            text='[color=ff3333]Global search[/color]',
            markup = True,
            height="50dp",
            size_hint_y=None,
            font_size = '26sp'
        )
        switch_btn_box.add_widget(label)
        btn = Button(background_color=[0,0,0,0.1], size_hint_y=None, size = label.size)
        btn.bind(on_release=self.text_field.search_box.switch_mode)
        switch_btn_box.add_widget(btn)
        resent_ending.add_widget(switch_btn_box)
        self.add_widget(resent_ending)
            
    def select_resent(self, obj):
        self.text_field.text = obj.text
        self.text_field.search()
        self.dismiss()
        
    def clean_resent(self,o):
        with open(self.resent_path + '/resent.csv', 'w', newline='') as _:
            pass
        self.dismiss()    
    
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
        
class EndOfTheList(OneLineAvatarIconListItem):
    def __init__(self):
        super(EndOfTheList, self).__init__()     
        self.add_widget(ImageLeftWidgetWithoutTouch(source="./icons/sadness.png"))
        self.text = 'This is the end of the list'
        
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
        #self.on_release = lambda : self.app.audio_play(track=self.track)
        self.on_release = self.play
        
    ### TRACK METHODS ###
    def play(self):
        self.app.player.start_playback(self)

    def hilighte(self):
        print(f"Track: {self.text} - {self.secondary_text} hilighted")
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhilighte(self):
        print(f"Track: {self.text} - {self.secondary_text} unhilighted")
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
        self.add_to_album_popup = AddToAlbumPopup()

        self.add_to_album_popup.ids.container.clear_widgets()
        album_list = self.app.meta.album_list() ###
        for album in album_list:
            self.add_to_album_popup.ids.container.add_widget(
                AlbumListItem( self.app, album, self.track, self.add_to_album_popup)
            )
        self.add_to_album_popup.open()
        
    def rename_track(self, new_artist=None, new_song=None):
        if new_artist and new_song:
            self.app.meta.edit_track(self.key, new_artist, new_song) ###
            self.text = new_artist
            self.secodary_text = new_song
            return self.rename_track_popup.dismiss()
            
        self.drop_down_menu.dismiss()
        self.rename_track_popup = RenameTrackPopup()
        func = lambda : self.rename_track(
            new_artist=self.rename_track_popup.ids.author.text,
            new_song=self.rename_track_popup.ids.song.text
        )
        btn = PopupActionButton("Enter", func, 0.5)
        self.rename_track_popup.ids.action.clear_widgets()
        self.rename_track_popup.ids.author.text = self.text
        self.rename_track_popup.ids.song.text = self.secondary_text
        self.rename_track_popup.ids.action.add_widget(btn)
        self.rename_track_popup.open()
        
    def delete_track(self, state=None):
        if state == "Confirm":
            try:
                self.app.meta.delete_track(self.key, key_album=self.album_key) ###
            except PermissionError: # if file loaded to player 
                self.app.player.stop()
                self.app.meta.delete_track(self.key, key_album=self.album_key) ###
            
            return self.confirmation_popup.dismiss()
                    
        elif state == "Cancel":
            return self.confirmation_popup.dismiss()

        self.drop_down_menu.dismiss()

        self.confirmation_popup = ConfirmationPopup()

        func = lambda :self.delete_track(state = "Confirm")
        btn1 = PopupActionButton("Confirm", func, 0.2)
        func = lambda :self.delete_track(state = "Cancel")
        btn2 = PopupActionButton("Cancel", func, 0.8)
        self.confirmation_popup.ids.action.clear_widgets()
        self.confirmation_popup.ids.action.add_widget(btn1)
        self.confirmation_popup.ids.action.add_widget(btn2)
        self.confirmation_popup.open()
    
    ### TRACK METHODS ###

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
            self.app.meta.add_to_album(self.track[0], self.album[0]) ###
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
            
        self.ids.close_menu.bind(on_press = lambda x: self.close_selection())
        self.ids.create_album.bind(on_press = lambda x: self.create_album())
        self.ids.delete_selected.bind(on_press = lambda x: self.delete_selected())
        
        self.app.audio_listing_key = 'selection'
        if self.album:
            self.screen.open_album(self.album, session = 1)

        else:
            self.screen.audios_listing(session = 1)

    def delete_selected(self):
        children = [*self.screen.ids.container.children]
        for child in children:
            child.delete_track()
                
        self.close_selection()

        
    def create_album(self, album_name=None):
        if album_name:
            album_key = self.app.meta.add_album(album_name, img=None) ###
            children = [*self.screen.ids.container.children]
            for child in children:
                child.add_to_album(album_key=album_key)

            self.create_album_popup.dismiss()          
            return self.close_selection()
            
        self.create_album_popup = CreateAlbumPopup()
        func = lambda :self.create_album(album_name=self.create_album_popup.ids.album_name.text)
        btn = PopupActionButton("Enter", func, 0.5)
        self.create_album_popup.ids.action.clear_widgets()
        self.create_album_popup.ids.action.add_widget(btn)
        self.create_album_popup.open()
        
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
        print('SessionListElement')
        if 'vk_' in session_name:
            self.session = VK_session(self,session_name)
            
        self.text = self.session.u_name
        self.secondary_text ='Connecting...'
        self.title = ImageLeftWidgetWithoutTouch(source="./icons/load.gif")

        self.add_widget(self.title)
            
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
        if 'vk_' in session_name:
            self.session = VK_session(self,session_name)
            
        self.secondary_text ='Connecting...'
        self.title = ImageLeftWidgetWithoutTouch(source="./icons/load.gif")
        
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
            self.app.meta.delete_track(self.key, key_album=self.album_key) ###
             
    def add_to_album(self, album_key=None):
         if album_key and self.check_box.active:
            self.app.meta.add_to_album(self.key, album_key) ###           

class LoadingAlbums(MDBoxLayout):
    def __init__(self):
        super(LoadingTracks, self).__init__()     
        self.add_widget(ImageLeftWidgetWithoutTouch(source="./icons/load.gif"))
        self.text = 'Loading...'            
class AlbumButton(MDBoxLayout, TouchBehavior):
    def __init__(self, app, album):
        super(AlbumButton, self).__init__()
        self.app = app
        self.album = album
        self.key = album[0]
        self.name = album[1]
        self.img = album[2]
        self.metric = self.app.root.size[0]/2.5
        self.img = Image(
            size=(self.metric,)*2,
            size_hint=(None,None),
            source=self.img
        )
                
        self.album_name = MDLabel(
            size=(self.metric,"20dp"),
            size_hint=(None,None),
            font_size = '14sp',
            text_color = "#232217",
            text = self.name,
            halign = "center",
            pos_hint= {'center_x':.5},
            shorten = True,
            shorten_from = "right"
        )
        
        self.orientation= "vertical"

        self.size_hint_y= None
        self.size_hint_x= None
        self.md_bg_color= "#3F6668"
        self.size=(self.metric,self.metric+self.album_name.size[1])

        self.add_widget(self.img)
        self.add_widget(self.album_name)
        
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            screen_to_return = self.app.manager.current
            self.app.manager.transition = SlideTransition(direction="up")
            self.app.manager.current = 'album'
            self.app.manager.get_screen('album').open_album(self.album) 


class VKTrack(TwoLineAvatarIconListItem):
#class VKTrack(TwoLineIconListItem):
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
        

    def play(self):
        self.app.player.start_playback(self)

    def hilighte(self):
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhilighte(self):
        self.bg_color = [0,0,0,0]
        self.isplaying = False
        
    def download(self):
        self.children[0].remove_widget(self.children[0].children[0])

        self.add_widget(ImageRightWidgetWithoutTouch(source="./icons/load.gif"))
        self.downloadEvent = Clock.schedule_interval(self.dowload_status,1)
        
        key = self.app.meta.new_track(self.text, self.secondary_text, self.img) ###
        task = ('vk',self.text,self.secondary_text,key,self.session.get_link(self.id),self.app.app_dir,self)
        self.app.downloader.add_download_task(task)


    def dowload_status(self, value):
        if self.is_downloaded:
            self.children[0].remove_widget(self.children[0].children[0])
            self.add_widget(ImageRightWidgetWithoutTouch(source="./icons/done.png"))
            self.downloadEvent.cancel()
            
    
class VKAlbumButton(MDBoxLayout, TouchBehavior):
    def  __init__(self, session, app, album):
        super(VKAlbumButton, self).__init__()
        self.img = album[2] or "./icons/song.png"
        self.name = album[1] or "Album"

        self.app = app
        self.session = session
        self.album = album
        
        self.orientation= "vertical"
        self.size_hint_y= None
        self.size_hint_x= None
        self.md_bg_color= "#3F6668"
        self.size=("200dp","220dp")
      
        self.add_widget(
            AsyncImage(
                size=("200dp","200dp"),
                size_hint=(None,None),
                source=self.img,
            )
        )
        self.add_widget(
            MDLabel(
              size=("160dp","20dp"),
              size_hint=(None,None),
              font_size = '14sp',
              text_color = "#232217",
              text = self.name,
              halign = "center",
              pos_hint= {'center_x':.5},
              shorten = True,
              shorten_from = "right"
          )
        )
        
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            screen_to_return = self.app.manager.current
            self.app.manager.transition = SlideTransition(direction="up")
            self.app.manager.current = 'album'
            self.app.manager.get_screen('album').open_album(self.album,session = self.session)

class TopAppBarMenuElem(MDRelativeLayout):
    def  __init__(self, img, pos, func=None):
        super(TopAppBarMenuElem, self).__init__()
        self.pos_hint = {'center_x':pos[0], 'center_y':pos[1]}
        self.size_hint = (None,None)
        self.size = ("40dp","40dp")
        self.md_bg_color= "#3F6668"
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


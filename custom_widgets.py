from kivymd.uix.behaviors import TouchBehavior
from kivy.uix.popup import Popup
from kivymd.uix.list import (OneLineAvatarIconListItem,
                             IconRightWidget,
                             IRightBodyTouch,
                             ImageLeftWidgetWithoutTouch,
                             ImageRightWidgetWithoutTouch,
                             TwoLineAvatarIconListItem)

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
import os
import vk_methods as vk
import shutil
import pickle
from kivy.clock import Clock
from utils import *

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

class Track(TwoLineAvatarIconListItem):
    def __init__(self, app, track):
        super(Track, self).__init__()
        self.add_widget(IconRightWidget(
            icon="./icons/more.png",
            on_release=lambda x: self.track_edit_menu())
        )
        self.app = app
        self.album_key = app.album_screen.key if app.manager.current=='album' else None
        self.track = track
        self.key=track[0]
        self.path=track[1]
        self.text = track[2]
        self.secondary_text = track[3]
        self.img = track[4]

        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.img))
        self.on_release = lambda : self.app.audio_play(track=self.track)
        
    ### TRACK METHODS ###
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
        self.drop_down_menu = MDDropdownMenu(
            caller=self, items=menu_items,position="center",width_mult=3, max_height=150
        )
        self.drop_down_menu.open()
        
    def add_to_album(self):
        self.drop_down_menu.dismiss()
        self.add_to_album_popup = AddToAlbumPopup()

        self.add_to_album_popup.ids.container.clear_widgets()
        album_list = meta_album_list() ###
        for album in album_list:
            self.add_to_album_popup.ids.container.add_widget(
                AlbumListItem( self.app, album, self.track, self.add_to_album_popup)
            )
        self.add_to_album_popup.open()
        
    def rename_track(self, new_artist=None, new_song=None):
        if new_artist and new_song:
            meta_edit_track(self.key, new_artist, new_song) ###
            self.text = new_artist
            self.secodary_text = new_song
            return self.rename_track_popup.dismiss()
            
        self.drop_down_menu.dismiss()

        self.rename_track_popup = RenameTrackPopup()
        btn = Button(size_hint=(0.6,.2),pos_hint={'center_x':0.5, 'center_y':0.2},text="Enter")
        btn.bind(on_press = lambda x:
            self.rename_track(
                new_artist=self.rename_track_popup.ids.artist.text,
                new_song=self.rename_track_popup.ids.song.text
            )
        )
        self.rename_track_popup.ids.action.clear_widgets()
        self.rename_track_popup.ids.artist.text = self.text
        self.rename_track_popup.ids.song.text = self.secondary_text
        self.rename_track_popup.ids.action.add_widget(btn)
        self.rename_track_popup.open()
        
    def delete_track(self, state=None):
        if state == "Confirm":
            try:
                delete_meta_track(self.key, key_album=self.album_key)
            except PermissionError: # if file loaded to player 
                self.app.unload_audio()
                delete_meta_track(self.key, key_album=self.album_key)
            
            return self.confirmation_popup.dismiss()
                    
        elif state == "Cancel":
            return self.confirmation_popup.dismiss()

        self.drop_down_menu.dismiss()

        self.confirmation_popup = ConfirmationPopup()
        no = Button(size_hint=(0.35,.2),pos_hint={'center_x':0.8, 'center_y':0.2},text="Cancel")
        yes = Button(size_hint=(0.35,.2),pos_hint={'center_x':0.2, 'center_y':0.2},text="Confirm")
        yes.bind(on_press = lambda x:self.delete_track(state = "Confirm"))
        no.bind(on_press = lambda x:self.delete_track(state = "Cancel"))
        self.confirmation_popup.ids.action.clear_widgets()
        self.confirmation_popup.ids.action.add_widget(yes)
        self.confirmation_popup.ids.action.add_widget(no)
        self.confirmation_popup.open()
    
    ### TRACK METHODS ###
class AlbumListItem(OneLineAvatarIconListItem):
    def __init__(self, app, album, track, popup=None):
        super(AlbumListItem, self).__init__()
        self.popup = popup
        self.album = album
        self.track = track
        self.text = self.album[2]
        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.album[3]))
        
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            meta_add_to_album(self.track[0], self.album[0]) ###
            return self.popup.dismiss()
            
        
class SelectionBottomMenu(MDBoxLayout):
    def __init__(self, app, screen):
        super(SelectionBottomMenu, self).__init__()
        self.app = app
        self.app.unload_audio()
        self.screen = screen
        # change top bar
        self.name = self.screen.ids.menu_row.title
        self.screen.ids.menu_row.title="selection menu"
        self.screen.ids.menu_row.right_action_items=[]
        self.screen.ids.menu_row.left_action_items=[]

        # remove album list
        if 'outer_album_container' in self.screen.ids:
            self.album_container = self.screen.ids.outer_album_container
            self.screen.ids.box.remove_widget(self.screen.ids.outer_album_container)
        # disable menu
        if 'nav_drawer' in self.screen.ids:
            self.screen.ids.nav_drawer.enable_swiping=False
        # change container content to checkbox
        children = [*self.screen.ids.container.children]
        self.screen.ids.container.clear_widgets()

        for child in children[::-1]:
            
            self.screen.ids.container.add_widget(
                TrackWithCheckBox(self.app, child.track)
            )
            
        self.ids.close_menu.bind(on_press = lambda x: self.close_selection())
        self.ids.create_album.bind(on_press = lambda x: self.create_album())
        self.ids.delete_selected.bind(on_press = lambda x: self.delete_selected())

    def delete_selected(self):
        children = [*self.screen.ids.container.children]
        for child in children:
            child.delete_track()
                
        self.close_selection()

        
    def create_album(self, album_name=None):
        if album_name:
            album_key = meta_add_album(album_name, img=None) ###
            children = [*self.screen.ids.container.children]
            for child in children:
                child.add_to_album(album_key=album_key)
                self.create_album_popup.dismiss()
                
            return self.close_selection()
            
        self.create_album_popup = CreateAlbumPopup()
        btn = Button(size_hint=(0.6,.2),pos_hint={'center_x':0.5, 'center_y':0.2},text="Enter")
        btn.bind(on_press = lambda x:self.create_album(album_name=self.create_album_popup.ids.album_name.text))
        self.create_album_popup.ids.action.clear_widgets()
        self.create_album_popup.ids.action.add_widget(btn)
        self.create_album_popup.open()
        
    def close_selection(self):
        self.screen.remove_widget(self)
        if self.screen.name == 'start':
            self.screen.ids.menu_row.title = self.name
            temp = self.screen.ids.outer_track_container
            self.screen.ids.box.remove_widget(self.screen.ids.outer_track_container)
            self.screen.ids.box.add_widget(self.album_container)
            self.screen.ids.box.add_widget(temp)
            self.screen.ids.nav_drawer.enable_swiping=True
            self.screen.ids.menu_row.right_action_items=[["./icons/edit.png", lambda x: self.screen.edit_menu()]]
            self.screen.ids.menu_row.left_action_items=[["./icons/menu", lambda x: self.screen.ids.nav_drawer.set_state('toggle')]]
            self.screen.downloaded_audios()
        else:
            self.screen.ids.menu_row.right_action_items=[
                ["./icons/edit.png", lambda x: self.screen.edit_menu()],
                ["./icons/back.png", lambda x: self.screen.close_album()]
            ]
            self.screen.open_album(self.name, self.screen.ids.album_image.source, self.screen.screen_to_return)
        
    ### SELECTION MENU METHODS ###

class SessionListElement(TwoLineAvatarIconListItem):
    def __init__(self, app, session_name):
        super(SessionListElement, self).__init__()
        self.app = app
        self.add_widget(IconRightWidget(
            icon="./icons/more.png",
            on_release=lambda x: self.mange_session())
        )
        if 'vk_' in session_name:
            self.session_name = session_name
            self.session = vk.load_session(self.session_name)
            self.type = 'vk'
            with open(self.app_dir + fr'/sessions/{session_name}/uid', 'rb') as f:
                data = pickle.load(f)
                self.text = data['u_name']
                self.secondary_text =data['uid']
            try:
                self.add_widget(ImageLeftWidgetWithoutTouch(source=self.app_dir + rf"/sessions/{session_name}/u_img.jpg"))
            except:
                pass
            
        self.size_hint_y=None
        self.on_release=lambda :self.open_session()

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
        self.app.unload_audio()
        self.app.main_screen.ids.nav_drawer.set_state('toggle')
        self.app.main_screen.vk_audios(self.session, self.secondary_text)
        
    def delete_session(self):
        pass

class TrackWithCheckBox(TwoLineAvatarIconListItem):
    def __init__(self, app, track):
        super(TrackWithCheckBox, self).__init__()
        self.check_box = RightCheckbox(size_hint = (1,None),pos_hint = {'center_y':0.5})
        self.add_widget(self.check_box)
        self.on_release=lambda : self.select(self.check_box)

        self.app = app
        self.album_key = app.album_screen.key if app.manager.current=='album' else None
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
            delete_meta_track(key_track, key_album=self.album_key) ###
             
    def add_to_album(self, album_key=None):
         if album_key and self.check_box.active:
            print(album_key)
            meta_add_to_album(self.key, album_key) ###           
            
class AlbumButton(MDBoxLayout, TouchBehavior):
    def __init__(self, app, album):
        super(AlbumButton, self).__init__()
        self.app = app
        self.album = album
        self.key = album[0]
        self.path = album[1]
        self.name = album[2]
        self.img = album[3]

            
        self.img = Image(
            size=(90,90),
            size_hint=(None,None),
            source=self.img
        )
                
        self.album_name = MDLabel(
            font_size = 13,
            text_color = "#232217",
            halign = "center",
            text = self.name,
            padding = [-1,26,10,0]
        )
        
        self.orientation= "vertical"
        self.adaptive_height= True
        self.size_hint_x= None
        self.add_widget(self.img)
        self.add_widget(self.album_name)
        
        self.press_state = False
        
        self.tap_interval = 0.5
        self.single_hit =  0
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if touch.is_double_tap:
                self.press_state = True
    
                if self.single_hit !=0:
                    self.single_hit.cancel()

                self.dispatch('on_double_press')
        else:
            return super(AlbumButton, self).on_touch_down(touch)
        
    def on_touch_up(self, touch):
        if self.press_state is False:
            if self.collide_point(touch.x, touch.y):
                
                def not_double(time):
                    self.dispatch('on_single_press')

                self.single_hit = Clock.schedule_once(self.on_single_press, self.tap_interval)
            else:
                return super(AlbumButton, self).on_touch_down(touch)
        else:
            self.press_state = False
            
    def on_single_press(self,obj):
        screen_to_return = self.app.manager.current
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album'
        self.app.manager.get_screen('album').open_album(self.album, screen_to_return) 

    def on_double_press(self):
        if self.app.manager.current=='start':
            self.app.manager.transition = SlideTransition(direction="up")
            self.app.manager.current = 'album_list'
            self.app.manager.get_screen('album_list').open_album_list() 

class VKTrack(TwoLineAvatarIconListItem):
    def __init__(self, session, u_id, app, ID, artist, song, img):
        super(VKTrack, self).__init__()
        self.img = img or "./icons/track.png"
        self.text = artist or 'artist'
        self.secondary_text = song or 'song'
        self.id = ID
        self.app = app
        self.u_id = u_id
        self.session = session

        self.add_widget(ImageLeftWidgetWithoutTouch(source=self.img))
        self.add_widget(IconRightWidget(
            icon="./icons/load.png",
            on_release=lambda x: self.download())
        )
    def download(self):
        vk.download_audio(
            self.session,
            self.u_id, self.id,
            self.text,
            self.secondary_text,
            img_link = self.img if self.img!="./icons/track.png" else None
        )
    
class VKAlbumButton(MDBoxLayout, TouchBehavior):
    def  __init__(self, session, u_id, app, ID, name, img):
        super(VKAlbumButton, self).__init__()
        self.img = img or "./icons/song.png"
        self.name = name or "Album"
        self.id = ID
        self.app = app
        self.u_id = u_id
        self.session = session
        
        self.orientation= "vertical"
        self.adaptive_height= True
        self.size_hint_x= None
        self.add_widget(
            AsyncImage(
                size=(90,90),
                size_hint=(None,None),
                source=self.img
            )
        )
        self.add_widget(
            MDLabel(
                font_size = 13,
                text_color = "#232217",
                halign = "center",
                text = self.name,
                padding = [-1,26,10,0]
            )
        )

        self.press_state = False
        
        self.tap_interval = 0.5
        self.single_hit =  0
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if touch.is_double_tap:
                self.press_state = True
    
                if self.single_hit !=0:
                    self.single_hit.cancel()

                self.dispatch('on_double_press')
        else:
            return super(VKAlbumButton, self).on_touch_down(touch)
        
    def on_touch_up(self, touch):
        if self.press_state is False:
            if self.collide_point(touch.x, touch.y):
                
                def not_double(time):
                    self.dispatch('on_single_press')

                self.single_hit = Clock.schedule_once(self.on_single_press, self.tap_interval)
            else:
                return super(VKAlbumButton, self).on_touch_down(touch)
        else:
            self.press_state = False
            
    def on_single_press(self,obj):
        screen_to_return = self.app.manager.current
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album'
        self.app.manager.get_screen('album').vk_open_album(
            self.session,
            self.u_id,
            self.id,
            self.name,
            self.img,
            screen_to_return
        ) 

    def on_double_press(self):
        if self.app.manager.current=='start':
            self.app.manager.transition = SlideTransition(direction="up")
            self.app.manager.current = 'album_list'
            self.app.manager.get_screen('album_list').vk_open_album_list(self.session, self.u_id) 

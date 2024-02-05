from kivy.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.properties import (
    StringProperty,
    DictProperty,
    NumericProperty,
    BooleanProperty,
    ObjectProperty,
    ColorProperty
)
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.image import Image, AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.checkbox import CheckBox
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle,Rectangle


Builder.load_string('''
#:import sp kivy.metrics.sp
#:import dp kivy.metrics.dp
<Track>:
    on_release: self.play()

    TrackImage:
        id: title
        pos: (self.parent.x + self.parent.offset, self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        source: self.parent.title

    Label:
        id: artist
        pos: (title.x + title.width + self.parent.offset,title.y + dp(4))
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.artist
        font_size: "16sp"
        color: (0,0,0,1)
        shorten: True
        shorten_from: "right"
        
    Label:
        id: song
        pos: (title.x + title.width + self.parent.offset,title.y + title.height - dp(4) - self.height)
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.song
        font_size: "16sp"
        color: (0.46,0.46,0.46,1)
        shorten: True
        shorten_from: "right"

    TrackAtion:
        id: action
        pos: (self.parent.x + self.parent.width - self.parent.height,self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        on_release: self.open_edit_menu()
        
        canvas.after:

            Rectangle:
                texture: self.action_texture
                pos: self.x+self.width/4, self.y+self.height/4
                size: self.width/2, self.height/2

<VKTrack>:
    on_release: self.play()
    canvas:
        Color:
            rgb : 0,0,1
        Line:
            rectangle: (self.x,self.y,self.width,self.height)
            width:1

    TrackImage:
        id: title
        pos: (self.parent.x + self.parent.offset, self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        source: self.parent.title

    Label:
        id: artist
        pos: (title.x + title.width + self.parent.offset,title.y + dp(4))
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.artist
        font_size: "16sp"
        color: (0,0,0,1)
        shorten: True
        shorten_from: "right"
        
    Label:
        id: song
        pos: (title.x + title.width + self.parent.offset,title.y + title.height - dp(4) - self.height)
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.song
        font_size: "16sp"
        color: (0.46,0.46,0.46,1)
        shorten: True
        shorten_from: "right"

    VKTrackAtion:
        id: action
        pos: (self.parent.x + self.parent.width - self.parent.height,self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        on_release: self.download()
        
        canvas.after:
            Color:
                rgba: (1,1,1,1)

            Rectangle:
                texture: self.action_texture
                pos: self.x+self.width/4, self.y+self.height/4
                size: self.width/2, self.height/2
                
<TrackWithCheckBox>:
    on_release: self.select(action)

    TrackImage:
        id: title
        pos: (self.parent.x + self.parent.offset, self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        source: self.parent.title

    Label:
        id: artist
        pos: (title.x + title.width + self.parent.offset,title.y + dp(4))
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.artist
        font_size: "16sp"
        color: (0,0,0,1)
        shorten: True
        shorten_from: "right"
        
    Label:
        id: song
        pos: (title.x + title.width + self.parent.offset,title.y + title.height - dp(4) - self.height)
        size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],"20dp")
        text_size: (self.parent.size[0]-4*self.parent.offset-2*title.size[0],dp(20))
        size_hint: (None,None)
        text: self.parent.song
        font_size: "16sp"
        color: (0.46,0.46,0.46,1)
        shorten: True
        shorten_from: "right"

    CheckBox:
        id: action
        pos: (self.parent.x + self.parent.width - self.parent.height,self.parent.y + self.parent.offset)
        size: (self.parent.height-2*self.parent.offset, self.parent.height-2*self.parent.offset)
        size_hint: (None,None)
        background_checkbox_down: './icons/checkbox_active.png'
        background_checkbox_normal: './icons/checkbox.png'
                
<NoAvailableTracks>:
    size_hint_y: None
    height: "72dp"
    Image:
        id: title
        pos: (self.parent.x + dp(5), self.parent.y + dp(5))
        size: (self.parent.height-dp(10), self.parent.height-dp(10))
        size_hint: (None,None)
        source: "./icons/sadness.png"

    Label:
        pos: (title.x + title.width + dp(25),title.y + (title.height - self.height)/2)
        size_hint: (None,None)
        text: 'No available tracks'
        font_size: "16sp"
        color: (0,0,0,1)  
''')

class TrackImage(Widget):
    
    source = StringProperty()
        
    def on_source(self,instance,source=None):
        self.image = AsyncImage(
            size_hint=(None,None),
            fit_mode = 'fill',
            size=("50dp","50dp"),
            source = './icons/player_back.png' if source == './icons/player_back.png' else source
        )
        self.image.fbind('texture',self._draw)
        self._draw()

    def _draw(self,*args):
        with self.canvas.after:
            self.canvas.after.clear()
            Color(1,1,1,1, mode='rgba')
            RoundedRectangle(texture= self.image.texture,pos=self.pos, size=self.size, radius=[dp(5)])
  
class TrackBase(ButtonBehavior):
    
    offset =NumericProperty("5dp")
    
    artist = StringProperty()
    
    song = StringProperty()
    
    title = StringProperty()
    
    bg_color = ColorProperty(None)
    def __init__(self, app, track,**kwargs):
        super(TrackBase, self).__init__(**kwargs)
        self.app = app
        self.track = track
        
        self.title = track[4]
        self.artist = track[2] or 'Artist'
        self.song = track[3] or 'Song'
        try:
            self.album_key = app.album_screen.album[0] if app.manager.current=='album' else None
        except:
            pass

        self.size_hint_y = None
        self.height = "72dp"
        
    def play(self):
        try:
            self.app.player.start_playback(self)
        except:
            self.highlighte()

    def highlighte(self):
        print(f"Track: {self.artist} - {self.song} highlighted")
        self.bg_color = "#E6E6E6"
        self.isplaying = True

    def unhighlighte(self):
        print(f"Track: {self.artist} - {self.song} unhighlighted")
        self.bg_color = [0,0,0,0]
        self.isplaying = False

    def on_bg_color(self, instance, color):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*color, mode='rgba')
            Rectangle(pos=self.pos, size=self.size)

    def select(self, check_box):
        print(check_box.active)
        check_box.active=not check_box.active

    def delete_track(self):
        if self.check_box.active:
            self.app.meta.delete_track(self.key, key_album=self.album_key) # [DB class method]
             
    def add_to_album(self, album_key=None):
         if album_key and self.check_box.active:
            self.app.meta.add_to_album(self.key, album_key) # [DB class method]
        
class ActionBase(ButtonBehavior):
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
        asyncio.get_event_loop().create_task(self.app.downloader.download(task,'vk'))
        
class TrackAtion(ActionBase,Widget):
    
    action_texture = ObjectProperty()
    
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
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
        
    def delete_track(self, state=None):
        if state:
            self.app.meta.delete_track(self.key, key_album=self.album_key) # DB class method
            self.parent.remove_widget(self)    
            return self.popup.dismiss()

        self.drop_down_menu.dismiss()

        self.popup = ConfirmationPopup()

        self.popup.ids.info.text = 'Are you sure want to delete track'
        self.popup.ids.action.ids.text.text = "Confirm"
        self.popup.ids.action.bind(on_release=lambda *args:self.delete_track(state = True))
        self.popup.ids.cancel.ids.text.text = "Cancel"
        self.popup.open()
            
        
class Track(TrackBase, FloatLayout):
    
    isplaying = BooleanProperty(False)
    


class VKTrackAtion(ActionBase,Widget):
    
    action_texture = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(VKTrackAtion, self).__init__(**kwargs)
        self.action_texture = Image(
            size_hint=(None,None),
            size=("25dp","25dp"),
            source = "./icons/load.png"
        ).texture
        
class VKTrack(TrackBase, FloatLayout):
    
    isplaying = BooleanProperty(False)

    is_downloaded = BooleanProperty(False)
    
    def __init__(self, session, app, track):
        super(VKTrack, self).__init__(app, track)
        self.session = session
        
        self.progress = None

class TrackWithCheckBox(TrackBase, FloatLayout):
    pass

class NoAvailableTracks(FloatLayout):
    pass

class EndOfTheList(Widget):
    def __init__(self):
        super(EndOfTheList, self).__init__()     
        self.size_hint_y = None
        self.height = "150dp"
        
styles = '''
RelativeLayout:
    ScrollView:
        size_hint: .4,.8
        pos_hint: {'center_x':0.5,'center_y':0.5}
        canvas:
            Color:
                rgb : 0,0,1
            Line:
                rectangle: (self.x,self.y,self.width,self.height)
                width:1

        GridLayout:
            id: container
            #adaptive_height: True
            size_hint_y: None
            height: self.minimum_height
            cols: 1
        
    
'''
class TestApp(MDApp):
    def build(self):
        self.r = Builder.load_string(styles)
        self.track_list = [('j','path','Boulevar Depo','Loot','C:/Users/VictoR/AppData/Roaming/login/images/t/74.jpg'),
                           ('j','path','Guf','123456789010111213141516171819','./icons/player_back.png'),
                           ('j','path','Degdfggdfgdfgfdgdfgdfgdfgdfgdfgddgfdfdfgdpo','gfddfg','./icons/player_back.png')]
        for track in self.track_list:
            self.r.ids.container.add_widget(Track(self,track))

        self.r.ids.container.add_widget(NoAvailableTracks())
        self.r.ids.container.add_widget(TrackWithCheckBox(self,track))
        return self.r

if __name__ == '__main__':
    TestApp().run()

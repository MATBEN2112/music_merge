from utils import rgb2hex
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image, AsyncImage
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.screenmanager import SlideTransition

class AlbumButton(ButtonBehavior, BoxLayout):
    def __init__(self, session, app, album = (None, "Untitled album", "./icons/song.png",)):
        super(AlbumButton, self).__init__()
        self.app = app
        self.session = session
        self.album = album

        self.key = album[0]
        self.name = album[1] or "Untitled album"
        self.img = album[2] or "./icons/song.png"
        self.metric = self.app.root.size[0]/2.5

        self.img = AsyncImage(
            size=(self.metric,)*2,
            fit_mode = 'fill',
            size_hint=(None,None),
            source=self.img
        )
                
        self.album_name = Label(
            shorten = True,
            size=(self.metric,"20dp"),
            text_size = (self.metric,dp(20)),
            color = self.app.text_clr,
            size_hint=(None,None),
            font_size = '18sp',
            text = self.name,
            halign = "center",
            pos_hint= {'center_x':.5},
            shorten_from = "right"
        )
        
        self.orientation= "vertical"

        self.size_hint= (None,None)
        self.size=(self.metric,self.metric+self.album_name.size[1])

        self.add_widget(self.img)
        self.add_widget(self.album_name)
        self.bind(pos=self._draw, size=self._draw)
        
        
    def on_release(self):
        screen_to_return = self.app.manager.current
        self.app.manager.transition = SlideTransition(direction="up")
        self.app.manager.current = 'album'
        self.app.manager.get_screen('album').open_album(self.album, session = self.session)

    def _draw(self,*args):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self.app.main_clr2, mode='rgba')
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])


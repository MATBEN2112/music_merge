from kivy.uix.scrollview import ScrollView
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ListProperty,
    BooleanProperty,
    ObjectProperty,
    StringProperty,
    ColorProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from math import exp
from kivymd.app import MDApp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.metrics import sp, dp
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle, Line, Rectangle
from kivy.clock import Clock
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
import asyncio
from kivy.uix.boxlayout import BoxLayout

class LoadSignBase(Widget):
    body_clr = ColorProperty((0.26, 0.26, 0.26, 1))
    ''' Body canvas color. '''
    
    def __init__(self,**kwargs):
        super(LoadSignBase, self).__init__(**kwargs)
        self.register_event_type('on_render')
        self.register_event_type('on_start_anim')
        self.register_event_type('on_stop_anim')
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        

    def on_render(self,*args):
        pass

    def on_start_anim(self,*args):
        pass
    
    def on_stop_anim(self,*args):
        pass
    
    def _draw(self,*args):
        pass


class LoadSign(LoadSignBase):
    dot1_clr = ColorProperty((1, 1, 1, 1))
    ''' Left dot color. '''
    
    dot2_clr = ColorProperty((0.5, 0.5, 0.5, 1))
    ''' Center dot color. '''
    
    dot3_clr = ColorProperty((1, 1, 1, 1))
    ''' Right dot color. '''
    
    dot_size = NumericProperty("15dp")
    ''' Dots size. '''
    
    dot_spacing = NumericProperty("25dp")
    ''' Space among dots. '''

    def __init__(self,scroll_view=None,**kwargs):
        super(LoadSign, self).__init__(**kwargs)
        self.scroll_view = scroll_view
        self._offset = 0
        self._lock = False
        self.dot1 = None
        self.dot2 = None
        self.dot3 = None
        self._dots = []
        
        self._draw()

    def _draw(self,*args):
        self.stop_anim()
        
        # draw body canvas
        with self.canvas:
            self.canvas.clear()
            Color(*self.body_clr)
            Rectangle(size=self.size,pos=self.pos)

        self._offset = (self.size[0] - self.dot_spacing*2 - self.dot_size*3)/2
        
        # draw dots
        with self.canvas.after:
            self.canvas.after.clear()
            
            Color(*self.dot1_clr)
            self.dot1 = RoundedRectangle(
                pos = (self.pos[0] + self._offset,self.pos[1] + self.size[1]/2 - self.dot_size/2),
                size = (self.dot_size,)*2,
                radius = [22,])

            Color(*self.dot2_clr)
            self.dot2 = RoundedRectangle(
                pos = (
                    self.pos[0] + self._offset + self.dot_size + self.dot_spacing,
                    self.pos[1] + self.size[1]/2 - self.dot_size/2
                ),
                size = (self.dot_size,)*2,
                radius = [22,])

            Color(*self.dot3_clr)
            self.dot3 = RoundedRectangle(
                pos = (
                    self.pos[0] + self._offset + (self.dot_size + self.dot_spacing)*2,
                    self.pos[1] + self.size[1]/2 - self.dot_size/2
                ),
                size = (self.dot_size,)*2,
                radius = [22,])
            

        self._dots = [self.dot1,self.dot2,self.dot3]

    def stop_anim(self,*args):
        if self._dots:
            self._dots = [self.dot1,self.dot2,self.dot3]

        for i in range(len(self._dots)):
            dot = self._dots[i]
            Animation.cancel_all(dot)
            dot.pos = (
                self.pos[0] + self._offset + (self.dot_size + self.dot_spacing)*i,
                self.pos[1] + self.size[1]/2 - self.dot_size/2
            )

        self._lock = False
    
    def start_anim(self,*args):
        self._anim()
    
    def _anim(self):
        dot = self._dots.pop(0)
        anim = Animation(
            pos = (dot.pos[0],self.pos[1] + self.size[1] - self.dot_size*2),
            d= .3,
            t = 'in_quad'
        ) + \
        Animation(pos = (dot.pos[0],self.pos[1] + self.size[1]/2 - self.dot_size/2),d= .3,t = 'in_quad')
        anim.bind(on_complete=self._unlock)
        anim.bind(on_progress=self._next)
        
        self._dots.append(dot)
        anim.start(dot)
        
    def _next(self, *args):
        if args[2] > 0.5 and not self._lock:
            self._lock = True
            self._anim()

    def _unlock(self, *args):
        self._lock = False

Builder.load_string('''
<Track>:
    on_release: self.highlighte()

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

''')
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
    
    def __init__(self, app, track = (None, '', 'Artist', 'Song', './icons/player_back.png',)):
        super(TrackBase, self).__init__()
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
        
class ActionBase(ButtonBehavior):

    action_texture = ObjectProperty()

    def __init__(self, **kwargs):
        super(ActionBase, self).__init__(**kwargs)
        self.fbind('pos',self._draw)
        self.fbind('size',self._draw)
        self.fbind('action_texture',self._draw)

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
            source = "./../icons/more.png"
        ).texture
        
class Track(TrackBase, FloatLayout):
    pass

class AlbumButton(ButtonBehavior, BoxLayout):
    def __init__(self, session, app, album = (None, "Untitled album", ".././icons/song.png",)):
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
            size_hint=(None,None),
            source=self.img
        )
                
        self.album_name = Label(
            shorten = True,
            size=(self.metric,"20dp"),
            text_size = (self.metric,dp(20)),
            color = (0,0,0,1),
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
        
    def _draw(self,*args):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(0,0,1,1, mode='rgba')
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])

Builder.load_string('''
<NoAvailableTracks>:
    size_hint_y: None
    height: "72dp"
    Image:
        id: title
        pos: (self.parent.x + dp(5), self.parent.y + dp(5))
        size: (self.parent.height-dp(10), self.parent.height-dp(10))
        size_hint: (None,None)
        source: ".././icons/sadness.png"

    Label:
        pos: (title.x + title.width + dp(25),title.y + (title.height - self.height)/2)
        size_hint: (None,None)
        text: 'No available tracks'
        font_size: "16sp"
        color: (0,0,0,1)
''')
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

    def add_track(self,i):
        print(self.child_kwargs[i],'###')
        track_obj = self.child_class(*self.child_args, **self.child_kwargs[i])
        self.add_widget(track_obj)

    def add_album(self,i):
        album_obj = self.child_class(*self.child_args, **self.child_kwargs[i])
        self.add_widget(album_obj)

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
        print(self._index)
  
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
                        self.add_album(self._index)
                    else:
                        self.add_track(self._index)

            # rescroll
            self.parent.scroll_y = 1 - self.chunk_size*self._child_height/self.parent.viewport_size[1]
            
            # create and add dummy either dynamic load of elements works awful
            # [ idk probable scrollview critical value appears ]
            self.dummy = Widget(size_hint_y = None, height = self.__exchange)
            self.__exchange *= -1
            self.add_widget(self.dummy)

        print(self._index)
            

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

styles = '''
<UpdatableListingContainer>:
    id: outer_container
    container: container
    load_sign: load_sign
    scroll_view: scroll_view
    StencilView:
        id: refresh_container
        size_hint: None, None
        size: (scroll_view.size[0],abs(scroll_view.min__overscroll))
        pos: (scroll_view.x,scroll_view.y+scroll_view.height-self.height)

        LoadSign:
            id: load_sign
            size_hint: None, None
            body_clr: (0,0,0,0)
            dot1_clr: (59/255, 85/255, 158/255, 1)
            dot2_clr: (129/255, 190/255, 247/255, 1)
            dot3_clr: (59/255, 85/255, 158/255, 1)
            dot_spacing: "50dp"
            pos: (self.parent.x+(scroll_view.width-self.width)/2,self.parent.y-scroll_view.min__overscroll)
            height: abs(scroll_view.min__overscroll)
            scroll_view: scroll_view
            
                
    UpdatableScrollView:
        id: scroll_view
        size_hint: None, None
        size: self.parent.size
        pos: self.parent.pos
        HighPerformanceContainer:
            id: container
            child_args: (app,)
            size_hint_y: None
            height: self.minimum_height
            cols: 1

'''
Builder.load_string(styles)
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
        
        if self.header and self._prev_scroll_y:
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

        # detemice where does the scroll go
        self._prev_scroll_y = scroll_y

    def _selection_start(self):
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


    def get_listing(self):
        return (self.container.child_class, self.container.child_args, self.listing, self.container.album_id)

    def append_listing(self,child_kwargs):
        for child in child_kwargs:
            self.container.child_kwargs.append(child)

    def clear(self):
        self.container.clear_widgets()



 
styles = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '150dp'

    UpdatableListingContainer:
        id: scrl
        pos_hint: {'center_x':0.5}
        overscroll_callback: (app.refresh_callback,(),{})
        canvas:
            Color:
                rgb : 0,0,1
            Line:
                rectangle: (self.x,self.y,self.width,self.height)
                width:1
            
    Button:
        size_hint_y: None
        height: '150dp'
        text: 'Track kisting'
        on_release: app.switch_listing(self)
        
    
'''

class UpdatableScrollViewApp(MDApp):

    track = BooleanProperty(True)
    
    def build(self):
        self.styles = Builder.load_string(styles)
        return self.styles
    
    def on_start(self):
        self.do_listing()

    def switch_listing(self, btn):
        btn.text = 'Album listing'
        self.track = not self.track
        self.do_listing()

    def do_listing(self):
        if self.track:
            data = []
            for i in range(400):
                data.append((str(i),str(i), 'Artist', f'Song {i}','./../icons/player_back.png'))

            data.append('EOL')
            self.styles.ids.scrl.set_listing(child_args=(self,),child_kwargs = data,child_class = Track)

        else:
            data = []
            for i in range(100):
                data.append((str(i),f"Untitled album {i}",'.././icons/song.png'))

            data.append('EOL')
            self.styles.ids.scrl.set_listing(child_args=(None, self,),child_kwargs = data,child_class = AlbumButton)
            

    async def refresh_callback(self,scroll_view):
        await asyncio.sleep(1)
        if self.track:
            data = []
            for i in range(50):
                data.append((str(i),str(i), 'Artist', f'Song {i}','./../icons/player_back.png'))

            self.styles.ids.scrl.append_listing(data)
        else:
            data = []
            for i in range(50):
                data.append((str(i),f"Untitled album {i}",'.././icons/song.png'))

            self.styles.ids.scrl.append_listing(data)
            
        

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UpdatableScrollViewApp().async_run(async_lib='asyncio'))
    loop.close()

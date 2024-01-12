from kivy.uix.layout import Layout
from kivy.properties import ListProperty, NumericProperty, DictProperty, OptionProperty,ObjectProperty, BooleanProperty
from kivy.animation import Animation
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

class DraggableScreenLayout(Layout):
    ''' Static screen. '''
    main_screen = ObjectProperty()

    ''' Swipeable screen. '''
    secondary_screen = ObjectProperty()

    ''' Property indicates which side second screen will be swiped from. '''
    direction = OptionProperty('right',options=("left", "right","top","bottom"))

    ''' Boolean property indicates is secondary screen is opened or closed. '''
    isopen = BooleanProperty(False)
    
    ''' The threshold used to trigger swipe as ratio of the screen size. '''
    sencety = NumericProperty(0.04)
    
    ''' The size of the border on main screen triggers grab action. '''
    border = NumericProperty('100dp')

    ''' Child widgets list ignoring bubbling when swipe is triggered
    (default: prevents unexpected button clicks).
    Swipe priority is higher than priority of interaction with listed widgets. '''
    low_priority = ListProperty((Button,ScrollView))

    ''' Child widgets list ignoring bubbling when swipe is triggered
    (default: prevents swiping on slider interact).
    Swipe priority is lower than priority of interaction with listed widgets. '''
    high_priority = ListProperty((Slider,))

    ''' The threshold used to trigger screen opening/closing as ratio of the screen size. '''
    swipe_threshold = NumericProperty(.3)
    
    ''' The animation kwargs used to construct the animation '''
    anim_kwargs = DictProperty({'d': .5, 't': 'in_quad'})
 
    def __init__(self, **kwargs):
        super(DraggableScreenLayout, self).__init__(**kwargs)
        self.animation = None
        self.sencety_lock = True
        self.child_event = False
        self._touch = None
        trigger = self._trigger_layout
        fbind = self.fbind
        fbind('border', trigger)
        fbind('parent', trigger)
        fbind('size', trigger)
        fbind('pos', trigger)

    def on_main_screen(self, *args):
        pass

    def on_secondary_screen(self, *args):
        pass

    def do_layout(self, *largs, **kwargs):
        w, h = kwargs.get('size', self.size)
        x, y = kwargs.get('pos', self.pos)
        for c in self.children:
            # size
            shw, shh = c.size_hint
            shw_min, shh_min = c.size_hint_min
            shw_max, shh_max = c.size_hint_max

            if shw is not None and shh is not None:
                c_w = shw * w
                c_h = shh * h

                if shw_min is not None and c_w < shw_min:
                    c_w = shw_min
                elif shw_max is not None and c_w > shw_max:
                    c_w = shw_max

                if shh_min is not None and c_h < shh_min:
                    c_h = shh_min
                elif shh_max is not None and c_h > shh_max:
                    c_h = shh_max
                c.size = c_w, c_h
            elif shw is not None:
                c_w = shw * w

                if shw_min is not None and c_w < shw_min:
                    c_w = shw_min
                elif shw_max is not None and c_w > shw_max:
                    c_w = shw_max
                c.width = c_w
            elif shh is not None:
                c_h = shh * h

                if shh_min is not None and c_h < shh_min:
                    c_h = shh_min
                elif shh_max is not None and c_h > shh_max:
                    c_h = shh_max
                c.height = c_h

            # pos
            for key, value in c.pos_hint.items():
                if key == 'x':
                    c.x = x + value * w
                elif key == 'right':
                    c.right = x + value * w
                elif key == 'pos':
                    c.pos = x + value[0] * w, y + value[1] * h
                elif key == 'y':
                    c.y = y + value * h
                elif key == 'top':
                    c.top = y + value * h
                elif key == 'center':
                    c.center = x + value[0] * w, y + value[1] * h
                elif key == 'center_x':
                    c.center_x = x + value * w
                elif key == 'center_y':
                    c.center_y = y + value * h
                    
        if not self.main_screen:
            self.main_screen = self.children[-1]
            
        if not self.secondary_screen:
            self.secondary_screen = self.children[-2]
            if self.direction == 'right':
                self.secondary_screen_start_pos = (self.main_screen.right,self.main_screen.pos[1])
                self.secondary_screen.pos = self.secondary_screen_start_pos
                
            elif self.direction == 'left':
                self.secondary_screen_start_pos = (-self.main_screen.right,self.main_screen.pos[1])
                self.secondary_screen.pos = self.secondary_screen_start_pos

            elif self.direction == 'top':
                self.secondary_screen_start_pos = (self.main_screen.pos[0],self.main_screen.top)
                self.secondary_screen.pos = self.secondary_screen_start_pos

            elif self.direction == 'bottom':
                self.secondary_screen_start_pos = (self.main_screen.pos[0],-self.main_screen.top)
                self.secondary_screen.pos = self.secondary_screen_start_pos
            
        if self.isopen:
            Animation(pos = self.main_screen.pos,**self.anim_kwargs).start(self.secondary_screen)

        else:
            Animation(pos = self.secondary_screen_start_pos,**self.anim_kwargs).start(self.secondary_screen)


    def _grab(self,touch):
        if self.direction == 'right':
            if not self.isopen and self.main_screen.right-self.border <= touch.x < self.main_screen.right: # secondary screen hiden
                touch.grab(self)

            elif self.isopen:
                touch.grab(self)
            
        elif self.direction == 'left':
            if not self.isopen and self.main_screen.x <= touch.x < self.main_screen.x+self.border: # secondary screen hiden
                touch.grab(self)

            elif self.isopen:
                touch.grab(self)

        elif self.direction == 'top':
            if not self.isopen and self.main_screen.top - self.border <= touch.y < self.main_screen.top: # secondary screen hiden
                touch.grab(self)

            elif self.isopen:
                touch.grab(self)

        elif self.direction == 'bottom':
            if not self.isopen and self.main_screen.y <= touch.y < self.main_screen.y + self.border: # secondary screen hiden
                touch.grab(self)

            elif self.isopen:
                touch.grab(self)

    def _event_priority(self, touch):
        __lock = False
        widgets = touch.grab_list
        if widgets:
            for widget in widgets:
                if isinstance(widget(),(*self.low_priority,)):
                    # is there any other way to stop bubbling???
                    touch.ungrab(widget())
                    # Button after all still highlighted but not triggered.
                    # [TODO Touch event propagations needs to be reworked on ScrollView class base]
                elif isinstance(widget(),(*self.high_priority,)):
                    __lock = True

        return __lock
                    
                
    def on_touch_down(self, touch):
        if (self.disabled or not self.collide_point(*touch.pos) or not self.children):
            return False

        self._grab(touch)
     
        # propagate motion event to children
        if self.isopen:
            for child in self.children:
                if child != self.main_screen:
                    if child.dispatch("on_touch_down", touch):
                        self.child_event = True
                        return self.child_event
                    

        else:
            for child in self.children:
                if child != self.secondary_screen:
                    if child.dispatch("on_touch_down", touch):
                        self.child_event = True
                        return self.child_event
            
        return True
        
    def on_touch_move(self, touch):
        

        if touch.grab_current == self and not self._event_priority(touch):
            print(touch.grab_list)
            return self._move_screen(touch)
            
        else:
            return super().on_touch_move(touch)

    def _move_screen(self,touch):
            
        if not self.sencety_lock or self.sencety < abs(touch.sx - touch.osx):
            if self.direction == 'right':
                self.sencety_lock = False
                if self.isopen:
                    self.secondary_screen.x = min(self.main_screen.right,max(0+(touch.x - touch.ox),0))

                else:
                    self.secondary_screen.x = max(0,min(self.main_screen.width+(touch.x - touch.ox),self.main_screen.right))

            elif self.direction == 'left':
                self.sencety_lock = False
                if self.isopen:
                    self.secondary_screen.x = min(0,max(0+(touch.x - touch.ox),-self.main_screen.right))

                else:
                    self.secondary_screen.x = max(-self.main_screen.right,min(-self.main_screen.right+(touch.x - touch.ox),0))

        if not self.sencety_lock or self.sencety < abs(touch.sy - touch.osy):
            if self.direction == 'top':
                self.sencety_lock = False
                if self.isopen:
                    self.secondary_screen.y = min(self.main_screen.top,max(0+(touch.y - touch.oy),0))

                else:
                    self.secondary_screen.y = max(0,min(self.main_screen.top+(touch.y - touch.oy),self.main_screen.top))

            
            elif self.direction == 'bottom':
                self.sencety_lock = False
                if self.isopen:
                    self.secondary_screen.y = min(0,max(0+(touch.y - touch.oy),-self.main_screen.top))

                else:
                    self.secondary_screen.y = max(-self.main_screen.top,min(-self.main_screen.top+(touch.y - touch.oy),0))     

        return True

    def on_touch_up(self, touch):

        self.sencety_lock = True
        self.child_event = False
            
        if touch.grab_current == self:
            k_x = abs(abs(self.secondary_screen.x)/self.main_screen.right - 1*self.isopen)
            k_y = abs(abs(self.secondary_screen.y)/self.main_screen.top - 1*self.isopen)
            
            if (k_x < self.swipe_threshold and self.direction in ['left','right']) \
            or (k_y < self.swipe_threshold and self.direction in ['bottom','top']): # chages state close or open
                self.isopen = not self.isopen
           
            self._trigger_layout() # trigger animation

            touch.ungrab(self)
            return True
            
        elif self.isopen:
            return self.secondary_screen.dispatch("on_touch_up", touch)

        else:
            return self.main_screen.dispatch("on_touch_up", touch)

    def open_screen(self):
        self.isopen = True
        self._trigger_layout()

    def close_screen(self):
        self.isopen = False
        self._trigger_layout()

from kivy.app import App
from kivy.lang import Builder
from kivy.base import runTouchApp
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

class AudioBar(BoxLayout):
    pass

class Main(Screen):
    pass

class Player(Screen):
    pass

kv = '''
<AudioBar>:
    id: audio_row
    height:"100dp"
    size_hint: .9,None
    pos_hint: {'center_x':0.5, 'center_y':-0.1}

    Button:
        id: action
        text: "play"
        font_size:'20sp'
        size_hint: None,1
        width: "90dp"
        on_release: app.play_stop()

    Button:
        id: song_name
        text: "Artist - song"
        font_size:'20sp'
        on_release: app.open_player()
		
    Button:
        id: song_timer
        size_hint: None,1
        width: "70dp"
        text: "00:00"
        font_size: '20sp'
        on_release: app.open_player()


<Main>:
    BoxLayout:
        orientation: "vertical"

        RelativeLayout:
            id: menu_row
            orientation: "vertical"
            size: (root.size[0],"200dp")
            size_hint: (None,None)
            pos_hint: {'center_x':0.5, 'center_y':0.95}
            canvas.after:
                Color:
                    rgba: 1, 0, 0, 0.5
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                pos_hint: {'center_x':0.5, 'center_y':0.5}
                text: "Menu bar"
                font_size: '28sp'
            

        BoxLayout:
            orientation: "vertical"
            size_hint: (None,None)
            size: (root.size[0],root.size[1]-menu_row.height)
            ScrollView:
                do_scroll_y: True
                
                BoxLayout:
                    id: box
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 0.5
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    Button:
                        text: 'add'
                        size_hint_y: None
                        height: "100dp"
                        font_size: '28sp'
                        on_release: app.add_w()
            
<Player>:
    RelativeLayout
        canvas.before:
            Color:
                rgba: 0, 0, .8, 0.5
            Rectangle:
                pos: self.pos
                size: self.size
        Button:
            pos_hint: {'center_x':0.5, 'top':1}
            background_color: 0,0,0,1
            size: (root.size[0],root.size[1]/4.7)
            size_hint: (None,None)
            text: 'close'
            on_release: app.close_player()
            
        Label:
            id: song_name
            text: "Artist - song"
            font_size: '28sp'
            width: root.size[0]*.9
            size_hint: (None,1)
            pos_hint:{'center_x':0.5, 'center_y':.4}


        Label:
            text: "00:00"
            pos_hint: {'center_x':.16, 'center_y':.3}
            size_hint: (1,1)
            font_size: "20sp"
        
        Label:
            text: "00:00"
            pos_hint: {'center_x':.84, 'center_y':.3}
            size_hint: (1,1)
            font_size: "20sp"
        
        Slider:
            orientation: "horizontal"
            active: False
            hint_radius: 10
            pos_hint: {'center_x':0.5, 'center_y':0.32}
            size: (root.size[0]*0.8,"25dp")
            size_hint: (None,None)


        Button:
            pos_hint: {'center_x':0.25, 'center_y':0.2}
            size: ("90dp","90dp")
            size_hint: (None,None)
            text: 'prev'
            on_release: app.next(1)

        Button:
            id: action
            pos_hint: {'center_x':0.5, 'center_y':0.2}
            size: ("90dp","90dp")
            size_hint: (None,None)
            text: 'play'
            on_release: app.play_stop()

        Button:
            pos_hint: {'center_x':0.75, 'center_y':0.2}
            size: ("90dp","90dp")
            size_hint: (None,None)
            text: 'next'
            on_release: app.next(-1)

'''

class ScreenLayoutApp(App):
    def build(self):
        self.current = 0
        self.audio = []
        Builder.load_string(kv)
        self.main_screen = Main(name='main')
        self.audio_bar = AudioBar()
        
        self.player_screen = Player(name='player')
        for i in range(1,10):
            self.audio.append(f"Artist - song {i}")
            self.main_screen.ids.box.add_widget(Button(
                        text = f"Artist - song {i}",
                        size_hint_y = None,
                        height = "100dp",
                        font_size = '28sp',
                        on_release = self.open_player_bar
                        ))
        self.audio = self.audio[::-1]
        self.manager = DraggableScreenLayout(direction = 'bottom')
        self.manager.add_widget(self.main_screen)
        self.manager.add_widget(self.player_screen)
        self.manager.add_widget(self.audio_bar)
        return self.manager

    def play_stop(self,*args):
        print(self.audio_bar.pos)
        self.player_screen.ids.action.text = 'play' if self.player_screen.ids.action.text=='stop' else 'stop'
        self.audio_bar.ids.action.text = 'play' if self.audio_bar.ids.action.text=='stop' else 'stop'

    def next(self,i):
        try:
            self.current += i
            if self.current<0:
                raise IndexError
            
            self.player_screen.ids.song_name.text = self.audio[self.current]
            self.audio_bar.ids.song_name.text = self.audio[self.current]
            
        except IndexError:
            self.current -= i

    def close_player(self):
        self.manager.close_screen()

    def open_player(self):
        self.manager.open_screen()
        
    def open_player_bar(self,*args):
        self.audio_bar.pos_hint= {'center_x':0.5, 'center_y':0.1}
        self.current = args[0].parent.children.index(args[0])
        self.player_screen.ids.song_name.text = args[0].text
        self.audio_bar.ids.song_name.text = args[0].text
        print(self.audio_bar.collide_point(50,50))

    def add_w(self):
        self.main_screen.ids.box.add_widget(Button(
                        text = f"Artist - song added",
                        size_hint_y = None,
                        height = "100dp",
                        font_size = '28sp',
                        on_release = self.open_player_bar
                        ))
        

if __name__ == '__main__':
    ScreenLayoutApp().run()

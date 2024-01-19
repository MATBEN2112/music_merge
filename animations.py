from kivy.app import App
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.metrics import sp
from kivy.core.text import Label as CoreLabel
from kivy.properties import (
    OptionProperty,
    ObjectProperty,
    NumericProperty,
    BooleanProperty,
    StringProperty,
    ColorProperty,
    ListProperty,
)
from kivy.graphics import (
    Color,
    Ellipse,
    Rectangle,
    Line,
    PushMatrix,
    PopMatrix,
    Rotate,
    StencilPop,
    StencilPush,
    StencilUnUse,
    StencilUse,
)

from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.widget import Widget
from kivy.clock import Clock
from math import sqrt
from kivy.graphics.texture import Texture
from gradient import Gradient

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

class CircularProgressBar(LoadSignBase): 
    thickness = NumericProperty("5dp")
    ''' Circle thickness. '''
    
    force_anim = BooleanProperty(True)
    ''' Label object to be draw. '''

    progress_clr = ColorProperty((1, 1, 1, 1))
    ''' Progress line color. '''
    
    label_clr = ColorProperty((1, 1, 1, 1))
    ''' Label text color. '''

    hint_clr = ColorProperty((.74, .74, .74, 1))
    ''' Hint color. '''
    
    label = ObjectProperty()
    ''' Label object to be draw. '''
    
    value = NumericProperty(0)
    ''' Represents current progress. '''
    
    widget_size = NumericProperty("100dp")
    ''' Circle size. '''

    _default_label_text = StringProperty("100dp")
    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        # Initialise the values modifiable via the class properties
        self._max_progress = 100
        self._min_progress = 0
        
        self.scheduler = None
        self._draw()

    @property
    def max(self):
        return self._max_progress

    @max.setter
    def max(self, value):
        if type(value) != int:
            raise TypeError("Maximum progress only accepts an integer value, not {}!".format(type(value)))
        elif value <= self._min_progress:
            raise ValueError("Maximum progress - {} - must be greater than minimum progress ({})!"
                             .format(value, self._min_progress))
        else:
            self._max_progress = value

    @property
    def min(self):
        return self._min_progress

    @min.setter
    def min(self, value):
        if type(value) != int:
            raise TypeError("Minimum progress only accepts an integer value, not {}!".format(type(value)))
        elif value > self._max_progress:
            raise ValueError("Minimum progress - {} - must be smaller than maximum progress ({})!"
                             .format(value, self._max_progress))
        else:
            self._min_progress = value
            self._value = value

    def on_label(self, *args):
        # Label-related values
        self.label = args[1]
        self._default_label_text = self.label.text
        self._label_size = (0, 0)
        

    def on_value(self, instance, value):
        if type(value) != int:
            raise TypeError("Progress must be an integer value, not {}!".format(type(value)))

        self._draw()

    def _norm(self):
        return abs(self.value/ ((self._max_progress - self._min_progress) / 100) / 100)

    def _percent(self):
        return int(abs(self.value/ ((self._max_progress - self._min_progress) / 100)))

    def _refresh_text(self):
        self.label.text = self._default_label_text.format(str(self._percent()))
        self.label.refresh()
        self._label_size = self.label.texture.size


    def _draw(self,*args):
        if not self.label:
            self.label = CoreLabel(text="{}%", font_size=sp(20))
            
        with self.canvas:
            self.stop_anim()
            self.canvas.clear()
            self._refresh_text()

            # Draw the background progress line
            Color(*self.body_clr)
            Line(circle=(self.pos[0] + self.widget_size / 2, self.pos[1] + self.widget_size / 2,
                         self.widget_size / 2 - self.thickness), width=self.thickness)

            # Draw the progress line
            if self._min_progress < self.value <= self._max_progress:
                Color(*self.progress_clr)
                Line(
                    circle=(
                        self.pos[0] + self.widget_size / 2,
                        self.pos[1] + self.widget_size / 2,
                        self.widget_size / 2 - self.thickness,
                        0,
                        self._norm() * 360
                    ),
                    width=self.thickness,
                    cap='round'
                    
                )

                # Center and draw the progress text
                Color(*self.label_clr)
                Rectangle(
                    texture=self.label.texture,
                    size=self._label_size,
                    pos=(
                        self.widget_size / 2 - self._label_size[0] / 2 + self.pos[0],
                        self.widget_size / 2 - self._label_size[1] / 2 + self.pos[1]
                    )
                )
                
            else:
                if self.force_anim:
                    self.start_anim()
     
    def start_anim(self):
        self.stop_anim()
        self._draw_hint()
        def _anim(*args):
            self.rotation.angle += 9
            if self.rotation.angle == 360:
                self.rotation.angle = 0
        
        self.scheduler = Clock.schedule_interval(_anim, 1/20)
                        
    def stop_anim(self):
        if self.scheduler:
            self.scheduler.cancel()
                
        self.canvas.after.clear()

    def _draw_hint(self):
        with self.canvas.after:
            PushMatrix(group="hint")
            self.rotation = Rotate(
                origin = (self.pos[0] + self.widget_size / 2,self.pos[1] + self.widget_size / 2),
                angle = 0,group="hint")
            
            StencilPush(group="hint")
            self.rect = Line(
            circle=(
                self.pos[0] + self.widget_size / 2,
                self.pos[1] + self.widget_size / 2,
                self.widget_size / 2 - self.thickness,
                0,
                -80
            ),
            width=self.thickness,
            group="hint"
            )
            StencilUse(group="hint")
            
            Color(*self.hint_clr)
            Rectangle(
                pos = self.pos,
                size = (self.widget_size,)*2,
                texture = Gradient.gradient((self.hint_clr,(0,0,0,0))),
                group="hint"
            )
            
            StencilUnUse(group="hint")
            Line(
            circle=(
                self.pos[0] + self.widget_size / 2,
                self.pos[1] + self.widget_size / 2,
                self.widget_size / 2 - self.thickness,
                0,
                -80
            ),
            width=self.thickness,
            group="hint"
            )

            StencilPop(group="hint")

            PopMatrix(group="hint")

class LoadingBar(LoadSignBase):
    label_clr = ColorProperty((1,1,1,1))
    ''' Label text color. '''
    
    filling_clr = ColorProperty([0.9,0.9,0.9,0.5,])
    ''' Fill color. '''

    blink_duration = NumericProperty(1)
    ''' Widget blink duration. '''
    
    filling_duration = NumericProperty(2)
    ''' Widget fill duration. '''

    fade_duration = NumericProperty(0.3)
    ''' Widget filling fade out duration. '''
    
    start_side = OptionProperty('left',options=("left", "right","top","bottom"))
    ''' Side fill starts from. '''
    
    anim_mode = OptionProperty('fill',options=("fill", "blink"))
    ''' Animation mode. '''
    
    sides = ListProperty()
    ''' List of sides fill starts from. '''
    
    label = ObjectProperty()
    ''' Label object to be draw. '''

    angle_rad = ListProperty([0, 0, 0, 0])
    ''' Do not let fillig go out of bounds if canvas is RoudedRectangle. '''
 
    _spread_rad = NumericProperty(0.1)
    _filling_clr = ColorProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # draw
        self.filling = None
        self._filling_clr = self.filling_clr

        self.bind(_filling_clr=self._set_color, _spread_rad=self._set_ellipse)
        self._sides = {}
        self._fill_order()
        self.fbind('sides',self._fill_order)
        self.fbind('start_side',self._fill_order)

        self._draw()

    def on_label(self,*args):
        self.label = args[1]
        
        # label parameters
        self._lt = [self.label.text + '.'*i for i in range(4)]
        self._text_index = 0
        self.text_event = None
        self._label_size = (0,0)
        self.label_text = None
        self._fixed_pos = None
        self._refresh_text(start = True)

    def _fill_order(self,*args):
        if args and isinstance(args[1],(list,tuple,)):
            self._sides = {s:None for s in args[1]}
        
        elif args and args[1] == "left":
            self.sides = ["left","right"]
            self._sides = {"left":None, "right":None}
            
        elif args and args[1] == "top":
            self.sides = ["top","bottom"]
            self._sides = {"top":None,"bottom":None}

        elif args and args[1] == "right":
            self.sides = ["right","left"]
            self._sides = {"right":None, "left":None}
            
        elif args and args[1] == "bottom":
            self.sides = ["bottom","top"]
            self._sides = {"bottom":None,"top":None}

        else:
            pass
            
        self._side = self.start_side
        self._side_index = 0       
        
    def _refresh_text(self, *args, start = False):
        if start or self._text_index >= len(self._lt):
            self._text_index = 0
            
        self.label.text = self._lt[self._text_index]
        self.label.refresh()
        self._label_size = self.label.texture.size
        if not self._fixed_pos:
            self._fixed_pos = (*self._label_size,)
            
        self._text_index += 1

        # Draw text
        with self.canvas.after:
            self.canvas.after.clear()
            Color(*self.label_clr)
            self.label_text = Rectangle(
                texture=self.label.texture,
                size=self._label_size,
                pos=(
                    self.size[0] / 2 - self._fixed_pos[0] / 2 + self.pos[0],
                    self.size[1] / 2 - self._fixed_pos[1] / 2 + self.pos[1]
                )
            )

    def _draw(self,*args):
        if not self.label:
            self.label = CoreLabel(text="Loading", font_size=sp(20))
            
        if self.text_event:
            self.text_event.cancel()

        # Draw body
        with self.canvas:
            self.canvas.clear()
            Color(*self.body_clr)
            Rectangle(size=self.size,pos=self.pos)

        self._refresh_text(start = True)

        # set spread start points
        for key in self._sides.keys():
            if key == "left":
                self._sides["left"] = (self.pos[0],self.pos[1]+self.size[1]/2)
            elif key == "right":
                self._sides["right"] = (self.pos[0]+self.size[0],self.pos[1]+self.size[1]/2)
            elif key == "top":
                self._sides["top"] = (self.pos[0] + self.size[0]/2,self.pos[1]+self.size[1])
            elif key == "bottom":
                self._sides["bottom"] = (self.pos[0] + self.size[0]/2,self.pos[1])

    def stop_anim(self):
        if self.text_event:
            self.text_event.cancel()

        # cancel resent animations
        Animation.cancel_all(self, "_spread_rad", "_filling_clr")
        self.canvas.after.clear()
        self._refresh_text(start = True)
        if self.filling in self.canvas.children:
            self.canvas.remove(self.filling)
            
        self._spread_rad = 0.1
        self._filling_clr = self.filling_clr
        
    def start_anim(self):
        self.stop_anim()
        self._draw_filling()
        self._anim()

    def _anim(self):      
        self.text_event = Clock.schedule_interval(self._refresh_text,.5)
        if self.anim_mode == "fill":
            self._fill()
        else:
            self._blink()

    def _fill(self, *args):
        # Adjust filling to widget size
        if self._side in ["left","right"]:
            self.finish_rad = sqrt(self.size[0]**2 + (self.size[1]/2)**2) * 2
        else:
            self.finish_rad = sqrt(self.size[1]**2 + (self.size[0]/2)**2) * 2

        anim = Animation(_spread_rad=self.finish_rad, t="linear", duration=self.filling_duration)
        anim.bind(on_complete=self._fade_out)
        anim.start(self)

    def _fade_out(self, *args):
        anim = Animation(
            _filling_clr=self._filling_clr[:-1]+[0],
            t="out_quad",
            duration=self.fade_duration,
        )
        anim.bind(on_complete=self.anim_complete)
        anim.start(self)

    def _blink(self, *args):
        anim = Animation(
            _filling_clr=self._filling_clr,
            t="linear",
            duration=self.blink_duration,
        )
        anim += Animation(
            _filling_clr=self._filling_clr[:-1]+[0.1],
            t="linear",
            duration=self.blink_duration,
        )
        anim.repeat = True
        anim.start(self)

    def anim_complete(self, *args):
        self._side_index += 1
        if len(self.sides) <= self._side_index:
            self._side_index = 0

        self._side = self.sides[self._side_index]

        # reset to defaults
        self._spread_rad = 0.1
        self._filling_clr = self.filling_clr
        self.start_anim()

    def _draw_filling(self): 
        with self.canvas:
            if self.anim_mode == "fill":
                StencilPush(group="filling")
                self.filling = Ellipse(
                    size=(self._spread_rad, self._spread_rad),
                    pos=(
                        self._sides[self._side][0] - self._spread_rad / 2.0,
                        self._sides[self._side][1] - self._spread_rad / 2.0,
                    ),
                    group="filling",
                )

                StencilUse(group="filling")
                self.clr = Color(rgba=self._filling_clr, group="filling")
                RoundedRectangle(
                    pos=(self.pos[0],self.pos[1]),
                    size=self.size,
                    radius=self.angle_rad,
                    group="filling",
                )

                StencilUnUse(group="filling")
                Ellipse(
                    size=(self._spread_rad, self._spread_rad),
                    pos=(
                        self._sides[self._side][0] - self._spread_rad / 2.0,
                        self._sides[self._side][1] - self._spread_rad / 2.0,
                    ),
                    group="filling",
                )

                StencilPop(group="filling")
            else:
                self.clr = Color(rgba=(self._filling_clr), group="blink")
                self.filling = RoundedRectangle(
                    pos=(self.pos[0],self.pos[1]),
                    size=self.size,
                    radius=self.angle_rad,
                    group="blink",
                )           

    def _set_color(self, instance, value):
        self.clr.a = value[3]

    def _set_ellipse(self, instance, value):
        self.filling.size = (self._spread_rad, self._spread_rad)
        self.filling.pos = (
            self._sides[self._side][0] - self._spread_rad / 2.0,
            self._sides[self._side][1] - self._spread_rad / 2.0,
        )


kv = '''
#:import Label kivy.core.text.Label
RelativeLayout:
    CircularProgressBar:
        id: load_circle
        force_anim: False
        label: Label(text="{}%%", font_size=20)
        size_hint: None,None
        pos_hint: {'center_x':0.5, 'center_y':0.5}

    Button:
        text: 'Start animation'
        on_release: app.start3(self)
        size_hint: None, None
        size: (100,100)
        pos_hint: {'center_x':0.6, 'center_y':0.1}
        
    Button:
        text: 'Start loading event'
        on_release: app.start2(self)
        size_hint: None, None
        size: (100,100)
        pos_hint: {'center_x':0.4, 'center_y':0.1}

    LoadSign:
        id: load
        size_hint: None,None
        size: (150,100)
        pos_hint: {'center_x':0.15, 'center_y':0.5}
            
    Button:
        text: 'Start'
        on_release: app.start1(self)
        size_hint: None, None
        size: (100,100)
        pos_hint: {'center_x':0.15, 'center_y':0.1}
        
    LoadingBar:
        id: load_bar1
        anim_mode: 'fill'
        start_side: 'top'
        label: Label(text="Fill", font_size=20)
        size_hint: None,None
        size: (200,80)
        pos_hint: {'center_x':0.85, 'center_y':0.4}
            
    LoadingBar:
        id: load_bar2
        anim_mode: 'blink'
        label: Label(text="Blink", font_size=20)
        size_hint: None,None
        size: (200,80)
        pos_hint: {'center_x':0.85, 'center_y':0.6}
            
    Button:
        text: 'Start'
        on_release: app.start4(self)
        size_hint: None, None
        size: (100,100)
        pos_hint: {'center_x':0.85, 'center_y':0.1}
        
'''
class LoadSignApp(App):
    def build(self):
        self.r = Builder.load_string(kv)
        self.load = self.r.ids.load
        self.load_circle = self.r.ids.load_circle
        self.load_bar1 = self.r.ids.load_bar1
        self.load_bar2 = self.r.ids.load_bar2
        return self.r
    
    def start1(self,instance):
        if instance.text == 'Start':
            instance.text = 'Stop'
            self.load.start_anim()
        else:
            instance.text = 'Start'
            self.load.stop_anim()

    def start2(self, instance):
        if instance.text == 'Start loading event':
            instance.text = 'Stop loading event'
            
            def animate(*args):
                if self.load_circle.value < self.load_circle.max:
                    self.load_circle.value += 1
                else:
                    self.load_circle.value = self.load_circle.min

            self.anim = Clock.schedule_interval(animate, 0.05)

        else:
            instance.text = 'Start loading event'
            self.anim.cancel()
            self.load_circle.value = 0

    def start3(self, instance):
        if instance.text == 'Start animation':
            instance.text = 'Stop animation'
            self.load_circle.start_anim()
        else:
            instance.text = 'Start animation'
            self.load_circle.stop_anim()

    def start4(self, instance):
        if instance.text == 'Start':
            instance.text = 'Stop'
            self.load_bar1.start_anim()
            self.load_bar2.start_anim()

        else:
            instance.text = 'Start'
            self.load_bar1.stop_anim()
            self.load_bar2.stop_anim()

if __name__ == '__main__':
    LoadSignApp().run()


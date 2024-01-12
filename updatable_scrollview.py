from kivy.uix.scrollview import ScrollView
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ListProperty,
    BooleanProperty
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from math import exp


class OverscrollUpdateEffect(DampedScrollEffect):    
    def on_overscroll(self, instance_refresh_scroll_effect, overscroll):        
        if 'scroll_view' not in dir(self):
            self.scroll_view = self.target_widget.parent

        if overscroll<0 and not self.scroll_view._is_loading: # upper overscroll
            if self.scroll_view.loading_container_up and not self.scroll_view._did_overscroll_up:
                self.scroll_view.loading_container_up.move_load_sign(overscroll)
                
            if overscroll < self.min_overscroll_up:
                self.scroll_view._did_overscroll_up = True
                return True
            
            else:
                self.scroll_view._did_overscroll_up = False
                return True

        if overscroll>0 and not self.scroll_view._is_loading: # down overscroll
            if self.scroll_view.loading_container_down and not self.scroll_view._did_overscroll_down:
                self.scroll_view.loading_container_down.move_load_sign(overscroll)
                
            if overscroll > self.min_overscroll_down:
                self.scroll_view._did_overscroll_down = True
                return True
            
            else:
                self.scroll_view._did_overscroll_down = False
                return True

load_sign_container_styles = '''
<LoadSignContainer>:
    id: refresh_container_outer
    size_hint: None, None
    size: 0, 0
    StencilView:
        id: refresh_container_inner
        size_hint: None, None
  
'''
Builder.load_string(load_sign_container_styles)
class LoadSignContainer(FloatLayout):
        
    def move_load_sign(self, dy):
        # fading effect
        if self.fading_effect:
            self.load_sign.opacity = exp(8*(abs(dy/self._min_overscroll) - 1))
        # move towards visible container field
        self.load_sign.y = self._start_pos[1]+dy if abs(dy)<=abs(self._min_overscroll) else self._start_pos[1]+self._min_overscroll
    
    def hide_load_sign(self):
        if self.hide_animation:
            self.hide_animation.bind(on_complete=lambda *args: self._hide_load_sign())
            self.hide_animation.start(self.load_sign)
        else:
            self._hide_load_sign()

    def _hide_load_sign(self):
        self.load_sign.pos = self._start_pos

class LoadSignContainerUp(LoadSignContainer):
    def __init__(self, scroll_view, **kwargs):
        super(LoadSignContainerUp, self).__init__(**kwargs)
        self.fading_effect = scroll_view.fading_effect
        self._min_overscroll = scroll_view.min_overscroll_up
        hide_animation = scroll_view.hide_animation_up
        y = scroll_view.height-self.ids.refresh_container_inner.height


        self.hide_animation = hide_animation
        # set container pos and size according to scrollview
        self.ids.refresh_container_inner.size =(scroll_view.size[0],abs(self._min_overscroll))
        self.ids.refresh_container_inner.pos = (scroll_view.x,scroll_view.y+y)
        
        # set attrs of instance of load sign
        self.load_sign = scroll_view.load_sign_up
        
        self.load_sign.size_hint = (None, None)
        self.load_sign.scroll_view = scroll_view
        self.load_sign.height = abs(self._min_overscroll)
        self.load_sign.pos = (
            self.ids.refresh_container_inner.x+(scroll_view.width-self.load_sign.width)/2,
            self.ids.refresh_container_inner.y-self._min_overscroll
        )
        
        # save load sign origin
        self._start_pos = (self.load_sign.x,self.load_sign.y)
        # add load sign to container
        if self.load_sign.parent:
            self.load_sign.parent.remove_widget(self.load_sign)
            
        self.ids.refresh_container_inner.add_widget(self.load_sign)
            
class LoadSignContainerDown(LoadSignContainer):
    def __init__(self, scroll_view, **kwargs):
        super(LoadSignContainerDown, self).__init__(**kwargs)
        self.fading_effect = scroll_view.fading_effect
        self._min_overscroll = scroll_view.min_overscroll_down
        hide_animation = scroll_view.hide_animation_down
        y = 0

        self.hide_animation = hide_animation
        # set container pos and size according to scrollview
        self.ids.refresh_container_inner.size =(scroll_view.size[0],abs(self._min_overscroll))
        self.ids.refresh_container_inner.pos = (scroll_view.x,scroll_view.y+y)
        
        # set attrs of instance of load sign
        self.load_sign = scroll_view.load_sign_down
        
        self.load_sign.size_hint = (None, None)
        self.load_sign.scroll_view = scroll_view
        self.load_sign.height = abs(self._min_overscroll)
        self.load_sign.pos = (
            self.ids.refresh_container_inner.x+(scroll_view.width-self.load_sign.width)/2,
            self.ids.refresh_container_inner.y-self._min_overscroll
        )
        
        # save load sign origin
        self._start_pos = (self.load_sign.x,self.load_sign.y)
        # add load sign to container
        if self.load_sign.parent:
            self.load_sign.parent.remove_widget(self.load_sign)
            
        self.ids.refresh_container_inner.add_widget(self.load_sign)

class UpdatableScrollView(ScrollView):

    ''' Any widget class that will be you used as top load sign '''
    load_sign_up = ObjectProperty()

    ''' Any widget class that will be you used as bottom load sign '''
    load_sign_down = ObjectProperty()

    overscroll_up_callback = ListProperty()

    overscroll_down_callback = ListProperty()

    ''' For proper work you should not edit this property '''
    do_scroll_x = BooleanProperty(False)

    ''' Load sign fading effect on it move '''
    fading_effect = BooleanProperty(True)

    ''' Top minimum overscroll value to execute callback if any '''
    min_overscroll_up = NumericProperty("-100dp")

    ''' Bottom minimum overscroll value to execute callback if any '''
    min_overscroll_down = NumericProperty("100dp")

    ''' Animation of hiding top load sign '''
    hide_animation_up = ObjectProperty()

    ''' Animation of hiding bottom load sign '''
    hide_animation_down = ObjectProperty()
    
    def __init__(self, **kwargs):
        self.task_loop = asyncio.get_event_loop()
        super(UpdatableScrollView, self).__init__(**kwargs)
        self.effect_cls= OverscrollUpdateEffect
        self.effect_cls.min_overscroll_up = self.min_overscroll_up
        self.effect_cls.min_overscroll_down = self.min_overscroll_down
        self._is_loading = False
        self._did_overscroll_up = False
        self._did_overscroll_down = False
        self.loading_container_up = None
        self.loading_container_down = None
        self._origin_vp_height = 0
        self._origin_height = 0
        # on load dummy widgets
        self.w_up = Widget(size_hint_y = None, height = abs(self.min_overscroll_up))
        self.w_down = Widget(size_hint_y = None, height = abs(self.min_overscroll_down))

    def on_viewport_size(self,*args):
        ''' Hold scroll pos on viewport resize '''
        if args[1][1]< Window.size[1]:
            return
        
        if self._origin_vp_height > self._origin_height:
            delta = self.viewport_size[1] - self._origin_vp_height
            bottom = self.scroll_y * (self._origin_vp_height - self._origin_height) + delta
            scroll = bottom / (self.viewport_size[1] - self.height)
            if 1>=scroll>=0:
                self.scroll_y = scroll
            elif scroll > 1:
                self.scroll_y = 1
            elif scroll < 0:
                self.scroll_y = 0
            
        self._origin_vp_height = self.viewport_size[1]
        self._origin_height = self.height
        

    def on_parent(self, *args):
        self.__create_widgets()

    def on_size(self, *args):
        self.__create_widgets()

    def on_pos(self, *args):
        self.__create_widgets()

    def __create_widgets(self):
        if self.loading_container_up in self.parent.children:
            self.parent.remove_widget(self.loading_container_up)

        if self.load_sign_up:
            self.loading_container_up = LoadSignContainerUp(self)
            self.parent.add_widget(self.loading_container_up)

        if self.loading_container_down in self.parent.children:
            self.parent.remove_widget(self.loading_container_down)

        if self.load_sign_down:
            self.loading_container_down = LoadSignContainerDown(self)
            self.parent.add_widget(self.loading_container_down)
    
    def on_touch_up(self, *args):
        ''' Creates task if any callback specified '''
        if self._did_overscroll_up and not self._is_loading:
            if self.overscroll_up_callback:
                self.children[0].add_widget(self.w_up, index = len(self.children[0].children))
                self.task_loop.create_task(self.exec_async(self.overscroll_up_callback))
                self._is_loading = True
                
            self._did_overscroll_up = False
            #return True [Blocks touch events]
            
        elif self._did_overscroll_down and not self._is_loading:
            if self.overscroll_down_callback:
                self.children[0].add_widget(self.w_down)
                self.task_loop.create_task(self.exec_async(self.overscroll_down_callback))
                self._is_loading = True
                
            self._did_overscroll_down = False
            #return True [Blocks touch events]

        return super().on_touch_up(*args)

    async def exec_async(self, callback_with_parm):
        ''' Asynchronous callback execution goes here '''
        args = (self,) + callback_with_parm[1]
        kwargs = callback_with_parm[2]
        callback = callback_with_parm[0]
        await callback(*args, **kwargs)

        self._is_loading = False
        if callback_with_parm == self.overscroll_up_callback:
            self.children[0].remove_widget(self.w_up)
            self.loading_container_up.hide_load_sign()
        else:
            self.children[0].remove_widget(self.w_down)
            self.loading_container_down.hide_load_sign()




from kivy.clock import Clock
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from random import randint
import asyncio

class LoadSign(Label):
    
    events = []
    
    def __init__(self, **kwargs):
        super(LoadSign, self).__init__(**kwargs)
        self.t = ['Loading...','Loading..','Loading.','Loading']
        self.text = 'Loading...'
        self.start_event()

    def _update_text(self,*args):
        if 'scroll_view' not in dir(self):
            return
        if self.scroll_view._is_loading:
            self.text = self.t.pop(0)
            self.t.append(self.text)
            
        elif self.text != 'Loading...':
            self.text = 'Loading...'
    
    def stop_event(self,event):
        event.cancel()
        self.text = 'Loading...'
        
    def start_event(self):
        if len(self.events)>1:
            self.stop_event(self.events.pop(0))
        self.events.append(Clock.schedule_interval(self._update_text,.5))


styles = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '150dp'
        background_color: (1,1,1,1)
    UpdatableScrollView:
        size_hint_x: .8
        pos_hint: {'center_x':0.5}
        hide_animation_up: app.upper_anim
        hide_animation_down: app.bottom_anim
        load_sign_up: app.upper_sign
        load_sign_down: app.bottom_sign
        overscroll_up_callback: (app.refresh_callback,(),{})
        overscroll_down_callback: (app.load_more_callback,(),{'count':5})
        canvas:
            Color:
                rgb : 0,0,1
            Line:
                rectangle: (self.x,self.y,self.width,self.height)
                width:5

        GridLayout:
            id: container
            #adaptive_height: True
            size_hint_y: None
            height: self.minimum_height
            cols: 1
    BoxLayout:
        size_hint_y: None
        height: '150dp'
        background_color: (1,1,1,1)
        
    
'''

class ListElement(Label):
    count = 0
    def __init__(self, **kwargs):
        super(ListElement, self).__init__(**kwargs)
        clr = (randint(0,255)/255, randint(0,255)/255, randint(0,255)/255, 1)
        self.color = clr
        self.font_size = '20sp'
        self.size_hint_y = None
        self.height = "100dp"
        self.text = str(self.count)

    @classmethod
    def create(cls):
        cls.count += 1
        return cls

    def on_size(self,*args):
        self.update_canvas()

    def on_pos(self,*args):
        self.update_canvas()

    def update_canvas(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color, mode='rgba')
            Line(rectangle=(self.x, self.y, self.width, self.height))


class UpdatableScrollViewApp(App):
    upper_sign = ObjectProperty(LoadSign())

    bottom_sign = ObjectProperty(LoadSign())

    upper_anim = ObjectProperty(Animation(x=-200, duration=1))

    bottom_anim = ObjectProperty(Animation(x=1200, duration=1))
    
    def build(self):
        self.styles = Builder.load_string(styles)
        return self.styles
    
    def on_start(self):
        self.task = None
        self.task_loop = asyncio.get_event_loop()
        for i in range(10):
            self.styles.ids.container.add_widget(ListElement.create()())


    async def refresh_callback(self,scroll_view):
        await asyncio.sleep(2)
        self.styles.ids.container.clear_widgets()
        for i in range(10):
            self.styles.ids.container.add_widget(ListElement.create()())
            
    async def load_more_callback(self,scroll_view, count = 10):
        await asyncio.sleep(2)
        for i in range(count):
            self.styles.ids.container.add_widget(ListElement.create()())
        

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UpdatableScrollViewApp().async_run(async_lib='asyncio'))
    loop.close()

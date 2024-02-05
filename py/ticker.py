# based on https://stackoverflow.com/questions/68084971/kivy-infinite-looping-scrollview
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    DictProperty,
    NumericProperty,
    BooleanProperty,
    ObjectProperty
)
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stencilview import StencilView

class TickerElement(Label):
    def update_styles(self, data):
        ''' Set label styles '''
        
        self.data = data
        for key, value in data.items():
            setattr(self, key, value)

    def fit_size(self):
        ''' Force update to size of text '''
        
        self.texture_update()
        self.size = self.texture_size
        return self.texture_size

class TickerContainer(RelativeLayout, StencilView):
    pass

class Ticker(RelativeLayout):
    ''' Animation axis direction '''
    orientation = StringProperty('x')
    
    ''' Dictionary of elements styles '''
    data = DictProperty(None, allow_none=True)
    
    ''' Elements sizing option ignored on fit_size set to True'''
    children_width = NumericProperty(200)
    
    ''' Elements sizing option ignored on fit_size set to True'''
    children_height = NumericProperty(100)
    
    ''' Elements quantity may be ignored if force_animation set to False '''
    children_number = NumericProperty(3)
    
    ''' Creates empty space between elemets '''
    divider = NumericProperty(20)
    
    ''' If set to True fits elemets to text texture size(children width/height will be ignored) '''
    fit_size = BooleanProperty(False)
    
    ''' On False: Prevents ticker movement if size of label is smaller
    than container size. Ignores event start/stop method and children quantity on False option '''
    force_animation = BooleanProperty(False)
    
    ''' Event update time interval '''
    t = NumericProperty(1/360)
    
    ''' Elements offset on each event iteration (negatiation forces reverse animation) '''
    step = NumericProperty(2)
    
    ''' Class to fill container with '''
    labelclass = ObjectProperty(TickerElement)

    def __init__(self, **kwargs):
        self.container = TickerContainer(size_hint=(None, None),size=(0, 0))
        
        super(Ticker, self).__init__(**kwargs)

        self.add_widget(self.container)

        self._create_widgets()

    def on_pos(self, widget, value):
        """ Set position """

    def on_size(self, widget, value):
        """ Set size and fit TickerContainer class to it self """

        self.container.size = self.size
        self._create_widgets()

    def on_data(self, widget, value):
        """ Set TickerElement class style """

        self._create_widgets()

    def on_labelclass(self, widget, value):
        """ Set custom ticker elements class """
        
        self._create_widgets()

    def on_children_height(self, widget, value):
        """ Set ticker elements height """
        
        self._create_widgets()

    def on_children_width(self, widget, value):
        """ Set ticker elements width """
        
        self._create_widgets()

    def on_children_number(self, widget, value):
        """ Set ticker elements quantity """

        self._create_widgets()

    def on_fit_size(self, widget, value):
        """ Set ticker elements quantity """

        self._create_widgets()

    def on_divider(self, widget, value):
        """ Set ticker elements quantity """

        self._create_widgets()

    def _create_widgets(self):
        """ Clean and recreate container elements """
        
        if self.fit_size and self.data:
            self._create_widgets_relativly()

        self.container.clear_widgets()

        if self.data and not self.force_animation and self.size[0] > self.children_width and self.orientation == 'x':
            return self._create_widget_nonanimated()
        
        elif self.orientation == 'x':
            self.children_number = 3
            
        self._create_widgets_x() if self.orientation == 'x' else self._create_widgets_y()
        self._set_ticker_label_styles()

    def _create_widget_nonanimated(self):
        self.children_number = 1
        _tmp_entry = self.labelclass(
                size_hint=(None, None),
                width = self.children_width,
                height=self.children_height,
                pos_hint= {'center_x':0.5,'center_y':0.5},
            )
        _tmp_entry.update_styles(self.data)
        self.container.add_widget(_tmp_entry)
        
    def _create_widgets_relativly(self):
        _tmp_entry = self.labelclass(
            size_hint=(None, None),
            width = self.children_width,
            height=self.children_height
        )
        _tmp_entry.update_styles(self.data)
        self.children_width, self.children_height = _tmp_entry.fit_size()
        
    def _create_widgets_y(self):
        for entry in range(self.children_number):
            _tmp_entry = self.labelclass(
                size_hint=(None, None),
                width = self.children_width,
                height=self.children_height,
                pos_hint= {'center_x':0.5},
                pos=(0, 10 + (self.children_height + self.divider) * entry )
            )

            self.container.add_widget(_tmp_entry)
        
    def _create_widgets_x(self):
        for entry in range(self.children_number):
            _tmp_entry = self.labelclass(
                size_hint=(None, None),
                width = self.children_width,
                height=self.children_height,
                pos_hint= {'center_y':0.5},
                pos=(10 + (self.children_width + self.divider) * entry, 0)
            )

            self.container.add_widget(_tmp_entry)

    def _set_ticker_label_styles(self):
        ''' Set styles if any '''

        if not self.data:
            return

        for child in self.container.children:
            child.update_styles(self.data)

    def scroll_x(self, delta_x):
        _highest, _lowest = self.container.children[0], self.container.children[0]

        for child in self.container.children:
            child.x += delta_x
            _highest = child if child.x > _highest.x else _highest
            _lowest = child if child.x < _lowest.x else _lowest

        if _highest.x > self.width + _highest.width:
            _highest.x = _lowest.x - (_highest.width + self.divider)

        elif _lowest.x < 0 - _lowest.width - _lowest.width:
            _lowest.x = _highest.x + (_highest.width + self.divider)
   
    def scroll_y(self, delta_y):
        _highest, _lowest = self.container.children[0], self.container.children[0]

        for child in self.container.children:
            child.y += delta_y
            _highest = child if child.y > _highest.y else _highest
            _lowest = child if child.y < _lowest.y else _lowest

        if _highest.y > self.height + _highest.height:
            _highest.y = _lowest.y - (_highest.height + self.divider)

        elif _lowest.y < 0 - _lowest.height - _lowest.height:
            _lowest.y = _highest.y + (_highest.height + self.divider)

    def _animation(self, *args):
        if self.orientation == 'x':
            self.scroll_x(self.step)
            
        else:
            self.scroll_y(self.step)
            
    def start_animation(self, step = None, t = None):
        if step:
            self.step = step
            
        if t:
            self.t = t

        if self.children_number > 1:
            self.tickerEvent = Clock.schedule_interval(self._animation,self.t)
        
    def stop_animation(self):
        if self.children_number > 1 and 'tickerEvent' in dir(self):
            self.tickerEvent.cancel()

styles = ("""           
<TickerContainer>:
    canvas:
        Color:
            rgb : 0,0,1
        Line:
            rectangle: (0+1,0+1,self.width - 1,self.height -1 )
            width:5
""")

class TickerApp(App):
    def build(self):
        root = GridLayout(cols=2)

        self.ticker1 = Ticker(
            fit_size = True,
            size=(200,200), 
            orientation = 'x'
        )
        self.ticker1.data = {'text': "Very very very very very very very very long text", 'font_size':'20sp'}     
        
        self.ticker2 = Ticker(
            fit_size = True,
            size=(200,200),
            data = {'text': "Y axis orientation", 'font_size':'20sp'},
            orientation = 'y', children_number= 8
        )

        self.ticker3 = Ticker(
            fit_size = True,
            size=(200,200), 
            orientation = 'x',
            children_number= 8
        )
        self.ticker3.data = {'text': "force_animation set to False\n<I am not out of bounds!!!>", 'font_size':'30sp', 'color': (1,0,0,1)}     

        self.ticker4 = Ticker(
            fit_size = True,
            size=(200,200), 
            orientation = 'x',
            force_animation = True,
            children_number= 5,
            divider = 100
        )
        self.ticker4.data = {'text': "force_animation set to True", 'font_size':'20sp'}

        root.add_widget(self.ticker1)
        root.add_widget(self.ticker2)
        root.add_widget(self.ticker3)
        root.add_widget(self.ticker4)
        

        self.ticker1.start_animation(-2)
        self.ticker2.start_animation()
        self.ticker3.start_animation(step = 20)
        self.ticker4.start_animation(step = 1, t = 1/60)
        return root
           
if __name__ == "__main__":
    Builder.load_string(styles)
    TickerApp().run()

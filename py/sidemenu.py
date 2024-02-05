from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
class SideMenu(MDNavigationDrawer):
    ''' Child widgets list ignoring bubbling when swipe is triggered
    (default: prevents unexpected button clicks).
    Swipe priority is higher than priority of interaction with listed widgets. '''
    low_priority = ListProperty((Button,ScrollView))
    
    def _event_priority(self, touch):
        widgets = touch.grab_list
        if widgets:
            for widget in widgets:
                if isinstance(widget(),(*self.low_priority,)):
                    touch.ungrab(widget())

    def on_touch_down(self, touch):
        if (self.disabled or not self.collide_point(*touch.pos) or not self.children):
            return False
        
    def on_touch_move(self, touch):
        print(touch.grab_list)
        self._event_priority(touch)
        return super().on_touch_move(touch)
    

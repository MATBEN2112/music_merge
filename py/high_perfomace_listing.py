from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label

kv = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        text: 'add'
        on_release: app.add_new_widget()
    ScrollView:
        id: scroll
        BoxLayout:
            id: box
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
'''

class TestApp(App):
    def build(self):
        self.count = 0
        return Builder.load_string(kv)

    def add_new_widget(self):
        vp_height = self.root.ids.scroll.viewport_size[1]
        sv_height = self.root.ids.scroll.height

        # add a new widget (must have preset height)
        label = Label(text='Widget #' + str(self.count), size_hint=(1, None), height=50)
        self.root.ids.box.add_widget(label)
        self.count += 1

        if vp_height > sv_height:  # otherwise there is no scrolling
            # calculate y value of bottom of scrollview in the viewport
            scroll = self.root.ids.scroll.scroll_y
            bottom = scroll * (vp_height - sv_height)

            # use Clock.schedule_once because we need updated viewport height
            # this assumes that new widgets are added at the bottom
            # so the current bottom must increase by the widget height to maintain position
            Clock.schedule_once(partial(self.adjust_scroll, bottom+label.height), -1)

    def adjust_scroll(self, bottom, dt):
        vp_height = self.root.ids.scroll.viewport_size[1]
        sv_height = self.root.ids.scroll.height
        self.root.ids.scroll.scroll_y = bottom / (vp_height - sv_height)

TestApp().run()

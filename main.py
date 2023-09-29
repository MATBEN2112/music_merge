from kivy.core.audio import SoundLoader

import kivy

from kivy.app import App
from kivy.uix.button import Button


class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        return Button(text='hello world', on_release=self.play_a)
    def play_a(self, o):
        self.sound = SoundLoader.load('1.mp3')
        print(self.sound)
        print(dir(self.sound))
        self.sound.play()
        


if __name__ == '__main__':
    TestApp().run()

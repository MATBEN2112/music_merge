from kivy.core.audio import SoundLoader

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.button import Button
from ffpyplayer.player import MediaPlayer


class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        return Button(text='hello world', on_release=self.play_a)
    def play_a(self, o):
        self.sound = SoundLoader('seg.ts')
        self.sound.play()
        #print(self.sound.extensions)
        print(dir(self.sound))
        


if __name__ == '__main__':
    TestApp().run()

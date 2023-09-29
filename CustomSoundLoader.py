from kivy.core.audio import SoundLoader

import kivy

from kivy.app import App
from kivy.uix.button import Button


class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        return Button(text='hello world', on_release=self.play_a)
    def play_a(self, o):
        sound = SoundLoader.load('file_example_MP3_1MG.mp3')
        sound.play()
        


if __name__ == '__main__':
    TestApp().run()

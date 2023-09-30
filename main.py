import kivy
from kivymd.uix.boxlayout import MDBoxLayout
#kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.button import Button
from ffpyplayer.player import MediaPlayer

from kivy.uix.videoplayer import VideoPlayer

class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        w = MDBoxLayout()
        w.add_widget(Button(text='mp3', on_release=self.play_mp3))
        w.add_widget(Button(text='ts', on_release=self.play_ts))
        w.add_widget(Button(text='m4a', on_release=self.play_m4a))
        return w
    def play_mp3(self, o):

        self.sound = MediaPlayer('1.mp3')

    def play_ts(self, o):
        self.sound = MediaPlayer('1.ts')

    def play_m4a(self, o):

        self.sound = MediaPlayer('1.m4a')


if __name__ == '__main__':
    TestApp().run()

import kivy
from kivymd.uix.boxlayout import MDBoxLayout
#kivy.require('1.0.7')
from kivy.core.audio import SoundLoader
from kivy.app import App
from kivy.uix.button import Button
from ffpyplayer.player import MediaPlayer

from kivy.uix.videoplayer import VideoPlayer
import os
from kivy.core.audio import Sound, SoundLoader
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE

load_framework(INCLUDE.AVFoundation)
AVAudioPlayer = autoclass("AVAudioPlayer")
NSURL = autoclass("NSURL")
NSString = autoclass("NSString")


class SoundAvplayer(Sound):
    @staticmethod
    def extensions():
        # taken from https://goo.gl/015kvU
        return ("aac", "adts", "aif", "aiff", "aifc", "caf", "mp3", "mp4",
                "m4a", "snd", "au", "sd2", "wav")

    def __init__(self, **kwargs):
        self._avplayer = None
        super(SoundAvplayer, self).__init__(**kwargs)

    def load(self):
        self.unload()
        fn = NSString.alloc().initWithUTF8String_(self.source)
        url = NSURL.alloc().initFileURLWithPath_(fn)
        self._avplayer = AVAudioPlayer.alloc().initWithContentsOfURL_error_(
            url, None)

    def unload(self):
        self.stop()
        self._avplayer = None

    def play(self):
        if not self._avplayer:
            return
        self._avplayer.play()
        super(SoundAvplayer, self).play()

    def stop(self):
        if not self._avplayer:
            return
        self._avplayer.stop()
        super(SoundAvplayer, self).stop()

    def seek(self, position):
        if not self._avplayer:
            return
        self._avplayer.playAtTime_(float(position))

    def get_pos(self):
        if self._avplayer:
            return self._avplayer.currentTime
        return super(SoundAvplayer, self).get_pos()

    def on_volume(self, instance, volume):
        if self._avplayer:
            self._avplayer.volume = float(volume)

    def _get_length(self):
        if self._avplayer:
            return self._avplayer.duration
        return super(SoundAvplayer, self)._get_length()
    

class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        w = MDBoxLayout()
        w.add_widget(Button(text='mp3', on_release=self.play_mp3))
        w.add_widget(Button(text='ts', on_release=self.play_ts))
        w.add_widget(Button(text='m4a', on_release=self.play_m4a))
        return w
    def play_mp3(self, o):
        self.sound = SoundAvplayer().load('1.m4a')
        self.sound.play()

    def play_ts(self, o):
        self.sound = SoundAvplayer().load('1.m4a')
        self.sound.play()
    def play_m4a(self, o):

        self.sound = SoundAvplayer().load('1.m4a')
        self.sound.play()



if __name__ == '__main__':
    TestApp().run()




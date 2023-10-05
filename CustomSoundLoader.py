import os
import pyobjus
from kivy.core.audio import Sound
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE


NSString = autoclass('NSString')


class IOSPlayer(Sound):
    def __init__(self, source, author='author', song='song'):
        IOS_player = autoclass('IOS_player')
        print(IOS_player.alloc())
        self.author = NSString.alloc().initWithUTF8String_(author)
        self.song = NSString.alloc().initWithUTF8String_(song)
        self.fn = NSString.alloc().initWithUTF8String_(source)
        self.player = IOS_player.alloc().initWithFn(self.fn,self.author,self.fn)
        self.player.load()

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def seek(self, position):
        t = pyobjus.objc_d(postion) # represent double
        try:
            print(t.numberWithFloat)
        except Exception as e:
            print(e)
        self.player.seek(t)

    def get_pos(self):
        return self.player.get_pos(t)

    def get_length(self):
        return self.player.get_len(t)
    

class TestApp(App):

    def build(self):
        # return a Button() as a root widget
        w = MDBoxLayout()
        w.add_widget(Button(text='mp3', on_release=self.play_mp3))
        w.add_widget(Button(text='ts', on_release=self.play_ts))
        w.add_widget(Button(text='m4a', on_release=self.play_m4a))
        return w
    def play_mp3(self, o):
        self.sound = SoundAvplayer.load('1.m4a')
        self.sound.play()

    def play_ts(self, o):
        self.sound = SoundAvplayer.load('1.m4a')
        self.sound.play()
    def play_m4a(self, o):

        self.sound = SoundAvplayer.load('1.m4a')
        self.sound.play()



if __name__ == '__main__':
    TestApp().run()




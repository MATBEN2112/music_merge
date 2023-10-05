import os
import pyobjus
from kivy.core.audio import Sound
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE


NSString = autoclass('NSString')


class IOSPlayer(Sound):
    def __init__(self, source, author='author', song='song'):
        IOS_player = autoclass('IOS_player')
        print(dir(IOS_player.alloc()))
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
    def test(self):
        self.player.test_func()
    

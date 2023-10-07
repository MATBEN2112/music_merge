import os
import pyobjus
from kivy.core.audio import Sound
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE


NSString = autoclass('NSString')


class IOSPlayer(Sound):
    def __init__(self, source, author='author', song='song'):
        IOS_player = autoclass('IOS_player')
        #print(dir(IOS_player.alloc()))
        self.author = NSString.alloc().initWithUTF8String_(author)
        self.song = NSString.alloc().initWithUTF8String_(song)
        self.fn = NSString.alloc().initWithUTF8String_(source)
        self.player = IOS_player.alloc().initWithFn_author_song_(self.fn,self.author,self.song)
        self.player.load()
        self.lenght = int(self.get_length())

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def seek(self, position):
        t = pyobjus.objc_d(position) # represent double
        print(t)
        self.player.seek_(t)

    def get_pos(self):
        return self.player.get_pos()

    def get_length(self):
        lenght = self.player.get_len()
        print('Song total lenght')
        print(lenght)
        print(type(lenght))
        print(int(lenght))
        return lenght
    def test(self):
        self.player.test_func()
    

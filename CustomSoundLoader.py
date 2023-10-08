import os
import pyobjus
from kivy.core.audio import Sound
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE
from pyobjus import objc_arr, objc_str

NSMutableArray = autoclass("NSMutableArray")
NSString = autoclass('NSString')


class IOSPlayer(Sound):
    def __init__(self):
        self.IOS_player = autoclass('IOS_player')
        self.player = self.IOS_player.alloc().init()
        
    def load_playlist(self, track_list, key):
        track_arr = NSMutableArray.arrayWithCapacity_(len(track_list))
        for track in track_list:
            img = NSString.alloc().initWithUTF8String_(track[4])
            author = NSString.alloc().initWithUTF8String_(track[2])
            song = NSString.alloc().initWithUTF8String_(track[3])
            fn = NSString.alloc().initWithUTF8String_(track[1])
            track_arr.addObject_(objc_arr(track[0], fn, author, song, img))
            
        self.player.loadPlaylist_key_(track_arr,key)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()
        
    def stop(self):
        self.player.stop()

    def seek(self, position):
        self.player.seek_(position)

    def get_pos(self):
        return self.player.get_pos()

    def get_length(self):
        return self.player.get_len()
        
    def get_info(self):
        info_dict = self.player.get_info()
        key = info_dict.objectForKey_(objc_str('key')).intValue()
        author = info_dict.objectForKey_(objc_str('author')).UTF8String()
        song = info_dict.objectForKey_(objc_str('song')).UTF8String()
        file = info_dict.objectForKey_(objc_str('file')).UTF8String()
        img = info_dict.objectForKey_(objc_str('img')).UTF8String()
        song_len = info_dict.objectForKey_(objc_str('len')).floatValue()
        song_pos = info_dict.objectForKey_(objc_str('pos')).floatValue()
        status = info_dict.objectForKey_(objc_str('status')).boolValue()
        info_dict = {'key':key, 'author':author, 'song':song, 'file':file, 'img':img, 'song_len':song_len, 'song_pos':song_pos,'status':status}
        print(info_dict)
        return info_dict

    def test(self):
        self.player.test_func()
    

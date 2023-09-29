from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, OptionProperty, BooleanProperty
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE
load_framework(INCLUDE.AVFoundation)
AVAudioPlayer = autoclass("AVAudioPlayer")
NSURL = autoclass("NSURL")
NSString = autoclass("NSString")
class SoundLoader(EventDispatcher):
    source = StringProperty("")

    volume = NumericProperty(1.)

    state = OptionProperty('pause', options=('stop', 'play', 'pause'))

    loop = BooleanProperty(False)
    _avplayer = None

    def __init__(self, *args,**kwargs):
        super(SoundLoader, self).__init__(**kwargs)
        self.state = 'pause'
        self.register_event_type('on_play')
        self.register_event_type('on_stop')
        self.register_event_type('on_pause')
        self.register_event_type('on_finish')

    def play(self):
        self.state = 'play'
        self._avplayer.prepareToPlay()
        self._avplayer.play()
        self.dispatch('on_play')

    def stop(self):
        if not self._avplayer:
            return
        print ("Trying to stop file: {}".format(self.source))
        self.state = 'stop'
        self._avplayer.stop()
        self.dispatch('on_stop')

    def pause(self):
        self.state = 'pause'
        self.stop()
        self.dispatch('on_pause')

    def load(self, filename):
        self.unload()
        fn = NSString.alloc().initWithUTF8String_(filename)
        url = NSURL.alloc().initFileURLWithPath_(fn)
        self._avplayer = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)

    def unload(self):
        self.stop()
        self._avplayer = None

    def _get_length(self):
        self.length = self._avplayer.duration
        return self.length

    def get_pos(self, dt=1):
        if self._avplayer.isPlaying():
            self.currentPos = self._avplayer.currentTime
        return self.currentPos

    def seek(self, position):
        if not self._avplayer:
            return
        self._avplayer.playAtTime_(float(position))

    def on_play(self):
        print("Playing")
        self.state = "play"

    def on_stop(self):
        print("Stopping")
        self.state = "stop"

    def on_pause(self):
        print("pausing")
        self.state = "pause"

    def on_finish(self):
        print("Finishing!")
        # self.stop()
if __name__ == '__main__':
    test = SoundLoader()
    test.load("./1.mp3")
    test.play()
    while True:
        test.get_pos()

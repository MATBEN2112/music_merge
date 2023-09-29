from kivy.core.audio import SoundLoader

sound = SoundLoader.load('1.mp3')
if sound:
    print("Sound found at %s" % sound.source)
    print("Sound is %.3f seconds" % sound.length)
    sound.play()

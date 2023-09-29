from kivy.core.audio import SoundLoader

sound = SoundLoader.load('1.mp3')
if sound:
    print("Sound found at %s" % sound.source)
    print("Sound is %.3f seconds" % sound.length)
    sound.play()
sound = SoundLoader.load('file_example_MP3_1MG.mp3')
if sound:
    print("Sound found at %s" % sound.source)
    print("Sound is %.3f seconds" % sound.length)
    sound.play()

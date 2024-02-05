# based on https://github.com/kengoon/KivyGradient
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics.texture import Texture
import numpy as np
from math import cos, sin, pi

kv = """
#:import Gradient gradient.Gradient
RelativeLayout:
    BoxLayout
        id: box

        canvas:
            Rectangle:
                id: rect
                size: self.size
                pos: self.pos
                texture: Gradient.gradient(((0,0,1,1),(0,1,0,1)))

    Slider:
        id: slider
        pos_hint: {'center_x':0.5, 'center_y':0.5}
        min: 0
        max: 90

    Label:
        pos_hint: {'center_x':0.05, 'center_y':0.45}
        text:  '0°'
        font_size: '20sp'

    Label:
        pos_hint: {'center_x':0.95, 'center_y':0.45}
        text:  '90°'
        font_size: '20sp'

    Label:
        id: angle
        pos_hint: {'center_x':0.5, 'center_y':0.45}
        text:  'angle=0°'
        font_size: '20sp'

"""
class Gradient(object):
    @staticmethod
    def gradient(clr = ((0,0,0,1),(1,1,1,1)), angle = 0, size = (10,10)):
        clr1 = np.array(clr[0])
        #clr2 = np.array(clr[1])
        
        # angle to rad
        angle = angle/360 * 2*pi
        
        # count gradient direction vector and it's axis projections
        gradient_vector =[(i[1]-i[0]) for i in zip(*clr)]
        delta_x = np.array([i*cos(angle)/(size[0]-1) for i in gradient_vector])
        delta_y = np.array([i*sin(angle)/(size[1]-1) for i in gradient_vector])

        # create list of pixels
        byte_buffer = []
        for i in range(size[0]):
            for j in range(size[1]):
                pixel = (clr1+delta_x*j + delta_y*i)*255
                byte_buffer += [int(i) if 0 <= i <= 255 else 255 if i > 255 else 0 for i in pixel]

        # create texture
        texture = Texture.create(size=size, colorfmt='rgba')
        texture.blit_buffer(bytes(byte_buffer), colorfmt='rgba', bufferfmt='ubyte')
        return texture     

class GradientApp(App):
    def build(self):
        self.r = Builder.load_string(kv)
        return self.r
    
    def on_start(self):
        self.r.ids.slider.bind(value=self.rotate)

    def rotate(self,*args):
        self.r.ids.box.canvas.children[1].texture = Gradient.gradient(((0,0,1,1),(0,1,0,1)),angle = args[1])
        self.r.ids.angle.text = f'angle={int(args[1])}°'

if __name__ == '__main__':
    GradientApp().run()

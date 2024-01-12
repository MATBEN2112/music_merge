from kivymd.uix.label import MDLabel
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.widget import Widget

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.uix.button import MDIconButton

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle, Line
import csv
import re
 
class DropDownElement(MDRelativeLayout):
    def __init__(self, dd, q):
        super(DropDownElement, self).__init__()
        self.size_hint_y = None
        self.height="50dp"

        label = MDLabel(
            text= q,
            size_hint_y= None,
            height="50dp",
            font_size= '28sp',
            markup=True,
            halign='left',
            padding= [30,0,0,0]
        )
        self.add_widget(label)
        btn = Button(
            background_color=dd.screen.app.btn_hitbox_clr,
            size_hint_y=None,
            height="50dp",
            text= q,
            opacity= 0
        )
        btn.bind(on_release=dd.select_resent)
        self.add_widget(btn)


class DropDownResent(DropDown):
    def __init__(self, screen, achor_widget, q):
        super(DropDownResent, self).__init__()
        self.auto_width = False
        #self.auto_dismiss = False
        self.width = screen.width
        self.global_mode = screen.global_mode
        self.resent_path = screen.app.app_dir
            
        self.q = q
        self.achor_widget = achor_widget
        self.screen = screen

        self.dd_layout = MDBoxLayout(
            md_bg_color = self.screen.app.secondary_clr1,
            orientation = "vertical",
            size_hint_y=None,
            height="550dp",      
        )
        self._create_resent_list()
        self.open(self.achor_widget)



    def _create_resent_list(self):
        self.dd_layout.clear_widgets()
        self.resent = []
        count = 0
        q = ''
        for i in self.q:# escape re meta symbols
            q += f'[{i}]'

        q_regexp = re.compile(rf'(.*){q}(.*)', re.IGNORECASE)
        self._create_header()
        with open(self.resent_path + '/resent.csv', newline='') as f:
            reader = csv.reader(f, delimiter=' ', quotechar='|')
            for row in reversed(list(reader)):
                self.resent.append(row[0])
                s = q_regexp.search(row[0])
                if s and count<9:
                    element = DropDownElement(self, row[0])
                    self.dd_layout.add_widget(element)
                    count += 1

        if count:
            self.dd_layout.add_widget(Widget())
            self._create_ending()

            self.add_widget(self.dd_layout)      
        
    def _create_header(self):
        resent_header = MDBoxLayout(
            md_bg_color = self.screen.app.secondary_clr2,
            size_hint_y=None,
            height="50dp"
        )

        label = MDLabel(
            text='Resent',
            font_size = '30sp',
            padding = [20,0,0,0]
        )
        resent_header.add_widget(label)
        clean_btn_box = MDRelativeLayout(size_hint=(None,1), width="150dp",height="50dp")
        label = MDLabel(
            text='[color=ff3333]Clean resent[/color]',
            markup = True,
            font_size = '30sp',
            padding = [0,0,20,0],
            halign= "right"
        )
        clean_btn_box.add_widget(label)
        btn = Button(background_color=self.screen.app.btn_hitbox_clr, size_hint_y=None, height="50dp")
        btn.bind(on_release=self.clean_resent)
        clean_btn_box.add_widget(btn)
        resent_header.add_widget(clean_btn_box)
            
        self.dd_layout.add_widget(resent_header)
        
    def _create_ending(self):
        resent_ending = MDBoxLayout(
            md_bg_color = self.screen.app.secondary_clr2,
            size_hint_y=None,
            height="50dp"
        )

        btn = Button(
            text='[color=0099FF]Global search[/color]' if self.screen.global_mode else '[color=0099FF]Local search[/color]',
            markup = True,
            font_size = '30sp',
            background_color=self.screen.app.btn_hitbox_clr,
            size_hint_y=None,
            height="50dp"
        )
        btn.bind(on_release=self.screen.switch_search)
        resent_ending.add_widget(btn)
        self.dd_layout.add_widget(resent_ending)
            
    def select_resent(self, obj):
        self.screen.ids.search_input.text = obj.text
        self.screen.search(obj.text)
        
    def clean_resent(self,o):
        with open(self.resent_path + '/resent.csv', 'w', newline='') as _:
            pass
        self.dismiss()

    def search(self, q):
        self.dismiss()
        # save search query to search history
        if not q:
            return
        
        if q not in self.resent:
            with open(self.screen.app.app_dir + '/resent.csv', 'a', newline='') as f:
                writer = csv.writer(f, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([q])
        else:
            self.resent.remove(q)
            self.resent.append(q)
            with open(self.screen.app.app_dir + '/resent.csv', 'w', newline='') as f:
                writer = csv.writer(f, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in self.resent:
                    writer.writerow([row])

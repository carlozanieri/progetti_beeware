import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

class ResponsiveApp(toga.App):
    def startup(self):
        # Contenitore principale
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

        # Intestazione responsive
        header_label = toga.Label(
            "Benvenuto su BeeWare", 
            style=Pack(padding=(20, 0), font_size=24, text_align=CENTER)
        )
        
        # Sotto-contenitore con elementi affiancati che si espandono
        content_box = toga.Box(style=Pack(direction=ROW, padding=10, flex=1))
        
        # Widget interni
        button1 = toga.Button("Bottone 1", style=Pack(flex=1, padding=5))
        button2 = toga.Button("Bottone 2", style=Pack(flex=1, padding=5))
        
        content_box.add(button1)
        content_box.add(button2)

        main_box.add(header_label)
        main_box.add(content_box)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 600))
        self.main_window.content = main_box
        self.main_window.show()


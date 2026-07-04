"""Pagina dettaglio slide"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN


class DettaglioSliderPage:
    """Pagina che mostra il dettaglio di una slide"""

    def __init__(self, app):
        self.app = app
        self.box = None

    def build(self):
        """Costruisce la pagina dettaglio"""
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Pulsante indietro
        btn_indietro = toga.Button(
            "← Indietro",
            on_press=self.close,
            style=Pack(margin=5, background_color="#043a55", color="white", width=200, margin_left=50)
        )
        self.box.add(btn_indietro)

        # Contenuto scrollabile (immagine + titolo + testo)
        scroll_content = toga.Box(style=Pack(direction=COLUMN))

        # Immagine
        self.detail_image = toga.ImageView(style=Pack(height=300, margin=10))
        scroll_content.add(self.detail_image)

        # Titolo
        self.detail_titolo = toga.Label(
            "",
            style=Pack(font_size=22, font_weight="bold", margin=15)
        )
        scroll_content.add(self.detail_titolo)

        # Testo in area scrollabile e sola lettura
        self.detail_testo = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, margin=15, margin_top=0, font_size=16, height=300)
        )
        scroll_content.add(self.detail_testo)

        # Scroll container che contiene tutto
        testo_scroll = toga.ScrollContainer(
            content=scroll_content,
            vertical=True,
            horizontal=False,
            style=Pack(flex=1)
        )
        self.box.add(testo_scroll)
        # Pulsante indietro
        btn_indietro = toga.Button(
            "← Indietro",
            on_press=self.close,
            style=Pack(margin=10, background_color="#043a55", color="white", width=200, margin_left=50)
        )
        self.box.add(btn_indietro)
        return self.box
        
    def show(self, slide, img):
        """Popola e mostra la pagina di dettaglio"""
        self.detail_image.image = img
        self.detail_titolo.text = slide.get("titolo", "")
        self.detail_testo.value = slide.get("testo", slide.get("caption", ""))
        self.app.main_window.content = self.box

    def close(self, widget=None):
        """Torna alla home"""
        self.app.main_window.content = self.app.root_box
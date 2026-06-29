"""Pagina Prenotazioni"""

import webbrowser
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class PrenotazioniPage:
    """Pagina con contatti telefonici ed email"""

    def __init__(self, app):
        self.app = app
        self.box = None

    def build(self):
        """Costruisce la pagina"""
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color="#000000"))

        maniglia = toga.Box(style=Pack(width=55, height=6, background_color="#404040", margin_top=10, margin_bottom=20))
        maniglia_container = toga.Box(style=Pack(direction=ROW, alignment="center"))
        maniglia_container.add(maniglia)
        self.box.add(maniglia_container)

        self.box.add(toga.Label(
            "Prenotazioni CasaBaldini",
            style=Pack(font_size=22, font_weight="bold", color="white", margin_bottom=10)
        ))

        self._add_contact("Chiamaci", "+39 320 7060411", "tel:+393207060411")
        self._add_contact("Chiamaci tel. fisso", "+39 055 2741209", "tel:+390552741209")
        self._add_contact(
            "Inviaci una mail",
            "carlo.zanieri@gmail.com",
            "mailto:carlo.zanieri@gmail.com?subject=Richiesta informazioni CasaBaldini"
        )

        self.box.add(toga.Label(
            "Le prenotazioni sono soggette a disponibilità. "
            "Contattaci direttamente per ricevere la migliore offerta garantita.",
            style=Pack(font_style="italic", color="#b3b3b3", font_size=13, margin=20)
        ))

        btn_chiudi = toga.Button(
            "CHIUDI",
            on_press=self.close,
            style=Pack(margin=10, background_color="#1a1a1a", color="white", flex=1)
        )
        self.box.add(btn_chiudi)

        return self.box

    def _add_contact(self, titolo, sottotitolo, url):
        """Aggiunge un contatto cliccabile"""
        contatto_box = toga.Box(style=Pack(direction=ROW, margin=10))

        testi_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        testi_box.add(toga.Label(titolo, style=Pack(font_weight="bold", color="white", font_size=14)))
        testi_box.add(toga.Label(sottotitolo, style=Pack(color="#b3b3b3", font_size=12)))
        contatto_box.add(testi_box)

        btn = toga.Button(
            "›",
            on_press=lambda w, u=url: webbrowser.open(u),
            style=Pack(width=40, background_color="#1a1a1a", color="white")
        )
        contatto_box.add(btn)

        self.box.add(contatto_box)

    async def open(self):
        """Apre la pagina"""
        self.app.main_window.content = self.box

    def close(self, widget=None):
        """Torna alla home"""
        self.app.main_window.content = self.app.root_box
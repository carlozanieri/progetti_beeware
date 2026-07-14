"""
CasaBaldini - App Toga
"""

import asyncio
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .slider import SliderManager
from .links import LinksManager
from .menu import MenuManager
from .pages.dovemangiare import DoveMangiarePage
from .pages.prenotazioni import PrenotazioniPage
from .pages.dettaglio_slider import DettaglioSliderPage
from .pages.home_page import HomePage


class CasaBaldiniApp(toga.App):
    def startup(self):
        self.menu_aperto = False

        # --- Contenuto principale ---
        self.root_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Navbar
        navbar = toga.Box(style=Pack(direction=ROW, background_color="#043a55", padding=8))
        btn_hamburger = toga.Button(
            "☰",
            style=Pack(width=40, height=40, background_color="#043a55", color="white", font_size=18)
        )
        self.titolo_navbar = toga.Label(
            "CasaBaldini",
            style=Pack(flex=1, font_size=18, font_weight="bold", color="white", margin_left=10)
        )
        navbar.add(btn_hamburger)
        navbar.add(self.titolo_navbar)

        # Status label per caricamento
        self.status_label = toga.Label(
            "Caricamento...",
            style=Pack(font_size=12, color="orange", margin=10)
        )

        # ImageView per lo slider
        self.image_view = toga.ImageView(style=Pack(flex=1, height=250))
        self.titolo_label = toga.Label(
            "", style=Pack(font_size=15, font_weight="bold", margin_top=8, margin_left=10)
        )
        self.caption_label = toga.Label(
            "", style=Pack(font_size=12, color="#555555", margin_left=10, margin_bottom=8)
        )

        # Slider manager (creato una volta sola, con callback)
        self.slider_manager = SliderManager(
            self.image_view, self.titolo_label, self.caption_label, self.status_label,
            on_image_click=self._mostra_dettaglio_slide
        )
        nav_row = self.slider_manager.build_controls()

        # Links manager
        self.links_manager = LinksManager()
        links_scroll = self.links_manager.build()

        # Assembla root_box
        self.root_box.add(navbar)
        self.root_box.add(self.status_label)
        self.root_box.add(self.image_view)
        self.root_box.add(self.titolo_label)
        self.root_box.add(self.caption_label)
        self.root_box.add(nav_row)
        self.root_box.add(links_scroll)

        # Menu manager
        self.menu_manager = MenuManager(self)
        self.menu_overlay = self.menu_manager.build_overlay()
        btn_hamburger.on_press = self.menu_manager.toggle

        # Pages
        self.dovemangiare_page = DoveMangiarePage(self)
        self.dovemangiare_page.build()

        self.prenotazioni_page = PrenotazioniPage(self)
        self.prenotazioni_page.build()

        self.dettaglio_page = DettaglioSliderPage(self)
        self.dettaglio_page.build()

        # Finestra principale
        self.main_window = toga.MainWindow(title="CasaBaldini")
        self.main_window.content = self.root_box
        self.main_window.show()

        self.home_page_view = HomePage(self)
        self.home_page_view.build()
        asyncio.create_task(self._inizializza())

    async def _inizializza(self):
        """Carica tutti i dati iniziali"""
        await self.menu_manager.load_data()
        await self.slider_manager.load("index")
        await self.links_manager.load()

    def _mostra_dettaglio_slide(self, slide, img):
        """Apre la pagina di dettaglio per la slide corrente"""
        self.dettaglio_page.show(slide, img)


def main():
    return CasaBaldiniApp()
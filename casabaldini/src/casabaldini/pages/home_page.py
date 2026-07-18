"""Pagina Home statica con logo e immagine"""

import asyncio
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..api import IMG_BASE


class HomePage:
    """Pagina Home con logo e immagine principale"""

    def __init__(self, app):
        self.app = app
        self.box = None
        self.logo_view = None
        self.header_view = None

    def build(self):
        """Costruisce la pagina Home"""
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color="#000000"))

        # Navbar
        navbar = toga.Box(style=Pack(direction=ROW, background_color="#043a55", padding=8))
        btn_hamburger = toga.Button(
            "☰",
            on_press=self.app.menu_manager.toggle,
            style=Pack(width=40, height=40, background_color="#043a55", color="white", font_size=18)
        )
        titolo_navbar = toga.Label(
            "CasaBaldini",
            style=Pack(flex=1, font_size=18, font_weight="bold", color="white", margin_left=10)
        )
        navbar.add(btn_hamburger)
        navbar.add(titolo_navbar)
        self.box.add(navbar)

        # Contenuto scrollabile
        scroll_content = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Logo — occupa tutta la larghezza, altezza fissa
        self.logo_view = toga.ImageView(
            style=Pack(flex=1, height=150)
        )
        scroll_content.add(self.logo_view)

        # Immagine principale — occupa tutta la larghezza, altezza fissa
        self.header_view = toga.ImageView(
            style=Pack(flex=1, height=300)
        )
        scroll_content.add(self.header_view)

        # Testi — occupano tutta la larghezza
        scroll_content.add(toga.Label(
            "Benvenuti a CasaBaldini",
            style=Pack(font_size=22, font_weight="bold", color="white",
                       margin_top=15, margin_left=10, margin_right=10, text_align="center")
        ))
        scroll_content.add(toga.Label(
            "Barberino di Mugello, a pochi km. da Firenze",
            style=Pack(font_size=15, color="#cccccc",
                       margin_top=5, margin_left=10, margin_right=10, text_align="center")
        ))
        scroll_content.add(toga.Label(
            "─" * 40,
            style=Pack(font_size=12, color="#555555",
                       margin_top=10, margin_left=10, margin_right=10, text_align="center")
        ))
        scroll_content.add(toga.Label(
            "Per informazioni telef. +39 3207060411",
            style=Pack(font_size=15, color="#cccccc",
                       margin_top=5, margin_left=10, margin_right=10, margin_bottom=20, text_align="center")
        ))

        # Scroll container
        scroll = toga.ScrollContainer(
            content=scroll_content,
            vertical=True,
            horizontal=False,
            style=Pack(flex=1)
        )
        self.box.add(scroll)

        return self.box

    def open(self):
        """Apre la pagina Home e carica le immagini"""
        self.app.main_window.content = self.box
        asyncio.create_task(self._load_images())

    async def _load_images(self):
        """Scarica le immagini dal server"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Logo
                logo_url = f"{IMG_BASE}/index/logo.jpg"
                try:
                    resp = await client.get(logo_url)
                    resp.raise_for_status()
                    self.logo_view.image = toga.Image(src=resp.content)
                except Exception as e:
                    print(f"Errore logo: {e}")

                # Header
                header_url = f"{IMG_BASE}/index/fronte.jpg"
                try:
                    resp = await client.get(header_url)
                    resp.raise_for_status()
                    self.header_view.image = toga.Image(src=resp.content)
                except Exception as e:
                    print(f"Errore header: {e}")

        except Exception as e:
            print(f"Errore caricamento immagini home: {e}")

    def close(self, widget=None):
        """Torna alla root_box"""
        self.app.main_window.content = self.app.root_box
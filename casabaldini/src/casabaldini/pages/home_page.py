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

        # Navbar (uguale a quella principale)
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
        scroll_content = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))

        # Logo in alto (placeholder, verrà caricato dopo)
        self.logo_view = toga.ImageView(style=Pack(width=250, align_items="center", margin_left=-10, margin_right=140))
        scroll_content.add(self.logo_view)

        # Immagine principale (placeholder)
        self.header_view = toga.ImageView(style=Pack(width=500, height=350, margin_left=-1, margin_right=40))
        scroll_content.add(self.header_view)

        # Testo introduttivo
        scroll_content.add(toga.Label(
            "Benvenuti a CasaBaldini",
            style=Pack(font_size=24, font_weight="bold", color="white", margin_left=10, margin_right=140)
        ))
        scroll_content.add(toga.Label(
            "Nel cuore del Mugello",
            style=Pack(font_size=16, color="#cccccc", margin_left=10, margin_right=140)
        ))
        scroll_content.add(toga.Label(
            " a pochi km. da Firenze",
            style=Pack(font_size=16, color="#cccccc", margin_left=10, margin_right=140)
        ))

        # Scroll container
        scroll = toga.ScrollContainer(
            content=scroll_content,
            vertical=True,
            horizontal=False,
            style=Pack(flex=1, padding=10)
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
                    self.logo_view.image = toga.Image(data=resp.content)
                except Exception as e:
                    print(f"Errore logo: {e}")

                # Header
                header_url = f"{IMG_BASE}/index/fronte.jpg"
                try:
                    resp = await client.get(header_url)
                    resp.raise_for_status()
                    self.header_view.image = toga.Image(data=resp.content)
                except Exception as e:
                    print(f"Errore header: {e}")

        except Exception as e:
            print(f"Errore caricamento immagini home: {e}")

    def close(self, widget=None):
        """Torna alla root_box"""
        self.app.main_window.content = self.app.root_box
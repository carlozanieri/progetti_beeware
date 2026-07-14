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

        # Contenuto scrollabile
        scroll_content = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))

        # Logo in alto (placeholder, verrà caricato dopo)
        self.logo_view = toga.ImageView(style=Pack(width=300, height=150, margin=20))
        scroll_content.add(self.logo_view)

        # Immagine principale (placeholder)
        self.header_view = toga.ImageView(style=Pack(width=500, height=350, margin=10))
        scroll_content.add(self.header_view)

        # Testo introduttivo
        scroll_content.add(toga.Label(
            "Benvenuti a CasaBaldini",
            style=Pack(font_size=24, font_weight="bold", color="white", margin=20)
        ))
        scroll_content.add(toga.Label(
            "Un luogo di charme nel cuore del Mugello",
            style=Pack(font_size=16, color="#cccccc", margin=10)
        ))

        # Scroll container
        scroll = toga.ScrollContainer(
            content=scroll_content,
            vertical=True,
            horizontal=False,
            style=Pack(flex=1)
        )
        self.box.add(scroll)

        # Pulsante per tornare indietro
        btn_back = toga.Button(
            "← Torna alla Home",
            on_press=self.close,
            style=Pack(margin=10, background_color="#043a55", color="white")
        )
        self.box.add(btn_back)

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
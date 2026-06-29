"""Footer con link utili a scorrimento automatico (marquee)"""

import asyncio
import webbrowser
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .api import fetch_links, download_image, IMG_BASE

SCORRI_INTERVALLO = 5.0    # secondi tra uno spostamento e l'altro
RIPRENDI_DOPO = 3.0        # secondi di pausa dopo un click


class LinksManager:
    """Gestisce la barra dei link in fondo con effetto marquee"""

    def build(self):
        """Costruisce il container scrollabile dei link"""
        self.links_box = toga.Box(style=Pack(direction=ROW))
        self.scroll = toga.ScrollContainer(
            content=self.links_box,
            horizontal=True,
            vertical=False,
            style=Pack(height=100, background_color="#043a55")
        )
        self._marquee_task = None
        self._all_links = []
        self._paused = False
        return self.scroll

    async def load(self):
        """Carica i link dal backend e avvia il marquee"""
        try:
            links_data = await fetch_links()
            self._all_links = []

            async with httpx.AsyncClient(timeout=10.0) as client:
                for link in links_data:
                    titolo = link.get("titolo", "")
                    url = link.get("link", "")
                    img_name = link.get("img", "")
                    img_url = f"{IMG_BASE}/links/{img_name}"

                    img = None
                    try:
                        data = await download_image(client, img_url)
                        img = toga.Image(data=data)
                    except Exception:
                        pass

                    self._all_links.append((titolo, url, img))

            self._popola_box()
            self._avvia_marquee()

        except Exception as err:
            print(f"ERRORE links: {err}")

    def _popola_box(self):
        """Riempie la box con i link (duplicati per marquee)"""
        self.links_box.clear()
        for _ in range(2):
            for titolo, url, img in self._all_links:
                link_box = toga.Box(style=Pack(direction=COLUMN, margin=5, alignment="center"))

                if img:
                    img_view = toga.ImageView(image=img, style=Pack(width=40, height=40))
                    link_box.add(img_view)

                btn = toga.Button(
                    titolo,
                    on_press=lambda w, u=url: self._on_click(u),
                    style=Pack(margin_top=3, margin_bottom=8, font_size=10,
                               background_color="#043a55", color="white")
                )
                link_box.add(btn)
                self.links_box.add(link_box)

    def _avvia_marquee(self):
        """Avvia il timer di scorrimento"""
        if self._marquee_task:
            self._marquee_task.cancel()
        self._paused = False
        self._marquee_task = asyncio.create_task(self._scorri())

    async def _scorri(self):
        """Loop di scorrimento continuo"""
        await asyncio.sleep(1)
        while True:
            await asyncio.sleep(SCORRI_INTERVALLO)
            if not self._paused and self.links_box.children:
                try:
                    primo = self.links_box.children[0]
                    self.links_box.remove(primo)
                    self.links_box.add(primo)
                except Exception:
                    pass

    def _on_click(self, url):
        """Gestisce il click su un link: apre il browser e mette in pausa"""
        self._paused = True
        webbrowser.open(url)
        # Riprendi dopo qualche secondo
        asyncio.create_task(self._riprendi_dopo_pausa())

    async def _riprendi_dopo_pausa(self):
        """Riprende lo scorrimento dopo una pausa"""
        await asyncio.sleep(RIPRENDI_DOPO)
        self._paused = False

    def ferma_marquee(self):
        """Ferma definitivamente lo scorrimento"""
        self._paused = True
        if self._marquee_task:
            self._marquee_task.cancel()
            self._marquee_task = None

    
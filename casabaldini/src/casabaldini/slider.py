"""Slider con autoplay, controlli overlay e indicatori cliccabili"""

import asyncio
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .api import fetch_slider, download_image, IMG_BASE

SLIDE_INTERVAL = 4


class SliderManager:
    """Gestisce lo slider: caricamento, visualizzazione, autoplay"""

    def __init__(self, image_view, titolo_label, caption_label, status_label, on_image_click=None):
        self.image_view = image_view
        self.titolo_label = titolo_label
        self.caption_label = caption_label
        self.status_label = status_label
        self.slides = []
        self.slide_images = []
        self.current_index = 0
        self.autoplay_task = None
        self.paused = False
        self.indicatori_box = None
        self.on_image_click = on_image_click

    def build_controls(self):

        """Costruisce i pulsanti freccia, dettaglio e gli indicatori"""
        controls_box = toga.Box(style=Pack(direction=COLUMN))

        # Pulsante dettaglio
        if self.on_image_click:
            print("Creo pulsante dettaglio")
            btn_dettaglio = toga.Button(
                "🔍 Dettaglio",
                on_press=lambda w: self.on_image_click(
                    self.slides[self.current_index] if self.slides else {},
                    self.slide_images[self.current_index] if self.slide_images else None
                ),
                style=Pack(margin=5, width=150, margin_left=200)
            )
            controls_box.add(btn_dettaglio)
        else:
            print("on_image_click è None, non creo il pulsante")
        # Pulsanti navigazione
        btn_prev, btn_next = self.build_arrow_buttons()
        nav_row = toga.Box(style=Pack(direction=ROW, margin=5))
        nav_row.add(btn_prev)
        nav_row.add(btn_next)
        controls_box.add(nav_row)

        # Box indicatori
        self.indicatori_box = toga.Box(style=Pack(direction=ROW, alignment="center", margin_bottom=10))
        controls_box.add(self.indicatori_box)

        return controls_box
    
    def build_arrow_buttons(self):
        """Restituisce i due pulsanti freccia separatamente"""
        btn_prev = toga.Button(
            "◀  Precedente",
            on_press=self.vai_precedente,
            style=Pack(flex=1, margin=5)
        )
        btn_next = toga.Button(
            "Successivo  ▶",
            on_press=self.vai_successivo,
            style=Pack(flex=1, margin=5)
        )
        return btn_prev, btn_next
    
    async def load(self, dir_val):
        """Carica slider da una sezione"""
        self.slides = []
        self.slide_images = []
        self.current_index = 0

        if self.autoplay_task:
            self.autoplay_task.cancel()
            self.autoplay_task = None

        self.status_label.text = f"Caricamento '{dir_val}'..."
        self.image_view.image = None
        self.titolo_label.text = ""
        self.caption_label.text = ""

        try:
            self.slides = await fetch_slider(dir_val)
            self.status_label.text = f"Scarico {len(self.slides)} immagini..."

            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, slide in enumerate(self.slides):
                    img_name = slide.get("img", "")
                    img_url = f"{IMG_BASE}/{dir_val}/{img_name}"
                    try:
                        data = await download_image(client, img_url)
                        self.slide_images.append(toga.Image(data=data))
                        self.status_label.text = f"Immagine {i+1}/{len(self.slides)}..."
                    except Exception as img_err:
                        print(f"Errore immagine {img_name}: {img_err}")
                        self.slide_images.append(None)

            self.status_label.text = ""
            self._aggiorna_indicatori()
            self.show(0)
            self.autoplay_task = asyncio.create_task(self._autoplay())

        except Exception as err:
            print(f"ERRORE slider: {err}")
            self.status_label.text = f"Errore: {err}"
            self.status_label.style.color = "red"

    def show(self, index):
        """Mostra una slide specifica"""
        if not self.slides:
            return
        self.current_index = index % len(self.slides)
        slide = self.slides[self.current_index]
        img = self.slide_images[self.current_index]
        if img:
            self.image_view.image = img
            self.titolo_label.text = slide.get("titolo", "")
            """self.caption_label.text = slide.get("caption", "")"""
            self._aggiorna_indicatori()

    def _aggiorna_indicatori(self):
        """Aggiorna i pallini indicatori cliccabili"""
        if self.indicatori_box is None:
            return
        self.indicatori_box.clear()
        for i in range(len(self.slides)):
            if i == self.current_index:
                # Pallino attivo: più grande e colorato
                btn = toga.Button(
                    "●",
                    on_press=lambda w, idx=i: self._vai_a(idx),
                    style=Pack(width=30, height=30, font_size=16, margin=5,
                               background_color="#00000000", color="#043a55")
                )
            else:
                # Pallino inattivo: più piccolo e grigio
                btn = toga.Button(
                    "○",
                    on_press=lambda w, idx=i: self._vai_a(idx),
                    style=Pack(width=30, height=30, font_size=14, margin=5,
                               background_color="#00000000", color="#999999")
                )
            self.indicatori_box.add(btn)

    def _vai_a(self, index):
        """Salta alla slide specificata dall'indicatore"""
        self.paused = True
        self.show(index)
        asyncio.create_task(self._riprendi())

    async def _autoplay(self):
        """Loop di autoplay"""
        while True:
            await asyncio.sleep(SLIDE_INTERVAL)
            if not self.paused and self.slides:
                self.show(self.current_index + 1)

    def vai_precedente(self, widget):
        self.paused = True
        self.show(self.current_index - 1)
        asyncio.create_task(self._riprendi())

    def vai_successivo(self, widget):
        self.paused = True
        self.show(self.current_index + 1)
        asyncio.create_task(self._riprendi())

    async def _riprendi(self):
        await asyncio.sleep(8)
        self.paused = False

    def build_clickable_image(self):
        """Rende l'ImageView cliccabile sostituendola con un Button contenente l'immagine"""
        # Non possiamo rendere ImageView cliccabile direttamente,
        # ma possiamo intercettare il click con un Box sovrapposto
        pass
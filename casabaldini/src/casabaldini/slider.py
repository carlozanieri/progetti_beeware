"""Slider con autoplay, controlli e indicatori cliccabili"""

import asyncio
import os
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .api import fetch_slider, download_image, IMG_BASE

SLIDE_INTERVAL = 4


class SliderManager:
    """Gestisce lo slider: caricamento, visualizzazione, autoplay"""

    def __init__(self, image_view, titolo_label, caption_label, status_label, loading_box=None, on_image_click=None):
        self.image_view = image_view
        self.titolo_label = titolo_label
        self.caption_label = caption_label
        self.status_label = status_label
        self.loading_box = loading_box
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

        btn_prev, btn_next = self.build_arrow_buttons()
        nav_row = toga.Box(style=Pack(direction=ROW, margin=5))
        nav_row.add(btn_prev)
        nav_row.add(btn_next)
        controls_box.add(nav_row)

        if self.on_image_click:
            btn_dettaglio = toga.Button(
                "🔍  Dettaglio",
                on_press=self._on_dettaglio_click,
                style=Pack(margin=5)
            )
            controls_box.add(btn_dettaglio)

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

    def build_loading_box(self):
        """Costruisce il box di caricamento con animazione testuale"""
        loading_box = toga.Box(style=Pack(direction=COLUMN, alignment="center", flex=1))
        
        # Spinner animato con caratteri
        self.spinner_label = toga.Label(
            "⏳",
            style=Pack(font_size=40, margin=20)
        )
        loading_box.add(self.spinner_label)
        
        self.loading_text = toga.Label(
            "Caricamento...",
            style=Pack(font_size=14, color="#043a55", font_weight="bold")
        )
        loading_box.add(self.loading_text)
        
        return loading_box

    def show_loading(self, message):
        """Mostra il box di caricamento e avvia animazione"""
        if self.loading_box:
            self.loading_text.text = message
            self.image_view.style.visibility = "hidden"
            self.loading_box.style.visibility = "visible"
            # Avvia animazione spinner
            if not hasattr(self, '_spinner_task') or self._spinner_task is None or self._spinner_task.done():
                self._spinner_task = asyncio.create_task(self._animate_spinner())

    def hide_loading(self):
        """Nasconde il box di caricamento e ferma animazione"""
        if self.loading_box:
            self.loading_box.style.visibility = "hidden"
            self.image_view.style.visibility = "visible"
        if hasattr(self, '_spinner_task') and self._spinner_task:
            self._spinner_task.cancel()

    async def _animate_spinner(self):
        """Anima lo spinner con caratteri che ruotano"""
        frames = ["◐", "◓", "◑", "◒"]
        while True:
            for frame in frames:
                try:
                    self.spinner_label.text = frame
                except Exception:
                    pass
                await asyncio.sleep(0.2)
    def show_loading(self, message):
        """Mostra il box di caricamento"""
        if self.loading_box:
            self.loading_text.text = message
            self.image_view.style.visibility = "hidden"
            self.loading_box.style.visibility = "visible"

    def hide_loading(self):
        """Nasconde il box di caricamento"""
        if self.loading_box:
            self.loading_box.style.visibility = "hidden"
            self.image_view.style.visibility = "visible"

    async def load(self, dir_val):
        """Carica slider da una sezione"""
        self.slides = []
        self.slide_images = []
        self.current_index = 0

        if self.autoplay_task:
            self.autoplay_task.cancel()
            self.autoplay_task = None

        self.show_loading(f"Caricamento '{dir_val}'...")
        self.image_view.image = None
        self.titolo_label.text = ""
        self.caption_label.text = ""

        try:
            self.slides = await fetch_slider(dir_val)
            total = len(self.slides)
            self.show_loading(f"Scarico {total} immagini...")

            async with httpx.AsyncClient(timeout=30.0) as client:
                urls = [f"{IMG_BASE}/{dir_val}/{s.get('img', '')}" for s in self.slides]
                tasks = [download_image(client, url) for url in urls]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                self.slide_images = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"Errore immagine {i}: {result}")
                        self.slide_images.append(None)
                    else:
                        self.slide_images.append(toga.Image(data=result))
                        self.show_loading(f"Immagine {i+1}/{total}...")

            self.hide_loading()
            self._aggiorna_indicatori()
            self.show(0)
            self.autoplay_task = asyncio.create_task(self._autoplay())

        except Exception as err:
            print(f"ERRORE slider: {err}")
            self.show_loading(f"Errore: {err}")
            self.loading_text.style.color = "red"

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
        self.caption_label.text = slide.get("caption", "")
        self._aggiorna_indicatori()

    def _aggiorna_indicatori(self):
        """Aggiorna i pallini indicatori cliccabili"""
        if self.indicatori_box is None:
            return
        self.indicatori_box.clear()
        for i in range(len(self.slides)):
            if i == self.current_index:
                btn = toga.Button(
                    "●",
                    on_press=lambda w, idx=i: self._vai_a(idx),
                    style=Pack(width=30, height=30, font_size=16, margin=2,
                               background_color="#00000000", color="#043a55")
                )
            else:
                btn = toga.Button(
                    "○",
                    on_press=lambda w, idx=i: self._vai_a(idx),
                    style=Pack(width=30, height=30, font_size=14, margin=2,
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

    def _on_dettaglio_click(self, widget):
        """Callback per il pulsante dettaglio"""
        if self.on_image_click and self.slides and self.slide_images:
            slide = self.slides[self.current_index]
            img = self.slide_images[self.current_index]
            if img:
                self.on_image_click(slide, img)
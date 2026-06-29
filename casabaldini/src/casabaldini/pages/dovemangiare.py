"""Pagina Dove Mangiare"""

import webbrowser
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from ..api import fetch_foods


class DoveMangiarePage:
    """Pagina con elenco ristoranti"""

    def __init__(self, app):
        self.app = app
        self.foods_urls = {}
        self.ristoranti_list = None
        self.box = None

    def build(self):
        """Costruisce la pagina"""
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        btn_indietro = toga.Button(
            "← Indietro",
            on_press=self.close,
            style=Pack(margin=10, background_color="#043a55", color="white")
        )
        self.box.add(btn_indietro)

        self.box.add(toga.Label(
            "Dove Mangiare",
            style=Pack(font_size=18, font_weight="bold", margin=10)
        ))

        return self.box

    async def open(self):
        """Apre la pagina e carica i dati"""
        self.app.main_window.content = self.box
        await self._load()

    def close(self, widget=None):
        """Torna alla home"""
        self.app.main_window.content = self.app.root_box

    async def _load(self):
        """Carica l'elenco ristoranti senza icone (per compatibilità GTK)"""
        from ..api import fetch_foods

        try:
            foods_data = await fetch_foods()
            items = []

            for food in foods_data:
                titolo = food.get("titolo", "")
                indirizzo = food.get("indirizzo", "")
                telefono = food.get("telefono", "")
                url = food.get("link", "")

                self.foods_urls[titolo] = url

                subtitle = ""
                if indirizzo:
                    subtitle += f"📍 {indirizzo}"
                if telefono:
                    subtitle += f"  📞 {telefono}"

                items.append({
                    "title": f"🍽️  {titolo}",
                    "subtitle": subtitle,
                    "icon": None,
                })
                print(f"Aggiunto: {titolo}")

            if self.ristoranti_list is not None:
                self.box.remove(self.ristoranti_list)

            self.ristoranti_list = toga.DetailedList(
                data=items,
                accessors=["title", "subtitle", "icon"],
                on_select=self._on_select,
                style=Pack(flex=1)
            )
            self.box.add(self.ristoranti_list)

            print(f"Totale ristoranti caricati: {len(items)}")

        except Exception as err:
            print(f"ERRORE dovemangiare: {err}")

    def _on_select(self, widget, **kwargs):
        """Apre il browser sul ristorante selezionato"""
        if hasattr(widget, 'selection') and widget.selection is not None:
            row = widget.selection
            titolo = row.title if hasattr(row, 'title') else row.get('title', '')
            # Rimuovi l'emoji iniziale se presente
            titolo_pulito = titolo.replace("🍽️  ", "").replace("🍽 ", "").strip()
            url = self.foods_urls.get(titolo_pulito, "")
            if url:
                webbrowser.open(url)
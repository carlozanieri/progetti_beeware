"""
CasaBaldini - App Toga con drawer hamburger, slider responsive e links
"""

import asyncio
import webbrowser
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import tempfile
import os

API_BASE = "https://json.casabaldini.eu/api/v1"
IMG_BASE = "https://json.casabaldini.eu/static/img"
SLIDE_INTERVAL = 4


class CasaBaldiniApp(toga.App):
    def startup(self):
        self.slides = []
        self.slide_images = []
        self.current_index = 0
        self.autoplay_task = None
        self.paused = False
        self.menu_aperto = False
        self.menu_data = []
        self.foods_urls = {}

        # --- Drawer laterale ---
        self.drawer_box = toga.Box(
            style=Pack(direction=COLUMN, flex=1, background_color="#1a3a4a")
        )
        btn_chiudi = toga.Button(
            "✕  Chiudi",
            on_press=self.toggle_drawer,
            style=Pack(margin=10, background_color="#043a55", color="white")
        )
        self.drawer_box.add(btn_chiudi)
        self.drawer_box.add(toga.Label(
            "CasaBaldini",
            style=Pack(font_size=18, font_weight="bold", color="white",
                       margin=15, background_color="#043a55")
        ))

        # --- Schermata Dove Mangiare ---
        self.dovemangiare_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        btn_indietro_dm = toga.Button(
            "← Indietro",
            on_press=self.chiudi_dovemangiare,
            style=Pack(margin=10, background_color="#043a55", color="white")
        )
        self.dovemangiare_box.add(btn_indietro_dm)
        self.dovemangiare_box.add(toga.Label(
            "Dove Mangiare",
            style=Pack(font_size=18, font_weight="bold", margin=10)
        ))
        # La DetailedList verrà creata dopo il caricamento dati
        self.ristoranti_list = None
        # --- Schermata Prenotazioni ---
        self.prenotazioni_box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color="#000000"))
        
        # Maniglia superiore
        maniglia = toga.Box(style=Pack(width=55, height=6, background_color="#404040", margin_top=10, margin_bottom=20))
        maniglia_container = toga.Box(style=Pack(direction=ROW, alignment="center"))
        maniglia_container.add(maniglia)
        self.prenotazioni_box.add(maniglia_container)
        
        # Titolo
        self.prenotazioni_box.add(toga.Label(
            "Prenotazioni CasaBaldini",
            style=Pack(font_size=22, font_weight="bold", color="white", margin_bottom=10)
        ))
        
        # Contatti
        self._aggiungi_contatto(
            self.prenotazioni_box,
            "Chiamaci",
            "+39 320 7060411",
            "tel:+393207060411"
        )
        self._aggiungi_contatto(
            self.prenotazioni_box,
            "Chiamaci tel. fisso",
            "+39 055 2741209",
            "tel:+390552741209"
        )
        self._aggiungi_contatto(
            self.prenotazioni_box,
            "Inviaci una mail",
            "carlo.zanieri@gmail.com",
            "mailto:carlo.zanieri@gmail.com?subject=Richiesta informazioni CasaBaldini"
        )
        
        # Testo informativo
        self.prenotazioni_box.add(toga.Label(
            "Le prenotazioni sono soggette a disponibilità. "
            "Contattaci direttamente per ricevere la migliore offerta garantita.",
            style=Pack(font_style="italic", color="#b3b3b3", font_size=13, margin=20)
        ))
        
        # Bottone Chiudi
        btn_chiudi_pren = toga.Button(
            "CHIUDI",
            on_press=self.chiudi_prenotazioni,
            style=Pack(margin=10, background_color="#1a1a1a", color="white", flex=1)
        )
        self.prenotazioni_box.add(btn_chiudi_pren)
        # --- Contenuto principale ---
        self.root_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Navbar
        navbar = toga.Box(style=Pack(direction=ROW, background_color="#043a55", margin=8))
        btn_hamburger = toga.Button(
            "☰",
            on_press=self.toggle_drawer,
            style=Pack(width=40, height=40, background_color="#043a55", color="white")
        )
        self.titolo_navbar = toga.Label(
            "CasaBaldini",
            style=Pack(flex=1, font_size=18, font_weight="bold", color="white", margin_left=10)
        )
        navbar.add(btn_hamburger)
        navbar.add(self.titolo_navbar)

        self.status_label = toga.Label(
            "Caricamento...",
            style=Pack(font_size=12, color="orange", margin=10)
        )
        self.image_view = toga.ImageView(style=Pack(flex=1, height=250))
        self.titolo_label = toga.Label(
            "", style=Pack(font_size=15, font_weight="bold", margin_top=8, margin_left=10)
        )
        self.caption_label = toga.Label(
            "", style=Pack(font_size=12, color="#555555", margin_left=10, margin_bottom=8)
        )

        btn_prev = toga.Button(
            "◀  Precedente", on_press=self.vai_precedente,
            style=Pack(flex=1, margin=5)
        )
        btn_next = toga.Button(
            "Successivo  ▶", on_press=self.vai_successivo,
            style=Pack(flex=1, margin=5)
        )
        nav_row = toga.Box(style=Pack(direction=ROW, margin=5))
        nav_row.add(btn_prev)
        nav_row.add(btn_next)

        self.links_box = toga.Box(style=Pack(direction=ROW, margin=5))
        self.links_scroll = toga.ScrollContainer(
            content=self.links_box,
            horizontal=True,
            vertical=False,
            style=Pack(height=100, background_color="#043a55")
        )

        self.root_box.add(navbar)
        self.root_box.add(self.status_label)
        self.root_box.add(self.image_view)
        self.root_box.add(self.titolo_label)
        self.root_box.add(self.caption_label)
        self.root_box.add(nav_row)
        self.root_box.add(self.links_scroll)

        self.main_window = toga.MainWindow(title="CasaBaldini")
        self.main_window.content = self.root_box
        self.main_window.show()

        asyncio.create_task(self.inizializza())

    def toggle_drawer(self, widget):
        if self.menu_aperto:
            self.main_window.content = self.root_box
            self.menu_aperto = False
        else:
            self.main_window.content = self.drawer_box
            self.menu_aperto = True

    async def inizializza(self):
        await self.carica_menu()
        await self.carica_slider("index")
        await self.carica_links()

    async def carica_menu(self):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/menu")
                response.raise_for_status()
                self.menu_data = response.json()

            for voce in self.menu_data:
                children = voce.get("children", [])
                parent_titolo = voce.get("parent", {}).get("titolo", "")

                self.drawer_box.add(toga.Label(
                    parent_titolo.upper(),
                    style=Pack(font_size=10, color="#aaaaaa", margin_top=10,
                               margin_left=15, margin_bottom=2, background_color="#1a3a4a")
                ))

                for child in children:
                    tipopage = child.get("tipopage", "")
                    link = child.get("link", "")
                    titolo = child.get("titolo", "")

                    if tipopage == "interna" and link.startswith("/casabaldini/"):
                        dir_val = link.split("/")[-1]
                        btn = toga.Button(
                            titolo,
                            on_press=lambda w, d=dir_val, t=titolo: asyncio.create_task(
                                self.cambia_sezione(d, t)
                            ),
                            style=Pack(margin_left=15, margin_top=8, margin_bottom=8,
                                       background_color="#1a3a4a", color="white", flex=1)
                        )
                        self.drawer_box.add(btn)

                    elif tipopage == "modale" and "dovemangiare" in link:
                        btn = toga.Button(
                            titolo,
                            on_press=lambda w: asyncio.create_task(self.apri_dovemangiare()),
                            style=Pack(margin_left=15, margin_top=8, margin_bottom=8,
                                       background_color="#1a3a4a", color="white", flex=1)
                        )
                        self.drawer_box.add(btn)
                    elif tipopage == "modale" and "prenotazioni" in link:
                        btn = toga.Button(
                            titolo,
                            on_press=lambda w: asyncio.create_task(self.apri_prenotazioni()),
                            style=Pack(margin_left=15, margin_top=8, margin_bottom=8,
                                       background_color="#1a3a4a", color="white", flex=1)
                        )
                        self.drawer_box.add(btn)
        except Exception as err:
            print(f"ERRORE menu: {err}")

    async def cambia_sezione(self, dir_val, titolo):
        self.main_window.content = self.root_box
        self.menu_aperto = False
        self.titolo_navbar.text = titolo
        await self.carica_slider(dir_val)

    async def apri_dovemangiare(self):
        self.main_window.content = self.dovemangiare_box
        self.menu_aperto = False
        await self.carica_dovemangiare()

    async def chiudi_dovemangiare(self, widget):
        self.main_window.content = self.root_box

    async def carica_dovemangiare(self):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/foods")
                response.raise_for_status()
                foods_data = response.json()

            items = []
            for food in foods_data:
                titolo = food.get("titolo", "")
                indirizzo = food.get("indirizzo", "")
                telefono = food.get("telefono", "")
                url = food.get("link", "")
                img_name = food.get("img", "")

                self.foods_urls[titolo] = url

                subtitle = ""
                if indirizzo:
                    subtitle += f"📍 {indirizzo}"
                if telefono:
                    subtitle += f"  📞 {telefono}"

                items.append({
                    "title": titolo,
                    "subtitle": subtitle,
                    "icon": None,  # temporaneamente nessuna icona
                })
                print(f"Aggiunto: {titolo}")

            # Rimuovi la vecchia lista se esiste
            if self.ristoranti_list is not None:
                self.dovemangiare_box.remove(self.ristoranti_list)

            # Crea una nuova DetailedList con i dati freschi
            self.ristoranti_list = toga.DetailedList(
                data=items,
                accessors=["title", "subtitle", "icon"],
                on_select=self.ristorante_selezionato,
                style=Pack(flex=1)
            )

            # Aggiungi la nuova lista al box
            self.dovemangiare_box.add(self.ristoranti_list)

            print(f"Totale ristoranti caricati: {len(items)}")

        except Exception as err:
            print(f"ERRORE dovemangiare: {err}")

    def ristorante_selezionato(self, widget, **kwargs):
        # Recupera la selezione corrente dalla DetailedList
        if hasattr(widget, 'selection') and widget.selection is not None:
            row = widget.selection
            # row è l'elemento selezionato (il dizionario che abbiamo creato)
            titolo = row.title if hasattr(row, 'title') else row.get('title', '')
            url = self.foods_urls.get(titolo, "")
            if url:
                webbrowser.open(url)

    def _aggiungi_contatto(self, box, titolo, sottotitolo, url):
        """Crea un box contatto cliccabile e lo aggiunge al box passato"""
        contatto_box = toga.Box(style=Pack(direction=ROW, margin=10))
        
        # Testi
        testi_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        testi_box.add(toga.Label(
            titolo,
            style=Pack(font_weight="bold", color="white", font_size=14)
        ))
        testi_box.add(toga.Label(
            sottotitolo,
            style=Pack(color="#b3b3b3", font_size=12)
        ))
        
        contatto_box.add(testi_box)
        
        # Rendi cliccabile tutto il box
        btn = toga.Button(
            "›",
            on_press=lambda w, u=url: webbrowser.open(u),
            style=Pack(width=40, background_color="#1a1a1a", color="white")
        )
        contatto_box.add(btn)
        
        box.add(contatto_box)

    def _aggiungi_contatto(self, box, titolo, sottotitolo, url):
        """Crea un box contatto cliccabile e lo aggiunge al box passato"""
        contatto_box = toga.Box(style=Pack(direction=ROW, margin=10))
        
        # Testi
        testi_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        testi_box.add(toga.Label(
            titolo,
            style=Pack(font_weight="bold", color="white", font_size=14)
        ))
        testi_box.add(toga.Label(
            sottotitolo,
            style=Pack(color="#b3b3b3", font_size=12)
        ))
        
        contatto_box.add(testi_box)
        
        # Rendi cliccabile tutto il box
        btn = toga.Button(
            "›",
            on_press=lambda w, u=url: webbrowser.open(u),
            style=Pack(width=40, background_color="#1a1a1a", color="white")
        )
        contatto_box.add(btn)
        
        box.add(contatto_box)

    async def apri_prenotazioni(self):
        self.main_window.content = self.prenotazioni_box
        self.menu_aperto = False

    def chiudi_prenotazioni(self, widget):
        self.main_window.content = self.root_box

    async def carica_slider(self, dir_val):
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
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/slider?dir={dir_val}")
                response.raise_for_status()
                self.slides = response.json()

            self.status_label.text = f"Scarico {len(self.slides)} immagini..."

            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, slide in enumerate(self.slides):
                    img_name = slide.get("img", "")
                    img_url = f"{IMG_BASE}/{dir_val}/{img_name}"
                    try:
                        img_response = await client.get(img_url)
                        img_response.raise_for_status()
                        self.slide_images.append(toga.Image(data=img_response.content))
                        self.status_label.text = f"Immagine {i+1}/{len(self.slides)}..."
                    except Exception as img_err:
                        print(f"Errore immagine {img_name}: {img_err}")
                        self.slide_images.append(None)

            self.status_label.text = ""
            self.mostra_slide(0)
            self.autoplay_task = asyncio.create_task(self.autoplay())

        except Exception as err:
            print(f"ERRORE slider: {err}")
            self.status_label.text = f"Errore: {err}"
            self.status_label.style.color = "red"

    async def carica_links(self):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/links")
                response.raise_for_status()
                links_data = response.json()

            async with httpx.AsyncClient(timeout=10.0) as client:
                for link in links_data:
                    titolo = link.get("titolo", "")
                    url = link.get("link", "")
                    img_name = link.get("img", "")
                    img_url = f"{IMG_BASE}/links/{img_name}"

                    link_box = toga.Box(style=Pack(direction=COLUMN, margin=5, alignment="center"))

                    try:
                        img_response = await client.get(img_url)
                        img_response.raise_for_status()
                        img = toga.Image(data=img_response.content)
                        img_view = toga.ImageView(image=img, style=Pack(width=40, height=40))
                        link_box.add(img_view)
                    except Exception:
                        pass

                    btn = toga.Button(
                        titolo,
                        on_press=lambda w, u=url: webbrowser.open(u),
                        style=Pack(margin_top=3, margin_bottom=8, font_size=10,
                                   background_color="#043a55", color="white")
                    )
                    link_box.add(btn)
                    self.links_box.add(link_box)

        except Exception as err:
            print(f"ERRORE links: {err}")

    def mostra_slide(self, index):
        if not self.slides:
            return
        self.current_index = index % len(self.slides)
        slide = self.slides[self.current_index]
        img = self.slide_images[self.current_index]
        if img:
            self.image_view.image = img
        self.titolo_label.text = slide.get("titolo", "")
        self.caption_label.text = slide.get("caption", "")

    async def autoplay(self):
        while True:
            await asyncio.sleep(SLIDE_INTERVAL)
            if not self.paused and self.slides:
                self.mostra_slide(self.current_index + 1)

    def vai_precedente(self, widget):
        self.paused = True
        self.mostra_slide(self.current_index - 1)
        asyncio.create_task(self.riprendi_autoplay())

    def vai_successivo(self, widget):
        self.paused = True
        self.mostra_slide(self.current_index + 1)
        asyncio.create_task(self.riprendi_autoplay())

    async def riprendi_autoplay(self):
        await asyncio.sleep(8)
        self.paused = False


def main():
    return CasaBaldiniApp()
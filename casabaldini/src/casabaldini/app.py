"""
CasaBaldini - App Toga con drawer hamburger, slider responsive e links
"""

import asyncio
import webbrowser
import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

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

        # --- Drawer laterale (schermata separata) ---
        self.drawer_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
                background_color="#1a3a4a",
            )
        )

        btn_chiudi = toga.Button(
            "✕  Chiudi",
            on_press=self.toggle_drawer,
            style=Pack(
                padding=10,
                background_color="#043a55",
                color="white",
            )
        )
        self.drawer_box.add(btn_chiudi)

        self.drawer_box.add(toga.Label(
            "CasaBaldini",
            style=Pack(
                font_size=18,
                font_weight="bold",
                color="white",
                padding=15,
                background_color="#043a55",
            )
        ))
        # --- Schermata Dove Mangiare ---
        self.dovemangiare_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        btn_indietro_dm = toga.Button(
            "← Indietro",
            on_press=self.chiudi_dovemangiare,
            style=Pack(padding=10, background_color="#043a55", color="white")
            )
        self.dovemangiare_box.add(btn_indietro_dm)
        self.dovemangiare_box.add(toga.Label(
                "Dove Mangiare",
                style=Pack(font_size=18, font_weight="bold", padding=10)
            ))

        self.ristoranti_box = toga.Box(style=Pack(direction=COLUMN))
        self.dovemangiare_scroll = toga.ScrollContainer(
            content=self.ristoranti_box,
            horizontal=False,
            vertical=True,
            style=Pack(flex=1)
        )
        self.dovemangiare_box.add(self.dovemangiare_scroll)
        # --- Contenuto principale ---
        self.root_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # --- Navbar top ---
        navbar = toga.Box(
            style=Pack(
                direction=ROW,
                background_color="#043a55",
                padding=8,
            )
        )
        btn_hamburger = toga.Button(
            "☰",
            on_press=self.toggle_drawer,
            style=Pack(
                width=40,
                height=40,
                background_color="#043a55",
                color="white",
            )
        )
        self.titolo_navbar = toga.Label(
            "CasaBaldini",
            style=Pack(
                flex=1,
                font_size=18,
                font_weight="bold",
                color="white",
                padding_left=10,
            )
        )
        navbar.add(btn_hamburger)
        navbar.add(self.titolo_navbar)

        # --- Status label ---
        self.status_label = toga.Label(
            "Caricamento...",
            style=Pack(font_size=12, color="orange", padding=10)
        )

        # --- ImageView ---
        self.image_view = toga.ImageView(
            style=Pack(flex=1, height=250)
        )

        # --- Titolo e caption slide ---
        self.titolo_label = toga.Label(
            "",
            style=Pack(
                font_size=15,
                font_weight="bold",
                padding_top=8,
                padding_left=10,
            )
        )
        self.caption_label = toga.Label(
            "",
            style=Pack(
                font_size=12,
                color="#555555",
                padding_left=10,
                padding_bottom=8,
            )
        )

        # --- Frecce navigazione ---
        btn_prev = toga.Button(
            "◀  Precedente",
            on_press=self.vai_precedente,
            style=Pack(flex=1, padding=5)
        )
        btn_next = toga.Button(
            "Successivo  ▶",
            on_press=self.vai_successivo,
            style=Pack(flex=1, padding=5)
        )
        nav_row = toga.Box(style=Pack(direction=ROW, padding=5))
        nav_row.add(btn_prev)
        nav_row.add(btn_next)

        # --- Footer links ---
        self.links_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.links_scroll = toga.ScrollContainer(
            content=self.links_box,
            horizontal=True,
            vertical=False,
            style=Pack(height=100, background_color="#043a55")  # aumentato da 80 a 100
        )

        # Assembla root_box
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
                    style=Pack(
                        font_size=10,
                        color="#aaaaaa",
                        padding_top=10,
                        padding_left=15,
                        padding_bottom=2,
                        background_color="#1a3a4a",
                    )
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
                            style=Pack(
                                padding_left=15,
                                padding_top=8,
                                padding_bottom=8,
                                background_color="#1a3a4a",
                                color="white",
                                flex=1,
                            )
                        )
                    elif tipopage == "modale" and "dovemangiare" in link:
                        btn = toga.Button(
                            titolo,
                            on_press=lambda w: asyncio.create_task(
                                self.apri_dovemangiare()
                            ),
                            style=Pack(
                                padding_left=15,
                                padding_top=8,
                                padding_bottom=8,
                                background_color="#1a3a4a",
                                color="white",
                                flex=1,
                            )
                        )   
                        self.drawer_box.add(btn)
    
        except Exception as e:
            print(f"ERRORE menu: {e}")
            self.status_label.text = f"Errore menu: {e}"

    async def cambia_sezione(self, dir_val, titolo):
        self.main_window.content = self.root_box
        self.menu_aperto = False
        self.titolo_navbar.text = titolo
        await self.carica_slider(dir_val)

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
                    except Exception as e:
                        print(f"Errore immagine {img_name}: {e}")
                        self.slide_images.append(None)

            self.status_label.text = ""
            self.mostra_slide(0)
            self.autoplay_task = asyncio.create_task(self.autoplay())

        except Exception as e:
            print(f"ERRORE slider: {e}")
            self.status_label.text = f"Errore: {e}"
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

                    link_box = toga.Box(style=Pack(
                        direction=COLUMN,
                        padding=5,
                        alignment="center",
                    ))

                    try:
                        img_response = await client.get(img_url)
                        img_response.raise_for_status()
                        img = toga.Image(data=img_response.content)
                        img_view = toga.ImageView(
                            image=img,
                            style=Pack(width=40, height=40)
                        )
                        link_box.add(img_view)
                    except Exception:
                        pass

                    btn = toga.Button(
                        titolo,
                        on_press=lambda w, u=url: webbrowser.open(u),
                        style=Pack(
                            padding_top=3,
                            padding_bottom=8,
                            font_size=10,
                            background_color="#043a55",
                            color="white",
                        )
                    )
                    link_box.add(btn)
                    self.links_box.add(link_box)

        except Exception as e:
            print(f"ERRORE links: {e}")

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

    async def apri_dovemangiare(self):
        # Chiudi drawer
        self.main_window.content = self.dovemangiare_box
        self.menu_aperto = False

    # Carica ristoranti se non già caricati
        if not self.ristoranti_box.children:
            await self.carica_dovemangiare()

    async def chiudi_dovemangiare(self, widget):
        self.main_window.content = self.root_box

    async def carica_dovemangiare(self):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{API_BASE}/foods")
                response.raise_for_status()
                foods_data = response.json()

            async with httpx.AsyncClient(timeout=15.0) as client:
                for food in foods_data:
                    titolo = food.get("titolo", "")
                    indirizzo = food.get("indirizzo", "")
                    telefono = food.get("telefono", "")
                    link = food.get("link", "")
                    img_name = food.get("img", "")
                    img_url = f"{IMG_BASE}/ristoranti/{img_name}"

                # Box orizzontale: immagine + info
                    riga = toga.Box(style=Pack(
                        direction=ROW,
                        padding=8,
                    ))

                # Immagine
                try:
                    img_response = await client.get(img_url)
                    img_response.raise_for_status()
                    img = toga.Image(data=img_response.content)
                    img_view = toga.ImageView(
                        image=img,
                        style=Pack(width=80, height=80)
                    )
                    riga.add(img_view)
                except Exception as e:
                    print(f"Errore immagine {img_name}: {e}")
                    # Placeholder se immagine non disponibile
                    riga.add(toga.Box(style=Pack(width=80, height=80)))

                # Info testuali
                info_box = toga.Box(style=Pack(
                    direction=COLUMN,
                    padding_left=10,
                    flex=1,
                ))
                info_box.add(toga.Label(
                    titolo,
                    style=Pack(font_size=14, font_weight="bold", padding_bottom=3)
                ))
                if indirizzo:
                    info_box.add(toga.Label(
                        f"📍 {indirizzo}",
                        style=Pack(font_size=11, padding_bottom=2)
                    ))
                if telefono:
                    info_box.add(toga.Label(
                        f"📞 {telefono}",
                        style=Pack(font_size=11, padding_bottom=2)
                    ))
                if link:
                    btn_link = toga.Button(
                        "Apri sito →",
                        on_press=lambda w, u=link: webbrowser.open(u),
                        style=Pack(font_size=11, padding_top=3)
                    )
                    info_box.add(btn_link)

                riga.add(info_box)
                self.ristoranti_box.add(riga)

                # Separatore visivo
                self.ristoranti_box.add(toga.Box(
                    style=Pack(height=1, background_color="#cccccc", margin_top=2, margin_bottom=2)
                ))
            for i, food in enumerate(foods_data):
                print(f"Processo ristorante {i+1}: {food.get('titolo', '')}")
        except Exception as e:
            print(f"ERRORE dovemangiare: {e}")
            self.ristoranti_box.add(toga.Label(
                f"Errore caricamento: {e}",
                style=Pack(color="red", padding=10)
            ))


def main():
    return CasaBaldiniApp()
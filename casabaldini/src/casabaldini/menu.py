"""Menu overlay a due livelli"""

import asyncio
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class MenuManager:
    """Gestisce il drawer overlay con menu primari e sottomenu"""

    def __init__(self, app):
        self.app = app
        self.menu_data = []

    def build_overlay(self):
        """Costruisce l'overlay del menu"""
        self.menu_overlay = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color="#00000088"))

        self.menu_box = toga.Box(style=Pack(direction=COLUMN, width=280, flex=1, background_color="#1a3a4a"))

        self.menu_box.add(toga.Label(
            "CasaBaldini",
            style=Pack(font_size=18, font_weight="bold", color="white", margin=15)
        ))

        self.menu_voci_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self.menu_box.add(self.menu_voci_box)

        btn_chiudi = toga.Button(
            "✕  Chiudi",
            on_press=self.toggle,
            style=Pack(margin=10, background_color="#043a55", color="white")
        )
        self.menu_box.add(btn_chiudi)

        overlay_row = toga.Box(style=Pack(direction=ROW, flex=1))
        overlay_row.add(self.menu_box)
        zona_chiudi = toga.Button(
            "",
            on_press=self.toggle,
            style=Pack(flex=1, background_color="#00000000")
        )
        overlay_row.add(zona_chiudi)
        self.menu_overlay.add(overlay_row)

        return self.menu_overlay

    async def load_data(self):
        """Carica i dati del menu dall'API"""
        from .api import fetch_menu
        try:
            self.menu_data = await fetch_menu()
        except Exception as err:
            print(f"ERRORE menu: {err}")

    def toggle(self, widget):
        """Apre/chiude il menu"""
        if self.app.menu_aperto:
            self.close()
        else:
            self.open()

    def open(self):
        """Apre il menu mostrando i menu primari"""
        self._show_primary()
        self.app.main_window.content = self.menu_overlay
        self.app.menu_aperto = True

    def close(self):
        """Chiude il menu"""
        self.app.main_window.content = self.app.root_box
        self.app.menu_aperto = False

    def _show_primary(self):
        """Popola con i titoli dei menu primari"""
        self.menu_voci_box.clear()
        self.menu_voci_box.add(toga.Label(
            "MENU",
            style=Pack(font_size=12, color="#aaaaaa", margin_top=10, margin_left=15, margin_bottom=5)
        ))
        for voce in self.menu_data:
            parent = voce.get("parent", {})
            parent_titolo = parent.get("titolo", "")
            children = voce.get("children", [])

            btn = toga.Button(
                parent_titolo,
                on_press=lambda w, c=children, t=parent_titolo: self._show_secondary(c, t),
                style=Pack(margin_left=15, margin_top=5, margin_bottom=5,
                           background_color="#1a3a4a", color="white", flex=1)
            )
            self.menu_voci_box.add(btn)

    def _show_secondary(self, children, titolo_padre):
        """Popola con i figli di un menu primario"""
        self.menu_voci_box.clear()

        btn_back = toga.Button(
            f"←  {titolo_padre}",
            on_press=lambda w: self._show_primary(),
            style=Pack(margin_left=10, margin_top=10, margin_bottom=10,
                       background_color="#1a3a4a", color="#aaaaaa")
        )
        self.menu_voci_box.add(btn_back)

        for child in children:
            tipopage = child.get("tipopage", "")
            link = child.get("link", "")
            titolo = child.get("titolo", "")

            if tipopage == "interna":
                if link == "/":
                    # Home page statica
                    btn = toga.Button(
                        titolo,
                        on_press=lambda w: asyncio.create_task(self._select_home()),
                        style=Pack(margin_left=25, margin_top=5, margin_bottom=5,
                                   background_color="#1a3a4a", color="white", flex=1)
                    )
                    self.menu_voci_box.add(btn)
                elif link.startswith("/casabaldini/"):
                    dir_val = link.split("/")[-1]
                    btn = toga.Button(
                        titolo,
                        on_press=lambda w, d=dir_val, t=titolo: self._select_section(d, t),
                        style=Pack(margin_left=25, margin_top=5, margin_bottom=5,
                                   background_color="#1a3a4a", color="white", flex=1)
                    )
                    self.menu_voci_box.add(btn)

            elif tipopage == "modale" and "dovemangiare" in link:
                btn = toga.Button(
                    titolo,
                    on_press=lambda w: asyncio.create_task(self._select_dovemangiare()),
                    style=Pack(margin_left=25, margin_top=5, margin_bottom=5,
                               background_color="#1a3a4a", color="white", flex=1)
                )
                self.menu_voci_box.add(btn)

            elif tipopage == "modale" and "prenotazioni" in link:
                btn = toga.Button(
                    titolo,
                    on_press=lambda w: asyncio.create_task(self._select_prenotazioni()),
                    style=Pack(margin_left=25, margin_top=5, margin_bottom=5,
                               background_color="#1a3a4a", color="white", flex=1)
                )
                self.menu_voci_box.add(btn)

    def _select_section(self, dir_val, titolo):
        """Naviga a una sezione interna"""
        self.close()
        self.app.titolo_navbar.text = titolo
        asyncio.create_task(self.app.slider_manager.load(dir_val))

    async def _select_dovemangiare(self):
        """Apre Dove Mangiare"""
        self.close()
        await self.app.dovemangiare_page.open()

    async def _select_prenotazioni(self):
        """Apre Prenotazioni"""
        self.close()
        await self.app.prenotazioni_page.open()

    async def _select_home(self):
        """Apre la Home page statica"""
        self.close()
        self.app.home_page_view.open()
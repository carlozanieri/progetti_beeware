"""
Gestione tabella sliders - Desktop App
Connessione diretta a PostgreSQL
"""

import sys
import psycopg2
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER


# ============================================================
# CONFIGURAZIONE DATABASE (modifica con i tuoi dati reali)
# ============================================================
DB_CONFIG = {
    "host": "57.131.31.228",
    "port": 5432,
    "dbname": "casabaldini",
    "user": "carlo",
    "password": "treX39",
}

# ============================================================
# MODELLO DATI
# ============================================================
FIELDS = [
    ("id", "ID", False),          # (nome_colonna, etichetta, modificabile)
    ("codice", "Codice", True),
    ("codice2", "Codice 2", True),
    ("img", "Immagine", True),
    ("titolo", "Titolo", True),
    ("caption", "Caption", True),
    ("link", "Link", True),
    ("testo", "Testo", True),
]

EDITABLE_FIELDS = [(col, lbl) for col, lbl, editable in FIELDS if editable]


# ============================================================
# OPERAZIONI DATABASE
# ============================================================
def get_connection():
    """Crea una connessione al database"""
    return psycopg2.connect(**DB_CONFIG)


def fetch_all():
    """Recupera tutti i record"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, codice, codice2, img, titolo, caption, link, testo FROM sliders ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def insert_record(data):
    """Inserisce un nuovo record"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sliders (codice, codice2, img, titolo, caption, link, testo)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def update_record(record_id, data):
    """Aggiorna un record esistente"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE sliders
           SET codice=%s, codice2=%s, img=%s, titolo=%s, caption=%s, link=%s, testo=%s
           WHERE id=%s""",
        data + (record_id,),
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_record(record_id):
    """Elimina un record"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sliders WHERE id=%s", (record_id,))
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# DIALOG MODIFICA/INSERIMENTO
# ============================================================
class RecordDialog:
    """Dialog per inserire o modificare un record"""

    def __init__(self, title, on_save, existing_data=None):
        self.on_save = on_save
        self.existing_data = existing_data

        self.box = toga.Box(style=Pack(direction=COLUMN, margin=20))

        # Titolo dialog
        self.box.add(toga.Label(
            title,
            style=Pack(font_size=18, font_weight="bold", margin_bottom=15)
        ))

        # Campi di input
        self.inputs = {}
        for col_name, label in EDITABLE_FIELDS:
            row_box = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
            lbl = toga.Label(label, style=Pack(width=100, font_weight="bold"))
            row_box.add(lbl)

            # Per il testo usa MultilineTextInput, per gli altri TextInput
            if col_name == "testo":
                inp = toga.MultilineTextInput(style=Pack(flex=1, height=100))
            elif col_name == "caption":
                inp = toga.MultilineTextInput(style=Pack(flex=1, height=60))
            else:
                inp = toga.TextInput(style=Pack(flex=1))

            # Precompila se stiamo modificando
            if existing_data:
                col_index = [c for c, _, _ in FIELDS].index(col_name)
                value = existing_data[col_index]
                if value:
                    if col_name in ("testo", "caption"):
                        inp.value = str(value)
                    else:
                        inp.value = str(value)

            self.inputs[col_name] = inp
            row_box.add(inp)
            self.box.add(row_box)

        # Pulsanti
        btn_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, margin_top=15))

        btn_salva = toga.Button(
            "Salva",
            on_press=self._do_save,
            style=Pack(margin=5, background_color="#043a55", color="white")
        )
        btn_annulla = toga.Button(
            "Annulla",
            on_press=self._do_cancel,
            style=Pack(margin=5)
        )
        btn_box.add(btn_salva)
        btn_box.add(btn_annulla)
        self.box.add(btn_box)

    def _do_save(self, widget):
        """Raccoglie i dati e chiama il callback"""
        data = []
        for col_name, _ in EDITABLE_FIELDS:
            inp = self.inputs[col_name]
            if hasattr(inp, 'value'):
                val = inp.value.strip()
            else:
                val = inp.text.strip()
            data.append(val if val else None)
        self.on_save(tuple(data))

    def _do_cancel(self, widget):
        """Chiude senza salvare"""
        self.on_save(None)


# ============================================================
# APP PRINCIPALE
# ============================================================
class SlidersManagerApp(toga.App):


    def startup(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # --- Toolbar ---
        toolbar = toga.Box(style=Pack(direction=ROW, background_color="#043a55", padding=10))

        lbl_title = toga.Label(
            "Gestione Sliders",
            style=Pack(flex=1, font_size=18, font_weight="bold", color="white")
        )
        toolbar.add(lbl_title)

        btn_refresh = toga.Button(
            "🔄  Aggiorna",
            on_press=self._refresh,
            style=Pack(margin_left=10, background_color="#065a75", color="white")
        )
        toolbar.add(btn_refresh)

        btn_new = toga.Button(
            "➕  Nuovo",
            on_press=self._new_record,
            style=Pack(margin_left=5, background_color="#065a75", color="white")
        )
        toolbar.add(btn_new)

        self.main_box.add(toolbar)

        # --- Tabella ---
        self.table = toga.Table(
            headings=["ID", "Codice", "Codice 2", "Immagine", "Titolo", "Caption", "Link", "Testo"],
            style=Pack(flex=1),
            on_select=self._on_select,
        )
        self.main_box.add(self.table)

        # --- Barra azioni ---
        actions = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))

        self.btn_edit = toga.Button(
            "✏️  Modifica",
            on_press=self._edit_record,
            style=Pack(margin=5, background_color="#043a55", color="white")
        )
        self.btn_edit.enabled = False
        actions.add(self.btn_edit)

        self.btn_delete = toga.Button(
            "🗑️  Elimina",
            on_press=self._delete_record,
            style=Pack(margin=5, background_color="#8b0000", color="white")
        )
        self.btn_delete.enabled = False
        actions.add(self.btn_delete)

        self.main_box.add(actions)

        # --- Status bar ---
        self.status_label = toga.Label(
            "Pronto",
            style=Pack(margin=5, font_size=11, color="#666666")
        )
        self.main_box.add(self.status_label)

        # --- Finestra ---
        self.main_window = toga.MainWindow(title="Gestione Sliders")
        self.main_window.content = self.main_box
        self.main_window.show()

        # Carica i dati iniziali
        self._load_data()
        self._show_status(f"Connesso a {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")

    def _load_data(self):
        """Carica i dati nella tabella"""
        try:
            rows = fetch_all()
            self.table.data = rows
            self._show_status(f"Caricati {len(rows)} record")
        except Exception as e:
            self._show_error(f"Errore caricamento: {e}")

    def _refresh(self, widget):
        """Ricarica la tabella"""
        self._load_data()

    def _on_select(self, table, **kwargs):
        """Abilita/disabilita pulsanti in base alla selezione"""
        print(f"DEBUG _on_select: table={table}, kwargs={kwargs}")
        if table.selection is not None:
            self.selected_row = table.selection
            self.btn_edit.enabled = True
            self.btn_delete.enabled = True
            print(f"DEBUG selected_row: {self.selected_row}")
        else:
            self.selected_row = None
            self.btn_edit.enabled = False
            self.btn_delete.enabled = False

    def _new_record(self, widget):
        """Apre dialog per nuovo record"""
        self._open_dialog("Nuovo Record", None)

    def _edit_record(self, widget):
        """Apre dialog per modifica record selezionato"""
        if hasattr(self, 'selected_row') and self.selected_row:
            # Converti Row in tupla per compatibilità con il resto del codice
            row = self._row_to_tuple(self.selected_row)
            self._open_dialog("Modifica Record", row)


    def _open_dialog(self, title, existing_data):
        """Apre il dialog di inserimento/modifica"""
        def on_save(data):
            self.main_window.content = self.main_box
            if data is None:
                self._show_status("Operazione annullata")
                return
            try:
                if existing_data:
                    record_id = existing_data[0]
                    update_record(record_id, data)
                    self._show_status(f"Record {record_id} aggiornato")
                else:
                    insert_record(data)
                    self._show_status("Nuovo record inserito")
                self._load_data()
            except Exception as e:
                self._show_error(f"Errore: {e}")

        dialog = RecordDialog(title, on_save, existing_data)
        self.main_window.content = dialog.box

    def _delete_record(self, widget):
        """Elimina il record selezionato con conferma"""
        if hasattr(self, 'selected_row') and self.selected_row:
            row = self.selected_row
            record_id = row.id if hasattr(row, 'id') else row[0]
            titolo = row.titolo if hasattr(row, 'titolo') else (row[4] or "senza titolo")

            # Dialog di conferma semplice
            confirm_box = toga.Box(style=Pack(direction=COLUMN, margin=30, alignment=CENTER))

            confirm_box.add(toga.Label(
                f"Eliminare il record #{record_id}?\n\"{titolo}\"",
                style=Pack(font_size=16, margin_bottom=20)
            ))

            btn_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))

            def do_delete(w):
                try:
                    delete_record(record_id)
                    self._show_status(f"Record {record_id} eliminato")
                    self._load_data()
                except Exception as e:
                    self._show_error(f"Errore eliminazione: {e}")
                self.main_window.content = self.main_box

            def do_cancel(w):
                self.main_window.content = self.main_box

            btn_yes = toga.Button(
                "Sì, elimina",
                on_press=do_delete,
                style=Pack(margin=5, background_color="#8b0000", color="white")
            )
            btn_no = toga.Button(
                "No, annulla",
                on_press=do_cancel,
                style=Pack(margin=5)
            )
            btn_box.add(btn_yes)
            btn_box.add(btn_no)
            confirm_box.add(btn_box)

            self.main_window.content = confirm_box

    def _row_to_tuple(self, row):
        """Converte un oggetto Row in una tupla ordinata"""
        return (
            getattr(row, 'id', None),
            getattr(row, 'codice', None),
            getattr(row, 'codice_2', None),
            getattr(row, 'immagine', None),
            getattr(row, 'titolo', None),
            getattr(row, 'caption', None),
            getattr(row, 'link', None),
            getattr(row, 'testo', None),
        )

    def _show_status(self, message):
        """Mostra messaggio nella barra di stato"""
        self.status_label.text = message

    def _show_error(self, message):
        """Mostra errore nella barra di stato"""
        self.status_label.text = f"❌ {message}"
        self.status_label.style.color = "red"


# ============================================================
# AVVIO
# ============================================================
def main():
    # Verifica dipendenza
    try:
        import psycopg2
    except ImportError:
        print("ERRORE: psycopg2 non installato. Esegui: pip install psycopg2-binary")
        sys.exit(1)

    return SlidersManagerApp(
        formal_name="Gestione Sliders",
        app_id="com.example.sliders_manager",
        app_name="sliders_manager",
    )


if __name__ == "__main__":
    main().main_loop()
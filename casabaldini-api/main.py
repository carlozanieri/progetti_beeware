from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from config import DATABASE_URL, API_HOST, API_PORT


# ==========================
# MODELLI PYDANTIC
# ==========================

class Slider(BaseModel):
    id: int
    img: str
    titolo: str
    testo: str
    caption: str

class Menu(BaseModel):
    id: int
    codice: str
    radice: str
    livello: int
    titolo: str
    link: str
    ordine: int
    tipopage: str

class FullMenu(BaseModel):
    parent: Menu
    children: list[Menu]

class Foods(BaseModel):
    id: int
    codice: str
    img: str
    titolo: str
    descrizione: str
    link: str
    width: str
    height: str
    indirizzo: str
    telefono: str
    apiedi: str

class Links(BaseModel):
    id: int
    codice: str
    img: str
    titolo: str
    descrizione: str
    link: str
    height: str
    width: str


# ==========================
# CONNESSIONE DATABASE
# ==========================

def get_db():
    """Restituisce una connessione al database."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


# ==========================
# APP FASTAPI
# ==========================

app = FastAPI(title="CasaBaldini API", version="1.0.0")

# CORS permissivo (come nella versione Rust)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File statici (immagini)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================
# ENDPOINTS
# ==========================

@app.get("/api/v1/slider", response_model=list[Slider])
def get_sliders(dir: Optional[str] = Query(default="index")):
    """
    Restituisce gli slider filtrati per sezione (dir).
    Se dir == 'index' filtra per codice, altrimenti per codice2.
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if dir == "index":
                cur.execute(
                    "SELECT id, img, titolo, testo, caption FROM sliders WHERE codice = %s",
                    (dir,)
                )
            else:
                cur.execute(
                    "SELECT id, img, titolo, testo, caption FROM sliders WHERE codice2 = %s",
                    (dir,)
                )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/v1/menu", response_model=list[FullMenu])
def get_menu():
    """Restituisce il menu completo con padre e figli."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Carica i menu padre
            cur.execute(
                "SELECT id, codice, radice, livello, titolo, link, ordine, tipopage "
                "FROM menu WHERE livello=2 AND attivo=1 ORDER BY ordine"
            )
            parents = [dict(row) for row in cur.fetchall()]

            # Carica tutti i sottomenu
            cur.execute(
                "SELECT id, codice, radice, livello, titolo, link, ordine, tipopage "
                "FROM submenu WHERE attivo=1 ORDER BY ordine"
            )
            all_sub = [dict(row) for row in cur.fetchall()]

        # Costruisce la struttura padre/figli
        result = []
        for parent in parents:
            children = [
                s for s in all_sub
                if s["radice"].strip() == parent["codice"].strip()
            ]
            result.append({
                "parent": parent,
                "children": children
            })

        return result
    finally:
        conn.close()


@app.get("/api/v1/foods", response_model=list[Foods])
def get_foods():
    """Restituisce la lista dei ristoranti."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, codice, img, titolo, descrizione, link, "
                "width, height, indirizzo, telefono, apiedi FROM food"
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/v1/links", response_model=list[Links])
def get_links():
    """Restituisce la lista dei link utili."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, codice, img, titolo, descrizione, link, height, width FROM links"
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


# ==========================
# AVVIO
# ==========================

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 API CasaBaldini partita su http://localhost:{API_PORT}")
    print(f"📂 Immagini servite su http://localhost:{API_PORT}/static/img/")
    print(f"📖 Documentazione su http://localhost:{API_PORT}/docs")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
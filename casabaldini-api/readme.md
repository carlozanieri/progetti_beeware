# CasaBaldini API - FastAPI

Riscrittura in Python/FastAPI dell'API service originalmente scritta in Rust/Axum.

## Struttura del progetto

```
casabaldini_api/
├── main.py          # API principale
├── config.py        # Parametri di connessione (NON committare su git)
├── requirements.txt # Dipendenze Python
├── static/          # File statici (immagini)
│   └── img/
│       ├── index/
│       ├── camere/
│       ├── lasala/
│       ├── ilpaese/
│       ├── links/
│       └── ristoranti/
└── README.md
```

## Installazione

```bash
pip install -r requirements.txt
```

## Configurazione

Modifica `config.py` con i parametri reali del tuo database:

```python
DB_HOST = "57.131.31.228"
DB_PORT = 5432
DB_NAME = "casabaldini"
DB_USER = "tuo_utente"
DB_PASSWORD = "tua_password"
```

## Avvio

```bash
python main.py
```

Oppure direttamente con uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 7878 --reload
```

## Endpoints

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | /api/v1/slider?dir=index | Slider per sezione |
| GET | /api/v1/menu | Menu completo |
| GET | /api/v1/foods | Lista ristoranti |
| GET | /api/v1/links | Link utili |
| GET | /static/img/{dir}/{file} | File statici |
| GET | /docs | Documentazione Swagger automatica |

## Note

- La porta di default è 3333 (stessa dell'API Rust)
- CORS è permissivo (come nell'originale Rust)
- La cartella `static/` deve essere nella stessa directory di `main.py`
- Copia le immagini dalla cartella `static/` dell'API Rust
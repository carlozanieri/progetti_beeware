# Configurazione database e parametri generali
# Sostituisci con i tuoi parametri reali

DB_HOST = "57.131.31.228"
DB_PORT = 5432
DB_NAME = "casabaldini"
DB_USER = "carlo"
DB_PASSWORD = "treX39"

# URL di connessione completo
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Porta su cui gira l'API
API_PORT = 3333
API_HOST = "0.0.0.0"
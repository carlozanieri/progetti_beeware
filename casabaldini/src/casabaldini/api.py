"""Chiamate API verso il backend Rust"""

import httpx

API_BASE = "https://json.casabaldini.eu/api/v1"
IMG_BASE = "https://json.casabaldini.eu/static/img"


async def fetch_menu():
    """Recupera la struttura del menu"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{API_BASE}/menu")
        response.raise_for_status()
        return response.json()


async def fetch_slider(dir_val):
    """Recupera gli slider per una sezione"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{API_BASE}/slider", params={"dir": dir_val})
        response.raise_for_status()
        return response.json()


async def fetch_links():
    """Recupera i link utili"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{API_BASE}/links")
        response.raise_for_status()
        return response.json()


async def fetch_foods():
    """Recupera l'elenco dei ristoranti"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{API_BASE}/foods")
        response.raise_for_status()
        return response.json()


async def download_image(client, url):
    """Scarica un'immagine e ritorna i dati binari"""
    response = await client.get(url)
    response.raise_for_status()
    return response.content
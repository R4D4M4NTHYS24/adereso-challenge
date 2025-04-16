# api_fetchers.py

import requests
import urllib3
import re
from functools import lru_cache
from typing import Tuple, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Sesiones HTTP persistentes
session_poke = requests.Session()
session_poke.verify = False
session_sw = requests.Session()
session_sw.verify = False

TIMEOUT = 2  # segundos

# Caches de entidad completas
pokemon_cache = {}
people_cache = {}
planet_cache = {}

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def normalize_pokemon_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[\.']", "", name)
    name = name.replace("♀", "-f").replace("♂", "-m")
    name = re.sub(r"\s+", "-", name)
    # Casos especiales
    name = name.replace("mister-mime", "mr-mime")
    return name

def normalize_swapi_name(name: str) -> str:
    name = name.strip()
    # Eliminar prefijos honoríficos
    for p in ["General ", "Captain ", "Admiral ", "Master ", "Senator ", "Darth "]:
        if name.startswith(p):
            name = name[len(p):]
    # Correcciones de guion
    replacements = {"Obi Wan": "Obi-Wan", "Qui Gon": "Qui-Gon"}
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name

def get_pokemon(name: str) -> dict:
    norm = normalize_pokemon_name(name)
    if norm in pokemon_cache:
        return pokemon_cache[norm]
    url = f"https://pokeapi.co/api/v2/pokemon/{norm}"
    try:
        r = session_poke.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        pokemon_cache[norm] = {
            "base_experience": data.get("base_experience"),
            "height": data.get("height"),
            "weight": data.get("weight"),
        }
        return pokemon_cache[norm]
    except Exception:
        return {}

def fetch_swapi_entity(name: str) -> Tuple[Optional[str], dict]:
    """
    Retorna:
      - ("people", data)   si lo encontró como personaje
      - ("planets", data)  si lo encontró como planeta
      - (None, {})         si no encontró nada
    """
    norm = normalize_swapi_name(name)
    # Intentar persona
    r = session_sw.get(f"https://swapi.dev/api/people/?search={norm}", timeout=TIMEOUT)
    if r.ok:
        results = r.json().get("results", [])
        for c in results:
            if c.get("name", "").lower() == norm.lower():
                return "people", c
        if results:
            return "people", results[0]
    # Intentar planeta
    r = session_sw.get(f"https://swapi.dev/api/planets/?search={norm}", timeout=TIMEOUT)
    if r.ok:
        results = r.json().get("results", [])
        for p in results:
            if p.get("name", "").lower() == norm.lower():
                return "planets", p
        if results:
            return "planets", results[0]
    return None, {}

def get_swapi(name: str) -> dict:
    # Verificar cachés primero
    if name in people_cache:
        return people_cache[name]
    if name in planet_cache:
        return planet_cache[name]

    kind, data = fetch_swapi_entity(name)
    if not data:
        return {}

    if kind == "people":
        entry = {
            "name": data.get("name"),
            "height": safe_float(data.get("height")),
            "mass": safe_float(data.get("mass")),
            "homeworld": data.get("homeworld"),
        }
        people_cache[name] = entry
    else:
        entry = {
            "name": data.get("name"),
            "rotation_period": safe_float(data.get("rotation_period")),
            "orbital_period": safe_float(data.get("orbital_period")),
            "diameter": safe_float(data.get("diameter")),
            "surface_water": safe_float(data.get("surface_water")),
            "population": safe_float(data.get("population")),
        }
        planet_cache[name] = entry

    return entry

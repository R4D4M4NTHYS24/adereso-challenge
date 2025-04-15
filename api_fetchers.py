# api_fetchers.py
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_pokemon(name: str) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        return {
            "base_experience": data.get("base_experience"),
            "height": data.get("height"),
            "weight": data.get("weight"),
        }
    except:
        return {}  # Silencioso


def get_starwars_character(name: str) -> dict:
    url = f"https://swapi.dev/api/people/?search={name}"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return {}
        character = results[0]
        return {
            "name": character.get("name"),
            "height": safe_float(character.get("height", 0)),
            "mass": safe_float(character.get("mass", 0)),
            "homeworld": character.get("homeworld")
        }
    except Exception as e:
        print(f"[❌] Error al obtener personaje {name}: {e}")
        return {}

def get_starwars_planet(name: str) -> dict:
    url = f"https://swapi.dev/api/planets/?search={name}"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return {}
        planet = results[0]
        return {
            "name": planet.get("name"),
            "rotation_period": safe_float(planet.get("rotation_period", 0)),
            "orbital_period": safe_float(planet.get("orbital_period")),
            "diameter": safe_float(planet.get("diameter", 0)),
            "surface_water": safe_float(planet.get("surface_water", 0)),
            "population": safe_float(planet.get("population", 0)),
        }
    except Exception as e:
        print(f"[❌] Error al obtener planeta {name}: {e}")
        return {}

import requests, os
from dotenv import load_dotenv
import re
from utils import CALL_RE

load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")
CHAT_URL = "https://recruiting.adere.so/chat_completion"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
Eres un asistente que convierte enunciados en español sobre Star Wars (planetas, personajes) y Pokémon
en expresiones aritméticas usando:
  • swapi("Nombre","atributo") para datos SWAPI
  • pokeapi("Nombre","atributo") para datos PokéAPI

Reglas:
- Usa comillas dobles y paréntesis exactos.
- Normaliza nombres: "Mr. Mime"→"mr-mime", "Nidoran hembra"→"nidoran-f", "General Grievous"→"Grievous", etc.
- Campos: altura→height, masa/peso (SW)→mass, peso (PKM)→weight, diámetro→diameter, población/habitantes→population, experience_base→base_experience, surface_water→surface_water.
- Solo operaciones + - * / y números si se mencionan constantes.
- Responde SOLO con la expresión sin texto adicional.

Ejemplos:
P: ¿Cuál es el peso de Pikachu multiplicado por el diámetro de Yavin IV?
R: pokeapi("pikachu","weight") * swapi("Yavin IV","diameter")

P: ¿Qué resulta de la altura de Obi Wan Kenobi menos la de Yoda?
R: swapi("Obi-Wan Kenobi","height") - swapi("Yoda","height")

P: Dame el doble de la masa de Darth Vader.
R: 2 * swapi("Darth Vader","mass")
"""

def interpretar_enunciado(enunciado: str) -> str:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": enunciado}
        ],
        "temperature": 0
    }
    try:
        r = requests.post(CHAT_URL, headers=HEADERS, json=payload, timeout=5)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"].strip()
        # Validación básica
        if CALL_RE.search(txt):
            return txt
    except Exception:
        pass
    return None

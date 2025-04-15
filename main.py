# main.py
import re
import os
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado
from api_fetchers import get_pokemon, get_starwars_character, get_starwars_planet
from utils import construir_contexto, evaluar_expresion, redondear_resultado

# Cargar token
load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")

BASE_URL = "https://recruiting.adere.so/challenge"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def get_test_problem():
    try:
        response = requests.get(f"{BASE_URL}/test", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[❌] Error al obtener el problema de prueba: {e}")
        return None


def detectar_tipo_entidad(nombre: str) -> str:
    """
    Detecta si una variable es un Pokémon, un personaje o un planeta,
    intentando primero con PokéAPI, luego con SWAPI (personaje y planeta).
    """
    try:
        poke = get_pokemon(nombre)
        if poke and poke.get("base_experience") is not None:
            return "pokemon"
    except:
        pass

    try:
        character = get_starwars_character(nombre)
        if character and character.get("mass") is not None:
            return "character"
    except:
        pass

    try:
        planet = get_starwars_planet(nombre)
        if planet and planet.get("diameter") is not None:
            return "planet"
    except:
        pass

    return "desconocido"



def obtener_datos_de_variables(variables: list) -> dict:
    datos = {}
    for var in variables:
        nombre = var.split(".")[0]
        if nombre in datos:
            continue

        tipo = detectar_tipo_entidad(nombre)
        if tipo == "pokemon":
            datos[nombre] = get_pokemon(nombre)
        elif tipo == "character":
            datos[nombre] = get_starwars_character(nombre)
        elif tipo == "planet":
            datos[nombre] = get_starwars_planet(nombre)
        else:
            print(f"[⚠️] Tipo desconocido para {nombre}")
    return datos


def main():
    print("🚀 Ejecutando flujo completo de resolución...\n")

    while True:
        problem = get_test_problem()
        if not problem:
            continue

        print("🧩 Enunciado:")
        print(problem["problem"], "\n")

        print("🤖 Interpretando enunciado con GPT...")
        interpretacion = interpretar_enunciado(problem["problem"])
        if not interpretacion:
            continue

        expression = interpretacion.get("expression")
        variables = interpretacion.get("variables", [])

        matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.', expression)
        variables = list(set(matches))
        if not variables:
            print("[⚠️] No se detectaron variables válidas. Saltando...\n")
            continue

        print("\n✅ Fórmula generada:")
        print(expression)
        print("📦 Variables:", variables)

        print("\n🔍 Obteniendo datos reales de APIs...")
        datos = obtener_datos_de_variables(variables)
        contexto = construir_contexto(variables, datos)

        print("\n📐 Evaluando expresión...")
        resultado = evaluar_expresion(expression, contexto)
        resultado_final = redondear_resultado(resultado)

        if resultado_final is None:
            print("\n[🟡] Este problema parece ser erróneo. Pasamos al siguiente.\n")
            continue  # <<--- Aquí el autoloop
        else:
            print(f"\n🎯 Resultado final: {resultado_final}")
            break  # <<--- Salimos del loop cuando el resultado es válido




if __name__ == "__main__":
    main()

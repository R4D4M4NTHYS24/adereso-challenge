# production_run.py

import os
import re
import time
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado
from api_fetchers import get_pokemon, get_starwars_character, get_starwars_planet
from utils import construir_contexto, evaluar_expresion, redondear_resultado

# Cargar token
load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")

BASE_URL_START = "https://recruiting.adere.so/challenge/start"
BASE_URL_SOLUTION = "https://recruiting.adere.so/challenge/solution"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

CUTOFF_SECONDS = 8


def iniciar_test_real():
    try:
        response = requests.get(BASE_URL_START, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[❌] Error al iniciar test real: {e}")
        return None


def enviar_solucion(problem_id: str, answer: float):
    try:
        payload = {
            "problem_id": problem_id,
            "answer": answer
        }
        response = requests.post(BASE_URL_SOLUTION, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[❌] Error al enviar solución: {e}")
        return None


def detectar_tipo_entidad(nombre: str) -> str:
    try:
        if (poke := get_pokemon(nombre)) and poke.get("base_experience") is not None:
            return "pokemon"
    except:
        pass
    try:
        if (char := get_starwars_character(nombre)) and char.get("mass") is not None:
            return "character"
    except:
        pass
    try:
        if (planet := get_starwars_planet(nombre)) and planet.get("diameter") is not None:
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
    print("🔐 Ejecutando en modo PRODUCCIÓN...")
    print("🚀 Iniciando test oficial de 3 minutos...\n")
    start_time = time.time()
    respuestas_correctas = 0

    while True:
        tiempo_transcurrido = time.time() - start_time
        tiempo_restante = 180 - tiempo_transcurrido

        if tiempo_restante <= 0:
            print("\n⏹️ Tiempo agotado: 180 segundos.")
            break

        if tiempo_restante <= CUTOFF_SECONDS:
            print(f"\n⏹️ Tiempo restante ({tiempo_restante:.2f} seg) menor al límite de seguridad ({CUTOFF_SECONDS} seg). No se inicia nuevo problema.")
            break

        problem = iniciar_test_real()
        if not problem:
            continue

        problem_id = problem.get("id")
        print("\n🧩 Enunciado:")
        print(problem["problem"])

        interpretacion = interpretar_enunciado(problem["problem"])
        if not interpretacion:
            continue

        expression = interpretacion.get("expression")
        matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.', expression)
        variables = list(set(matches))

        print("\n✅ Fórmula generada:")
        print(expression)
        print("📦 Variables:", variables)

        datos = obtener_datos_de_variables(variables)
        contexto = construir_contexto(variables, datos)

        resultado = evaluar_expresion(expression, contexto)
        resultado_final = redondear_resultado(resultado)

        if resultado_final is None:
            print("[🟡] Problema inválido o con datos inconsistentes. Saltando...\n")
            continue

        print(f"🎯 Resultado final: {resultado_final}")

        respuesta = enviar_solucion(problem_id, resultado_final)
        if respuesta and respuesta.get("status") == "success":
            respuestas_correctas += 1
        else:
            print("[❌] La API no confirmó si fue correcta. Continuamos...")

    print("\n⏱️ Tiempo finalizado.")
    print(f"\n✅ Respuestas correctas en producción: {respuestas_correctas}")
    total_duracion = time.time() - start_time
    print(f"\n🕒 Duración real de la ejecución: {total_duracion:.2f} segundos")


if __name__ == "__main__":
    main()

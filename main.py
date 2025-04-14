# main.py
import os
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")

BASE_URL = "https://recruiting.adere.so/challenge"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def get_test_problem():
    """Llama al endpoint de práctica y devuelve el problema."""
    try:
        response = requests.get(f"{BASE_URL}/test", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[❌] Error al obtener el problema de prueba: {e}")
        return None


def main():
    print("🚀 Ejecutando test del desafío técnico Adereso...\n")

    problem = get_test_problem()

    if not problem:
        print("[⚠️] No se pudo obtener el problema.")
        return

    print("🧩 Enunciado:")
    print(problem["problem"], "\n")

    print("🤖 Interpretando enunciado con GPT...")
    interpretacion = interpretar_enunciado(problem["problem"])

    if interpretacion:
        print("\n✅ Fórmula generada:")
        print(interpretacion.get("expression", "[sin expresión]"))
        print("\n📦 Variables involucradas:")
        print(interpretacion.get("variables", []))
    else:
        print("[⚠️] No se pudo interpretar el enunciado con GPT.")


if __name__ == "__main__":
    main()

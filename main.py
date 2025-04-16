# main.py
import os
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado
from utils import evaluar_expresion, redondear_resultado

load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")
BASE_URL = "https://recruiting.adere.so/challenge"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_test_problem():
    try:
        response = requests.get(f"{BASE_URL}/test", headers=HEADERS, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[❌] Error al obtener el problema de prueba: {e}")
        return None

def main():
    print("🚀 Ejecutando flujo completo de resolución...\n")

    while True:
        problem = get_test_problem()
        if not problem:
            continue

        print("🧩 Enunciado:")
        print(problem["problem"], "\n")

        print("🤖 Interpretando enunciado con GPT...")
        expression = interpretar_enunciado(problem["problem"])
        if not expression:
            continue

        print("\n✅ Expresión generada:")
        print(expression)

        print("\n📐 Evaluando expresión...")
        resultado = evaluar_expresion(expression)
        resultado_final = redondear_resultado(resultado)

        if resultado_final is None:
            print("\n[🟡] Este problema parece ser erróneo. Pasamos al siguiente.\n")
            continue
        else:
            print(f"\n🎯 Resultado final: {resultado_final}")
            break

if __name__ == "__main__":
    main()

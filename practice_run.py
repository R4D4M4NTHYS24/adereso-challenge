import os
import time
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado
from utils import evaluar_expresion, redondear_resultado

load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")
BASE_URL = "https://recruiting.adere.so/challenge/test"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
CUTOFF = 3  # segundos de reserva para no comenzar un nuevo problema si queda menos

# Activa/desactiva el logging detallado
VERBOSE = False

def get_problem():
    try:
        r = requests.get(BASE_URL, headers=HEADERS, timeout=1.5)
        r.raise_for_status()
        return r.json()
    except Exception:
        if VERBOSE:
            print("[⚠] Error al obtener problema, reintentando...")
        return None

def main():
    if VERBOSE:
        print(f"🚀 Iniciando práctica 3 minutos (verbose={VERBOSE})\n")
    start = time.time()
    correct = 0
    problema_n = 0

    while True:
        elapsed = time.time() - start
        remaining = 180 - elapsed
        if remaining < CUTOFF or remaining <= 0:
            break

        prob = get_problem()
        if not prob:
            continue

        problema_n += 1
        pid = prob.get("id")
        texto = prob.get("problem", "")

        if VERBOSE:
            print(f"\n🧩 Problema #{problema_n} (id: {pid}):")
            print(texto)

        # 1) Interpretación
        expr = interpretar_enunciado(texto)
        if not expr:
            if VERBOSE: print("[⚠] No se pudo generar expresión DSL, salto problema.")
            continue
        if VERBOSE: print(f"✅ Expresión DSL: {expr}")

        # 2) Evaluación
        try:
            resultado_crudo = evaluar_expresion(expr)
        except Exception as e:
            if VERBOSE: print(f"[❌] Error interno al evaluar DSL: {e}")
            continue

        if resultado_crudo is None:
            if VERBOSE: print("[🟡] Resultado crudo None, salto problema.")
            continue
        if VERBOSE: print(f"🔢 Resultado crudo: {resultado_crudo}")

        # 3) Redondeo
        resultado_final = redondear_resultado(resultado_crudo)
        if resultado_final is None:
            if VERBOSE: print("[🟡] No se pudo redondear, salto problema.")
            continue
        if VERBOSE: print(f"🎯 Resultado redondeado: {resultado_final}")

        # 4) Contar acierto
        correct += 1
        if VERBOSE: print(f"✅ Acierto # {correct}")

    total_time = time.time() - start
    print(f"\n⏱️ Práctica finalizada. Aciertos: {correct} en {total_time:.1f}s")

if __name__ == "__main__":
    main()

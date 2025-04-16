# production_run.py
import os
import time
import requests
from dotenv import load_dotenv
from gpt_interpreter import interpretar_enunciado
from utils import evaluar_expresion, redondear_resultado

load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

START_URL = "https://recruiting.adere.so/challenge/start"
SOLVE_URL = "https://recruiting.adere.so/challenge/solution"

# Reserva de tiempo al final (segundos)
CUTOFF = 5

# Logging detallado (desactívalo en real para ahorrar I/O)
VERBOSE = False

def main():
    if VERBOSE:
        print(f"🚀 Iniciando prueba oficial (verbose={VERBOSE})\n")
    start_ts = time.time()
    aciertos = 0
    intento = 0

    # 1️⃣ Iniciar la prueba real
    resp = requests.get(START_URL, headers=HEADERS, timeout=2)
    resp.raise_for_status()
    problema = resp.json()

    # 2️⃣ Loop principal
    while True:
        elapsed = time.time() - start_ts
        if elapsed >= 180 or (180 - elapsed) < CUTOFF:
            break

        pid = problema.get("id")
        texto = problema.get("problem", "")

        if VERBOSE:
            intento += 1
            print(f"\n🧩 Problema #{intento} (id: {pid}):")
            print(texto)

        # Interpretar
        expr = interpretar_enunciado(texto)
        if not expr:
            if VERBOSE:
                print("[⚠] No DSL, salto.")
            # Aún debemos llamar al endpoint para avanzar:
            problema = {}  # forzar next GET
        else:
            if VERBOSE:
                print(f"✅ DSL: {expr}")

            # Evaluar
            try:
                raw = evaluar_expresion(expr)
            except Exception as e:
                raw = None
                if VERBOSE:
                    print(f"[❌] Error eval: {e}")

            if raw is None:
                if VERBOSE:
                    print("[🟡] Resultado crudo inválido, salto.")
            else:
                if VERBOSE:
                    print(f"🔢 Crudo: {raw}")

                # Redondear
                final = redondear_resultado(raw)
                if final is None:
                    if VERBOSE:
                        print("[🟡] No redondeable, salto.")
                else:
                    if VERBOSE:
                        print(f"🎯 Final: {final}")

                    # Enviar solución
                    payload = {"problem_id": pid, "answer": final}
                    post = requests.post(SOLVE_URL, headers=HEADERS, json=payload, timeout=2)
                    # Si el server indica fin (código distinto de 200), rompemos
                    if post.status_code != 200:
                        if VERBOSE:
                            print(f"[ℹ] Test terminado (status {post.status_code}).")
                        break

                    problema = post.json()
                    aciertos += 1
                    if VERBOSE:
                        print(f"✅ Acierto #{aciertos}")

        # En caso de salto sin POST (DSL roto), pedimos manualmente el siguiente
        if not problema.get("id"):
            try:
                resp = requests.get(START_URL, headers=HEADERS, timeout=2)
                resp.raise_for_status()
                problema = resp.json()
            except:
                if VERBOSE:
                    print("[⚠] No pude avanzar problema, reintentando...")

    total = time.time() - start_ts
    print(f"\n⏱️ Prueba finalizada. Aciertos: {aciertos} en {total:.1f}s")

if __name__ == "__main__":
    main()

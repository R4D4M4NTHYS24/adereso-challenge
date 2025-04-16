# production_run.py  (logging compacto)
import os, time, json, requests, math
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from gpt_interpreter import interpretar_enunciado
from utils           import evaluar_expresion, redondear_resultado

load_dotenv()
TOKEN   = os.getenv("ADERESO_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

START_URL = "https://recruiting.adere.so/challenge/start"
SOLVE_URL = "https://recruiting.adere.so/challenge/solution"

TIMEOUT   = 5.0   # todos los GET/POST
CUTOFF    = 8     # reserva final
VERBOSE   = True  # True = compacto ; False = silencio total
LOG_EVERY = 10    # imprime 1 de cada 10 problemas

# ─────────────────────────────────────────────────────────────
def dlog(msg, n=None):
    """Log compacto controlado por VERBOSE & LOG_EVERY"""
    if not VERBOSE:
        return
    if n is None or n % LOG_EVERY == 0:
        print(msg)

def safe_post(payload, retries=1):
    for i in range(retries + 1):
        try:
            return requests.post(SOLVE_URL, headers=HEADERS,
                                 json=payload, timeout=TIMEOUT)
        except ReadTimeout:
            if i == retries:
                raise
            dlog("  ⏳ POST timeout, reintentando…")

def main():
    try:
        r = requests.get(START_URL, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        problema = r.json()            # {'id':..,'problem':..}
    except Exception as e:
        print("❌ No se pudo iniciar:", e)
        return

    t0          = time.time()
    aciertos    = 0
    total_count = 0

    while time.time() - t0 < 180 - CUTOFF:
        pid, texto = problema["id"], problema["problem"]
        total_count += 1
        dlog(f"\n🧩 #{total_count} id={pid[:6]}… {texto[:70]}…", total_count)

        # ── interpretar y evaluar ───────────────────────────
        expr = interpretar_enunciado(texto)
        raw  = None
        if expr:
            try:
                raw = evaluar_expresion(expr)
            except Exception as e:
                dlog(f"  ⚠️ Eval error: {e}", total_count)

        final  = redondear_resultado(raw) if raw is not None else None
        answer = final if final is not None else 0

        # ── POST solución ──────────────────────────────────
        try:
            post = safe_post({"problem_id": pid, "answer": answer}, retries=1)
        except Exception as e:
            print("❌ POST fallido:", e)
            break

        if post.status_code == 401:
            print("⚠️  Token inválido/expirado.")
            break

        data = post.json()
        nxt  = data.get("next_problem")
        if not nxt:                     # terminó la sesión
            dlog(f"ℹ️ Fin servidor: {data}")
            break

        if final is not None:           # respuesta correcta
            aciertos += 1
            dlog(f"  ✅ Aciertos parciales: {aciertos}", total_count)

        problema = nxt                  # avanzar

    print(f"\n⏱️ Terminado. Correctas: {aciertos}  |  Procesadas: {total_count}")

if __name__ == "__main__":
    main()

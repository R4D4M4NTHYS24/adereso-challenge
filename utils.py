# utils.py

from simpleeval import SimpleEval

def construir_contexto(variables: list, objetos: dict) -> dict:
    """
    Construye un contexto jerárquico para simpleeval, por ejemplo:
    dugtrio.base_experience → objetos["dugtrio"]["base_experience"]
    """
    contexto = {}
    for nombre, atributos in objetos.items():
        contexto[nombre] = atributos  # ejemplo: contexto["dugtrio"] = { "base_experience": 170 }
    return contexto


def evaluar_expresion(expression: str, contexto: dict) -> float:
    """
    Evalúa una expresión matemática con un contexto seguro usando simpleeval.
    """
    try:
        s = SimpleEval(names=contexto)
        return s.eval(expression)
    except Exception as e:
        print(f"[❌] Error al evaluar expresión: {e}")
        return None

def redondear_resultado(valor: float) -> float:
    """
    Redondea el resultado a 10 decimales, devolviendo float
    pero con precisión visible al convertirlo a string.
    """
    try:
        return float(format(valor, ".10f"))
    except Exception as e:
        print(f"[❌] Error al redondear: {e}")
        return None


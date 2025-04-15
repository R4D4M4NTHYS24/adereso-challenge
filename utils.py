# utils.py

from simpleeval import SimpleEval

def construir_contexto(variables: list, objetos: dict) -> dict:
    """
    Construye un contexto jerárquico con objetos anidados:
    por ejemplo: luke.mass → objetos['luke']['mass']
    """
    contexto = {}
    for nombre in variables:
        if nombre not in objetos:
            continue
        partes = nombre.split(".")
        if len(partes) == 1:
            contexto[nombre] = objetos[nombre]
        else:
            actual = contexto
            for parte in partes[:-1]:
                actual = actual.setdefault(parte, {})
            actual[partes[-1]] = objetos[nombre]
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
    Redondea el resultado a 10 decimales como lo exige la prueba.
    """
    try:
        return round(float(valor), 10)
    except Exception as e:
        print(f"[❌] Error al redondear: {e}")
        return None

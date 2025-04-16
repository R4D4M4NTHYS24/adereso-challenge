import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from simpleeval import SimpleEval
from api_fetchers import get_pokemon, get_swapi

MAX_WORKERS = 10

# Expresión que detecta todas las llamadas swapi/pokeapi(...)
CALL_RE = re.compile(r'(swapi|pokeapi)\("([^"]+)",\s*"([^"]+)"\)')

def prefetch_datos(expression: str, timeout_per_call=1.5):
    """
    Extrae todas las llamadas únicas y las ejecuta concurrentemente,
    devolviendo un dict { (func,nombre,campo): valor }
    """
    calls = set(CALL_RE.findall(expression))
    resultados = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {}
        for func, name, field in calls:
            key = (func, name, field)
            if func == "swapi":
                futures[exe.submit(get_swapi, name)] = key
            else:
                futures[exe.submit(get_pokemon, name)] = key

        for fut in as_completed(futures, timeout=timeout_per_call * len(futures)):
            key = futures[fut]
            try:
                data = fut.result(timeout=timeout_per_call)
                if key[0] == "swapi":
                    resultados[key] = data.get(key[2])
                else:
                    resultados[key] = data.get(key[2])
            except Exception:
                resultados[key] = None
    return resultados

def evaluar_expresion(expression: str) -> float:
    datos = prefetch_datos(expression)
    def swapi_func(name, field):
        v = datos.get(("swapi", name, field))
        if v is None:
            raise ValueError(f"SWAPI: {name}.{field} no disponible")
        return v
    def pokeapi_func(name, field):
        v = datos.get(("pokeapi", name, field))
        if v is None:
            raise ValueError(f"PokeAPI: {name}.{field} no disponible")
        return v

    se = SimpleEval()
    se.functions.update({"swapi": swapi_func, "pokeapi": pokeapi_func})
    return se.eval(expression)

def redondear_resultado(valor: float) -> float:
    if valor is None:
        return None
    return float(f"{valor:.10f}")

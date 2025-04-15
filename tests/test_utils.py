# tests/test_utils.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import evaluar_expresion, redondear_resultado, construir_contexto

def test_evaluar_expresion_simple():
    contexto = {
        "luke": {"mass": 77},
        "vulpix": {"base_experience": 60}
    }
    expresion = "luke.mass * vulpix.base_experience"
    resultado = evaluar_expresion(expresion, contexto)
    assert resultado == 4620

def test_redondear_resultado_precision():
    valor = 3.141592653589793
    redondeado = redondear_resultado(valor)
    assert redondeado == 3.1415926536

def test_construir_contexto_basico():
    variables = ["luke.mass", "vulpix.base_experience"]
    objetos = {
        "luke.mass": 77,
        "vulpix.base_experience": 60
    }
    contexto = construir_contexto(variables, objetos)
    assert contexto["luke"]["mass"] == 77
    assert contexto["vulpix"]["base_experience"] == 60

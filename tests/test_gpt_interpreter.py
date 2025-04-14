# tests/test_gpt_interpreter.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gpt_interpreter import interpretar_enunciado

def test_interpretar_enunciado_retornar_dict_con_expression_y_variables():
    enunciado = (
        "Luke Skywalker está entrenando con el Pokémon Vulpix. "
        "Multiplica su masa por la experiencia base del Pokémon. "
        "¿Qué resultado obtienen juntos?"
    )

    resultado = interpretar_enunciado(enunciado)

    assert isinstance(resultado, dict), "La respuesta debe ser un diccionario"
    assert "expression" in resultado, "Debe contener la clave 'expression'"
    assert "variables" in resultado, "Debe contener la clave 'variables'"
    assert isinstance(resultado["variables"], list), "Las variables deben venir en una lista"

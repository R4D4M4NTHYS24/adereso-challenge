# gpt_interpreter.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("ADERESO_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

CHAT_URL = "https://recruiting.adere.so/chat_completion"

def interpretar_enunciado(enunciado: str) -> dict:
    """
    Envía el enunciado en lenguaje natural al endpoint de GPT
    y espera como respuesta una expresión matemática en formato evaluable.
    """

    prompt_sistema = (
        "Tu trabajo es convertir un enunciado en lenguaje natural en una expresión de Python.\n"
        "Devuelve solo un JSON válido con dos claves:\n"
        "- 'expression': una fórmula lista para evaluar (por ejemplo: 'luke.mass * vulpix.base_experience')\n"
        "- 'variables': una lista de los nombres de variables requeridas\n"
        "Ejemplo de salida válida:\n"
        "{\n"
        "  \"expression\": \"luke.mass * vulpix.base_experience\",\n"
        "  \"variables\": [\"luke\", \"vulpix\"]\n"
        "}\n"
        "No expliques nada. Solo responde con el JSON."
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": enunciado}
        ]
    }

    try:
        response = requests.post(CHAT_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        return eval(content)  # se espera un dict como {'expression': '...', 'variables': [...]}

    except Exception as e:
        print(f"[❌] Error al interpretar con GPT: {e}")
        return None

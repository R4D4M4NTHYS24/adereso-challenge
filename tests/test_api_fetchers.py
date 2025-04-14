# tests/test_api_fetchers.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_fetchers import get_pokemon, get_starwars_character, get_starwars_planet

def test_get_pokemon_vulpix():
    result = get_pokemon("vulpix")
    assert isinstance(result, dict)
    assert "base_experience" in result
    assert "weight" in result

def test_get_starwars_character_luke():
    result = get_starwars_character("Luke Skywalker")
    assert isinstance(result, dict)
    assert "mass" in result
    assert "height" in result

def test_get_starwars_planet_tatooine():
    result = get_starwars_planet("Tatooine")
    assert isinstance(result, dict)
    assert "diameter" in result
    assert "rotation_period" in result

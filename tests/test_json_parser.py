import pytest

from app.core.exceptions import OllamaServiceError
from app.utils.json_parser import safe_parse_json


def test_parses_clean_json():
    result = safe_parse_json('{"a": 1, "b": [1, 2, 3]}')
    assert result == {"a": 1, "b": [1, 2, 3]}


def test_parses_json_wrapped_in_markdown_fence():
    text = '```json\n{"a": 1}\n```'
    assert safe_parse_json(text) == {"a": 1}


def test_parses_json_with_surrounding_commentary():
    text = 'Sure, here is the JSON you asked for:\n{"a": 1}\nLet me know if you need more.'
    assert safe_parse_json(text) == {"a": 1}


def test_raises_on_truly_invalid_json():
    with pytest.raises(OllamaServiceError):
        safe_parse_json("this is not json at all")

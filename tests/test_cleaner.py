"""Unit tests for modules/cleaner.py"""

from modules.cleaner import normalize_text


def test_normalize_bullets_and_whitespace():
    raw = "• Developed API\n● Built database\n   - Cleaned data   "
    clean = normalize_text(raw)
    assert "- Developed API" in clean
    assert "- Built database" in clean
    assert "- Cleaned data" in clean


def test_normalize_hyphenated_line_breaks():
    raw = "Imple-\nmented microservice architec-\nture."
    clean = normalize_text(raw)
    assert "Implemented" in clean
    assert "architecture" in clean


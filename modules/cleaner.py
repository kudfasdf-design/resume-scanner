"""Text cleaner module for normalizing extracted resume text."""

import re
import unicodedata


def normalize_text(raw_text: str) -> str:
    """Normalize unicode, bullets, hyphens, and whitespace while preserving line structure."""
    if not raw_text:
        return ""

    # Normalize unicode to NFKC
    text = unicodedata.normalize("NFKC", raw_text)

    # Standardize bullet symbols to a common bullet "-"
    bullet_chars = r"[•●○◦■▪▫◆◇‣⁃–—\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]"
    text = re.sub(bullet_chars, " - ", text)

    # Fix hyphenated words broken across lines (e.g., "develop-\ning" -> "developing")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Replace non-breaking spaces and special spaces with standard space
    text = re.sub(r"[\u00A0\u1680\u180E\u2000-\u200B\u202F\u205F\u3000\uFEFF]", " ", text)

    # Clean multiple spaces per line, but keep newline structure
    lines = []
    for line in text.splitlines():
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Collapse more than two consecutive empty lines
    cleaned_text = "\n".join(lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()


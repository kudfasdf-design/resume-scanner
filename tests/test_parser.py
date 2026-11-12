"""Unit tests for modules/parser.py"""

import pytest
from modules.parser import validate_file, extract_text, UnsupportedFormatError, FileTooLargeError, ParseError


def test_validate_file_unsupported_format():
    with pytest.raises(UnsupportedFormatError):
        validate_file(b"content", "resume.txt")


def test_validate_file_too_large():
    large_bytes = b"0" * (6 * 1024 * 1024)
    with pytest.raises(FileTooLargeError):
        validate_file(large_bytes, "resume.pdf")


def test_validate_file_empty():
    with pytest.raises(ParseError):
        validate_file(b"", "resume.pdf")


def test_extract_text_docx(tmp_path):
    import docx
    doc_path = tmp_path / "test.docx"
    doc = docx.Document()
    doc.add_paragraph("Alex Morgan\nSoftware Engineer with experience in Python and React.")
    doc.save(str(doc_path))

    with open(doc_path, "rb") as f:
        text = extract_text(f.read(), "test.docx")
    assert "Alex Morgan" in text
    assert "Python" in text


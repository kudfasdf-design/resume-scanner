"""Parser module for file validation and text extraction from PDF and DOCX files."""

import io
from pathlib import Path
import pdfplumber
import docx
from config import MAX_FILE_BYTES, MAX_FILE_MB, ALLOWED_EXTENSIONS


class ParserError(Exception):
    """Base exception for parsing errors."""
    pass


class UnsupportedFormatError(ParserError):
    """Raised when file extension is not supported."""
    pass


class FileTooLargeError(ParserError):
    """Raised when file exceeds maximum allowed size."""
    pass


class ScannedPdfError(ParserError):
    """Raised when a PDF contains no extractable text (e.g. scanned image)."""
    pass


class ParseError(ParserError):
    """Raised when file content is corrupted or unreadable."""
    pass


def validate_file(file_bytes: bytes, filename: str) -> None:
    """Validate file extension and size constraints."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise UnsupportedFormatError(
            f"Unsupported file format '{ext}'. Allowed formats are: {allowed}."
        )

    if len(file_bytes) > MAX_FILE_BYTES:
        mb = len(file_bytes) / (1024 * 1024)
        raise FileTooLargeError(
            f"File size ({mb:.1f} MB) exceeds maximum allowed limit of {MAX_FILE_MB} MB."
        )

    if len(file_bytes) == 0:
        raise ParseError("The uploaded file is empty (0 bytes).")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF using pdfplumber."""
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                raise ParseError("The PDF file contains no pages.")
            for page in pdf.pages:
                page_text = page.extract_text(layout=True) or ""
                if page_text.strip():
                    text_parts.append(page_text)

        full_text = "\n\n".join(text_parts).strip()
        if len(full_text) < 50:
            raise ScannedPdfError(
                "Unable to extract text from PDF. The document appears to be a scanned image or empty. "
                "Please upload a text-based PDF or DOCX resume."
            )
        return full_text
    except (ScannedPdfError, ParseError):
        raise
    except Exception as e:
        raise ParseError(f"Failed to read PDF file: {str(e)}") from e


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from DOCX paragraphs and tables."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text_parts = []

        # Read paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                text_parts.append(text)

        # Read table cells
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    text_parts.append(" | ".join(row_cells))

        full_text = "\n".join(text_parts).strip()
        if len(full_text) < 30:
            raise ParseError("The DOCX document contains insufficient text content.")
        return full_text
    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse DOCX document: {str(e)}") from e


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Validate file and extract raw text."""
    validate_file(file_bytes, filename)
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise UnsupportedFormatError(f"Unsupported extension: {ext}")


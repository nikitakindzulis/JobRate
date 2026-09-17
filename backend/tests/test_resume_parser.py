import pytest

from app.services.resume_parser import extract_text


def test_extract_txt():
    content = "Python, FastAPI, SQL".encode("utf-8")
    assert extract_text("resume.txt", content) == "Python, FastAPI, SQL"


def test_unsupported_format_raises():
    with pytest.raises(ValueError):
        extract_text("resume.xyz", b"data")


def test_missing_extension_raises():
    with pytest.raises(ValueError):
        extract_text("resume", b"data")

"""
Unit tests for Comic (.cbz, .cbr) and ePub (.epub) Parsers (Phase 6).
Validates comic archive extraction, ComicInfo.xml metadata, and ePub chapter ingestion.
"""
import io
import zipfile
import pytest
from backend.parsers.comic_parser import parse_cbz, create_cbz_package
from backend.parsers.epub_parser import parse_epub
from backend.parsers.format_detector import detect_format


def test_format_detector_cbz_epub():
    assert detect_format("comic.cbz", b"PK\x03\x04") == "cbz"
    assert detect_format("comic.cbr", b"Rar!") == "cbr"
    assert detect_format("novel.epub", b"PK\x03\x04") == "epub"


def test_create_and_parse_cbz():
    frames = [
        {"heading": "INT. LAB - DAY", "description": "Dr. Vance inspects the vial.", "moment_summary": "Discovery"},
        {"heading": "EXT. ALLEY - NIGHT", "description": "Shadowy figures approach.", "moment_summary": "Ambush"},
    ]

    cbz_bytes = create_cbz_package("Cyberspace Noir", frames, metadata={"series": "Cyber Noir", "issue": "1"})
    assert isinstance(cbz_bytes, bytes)
    assert len(cbz_bytes) > 200

    parsed = parse_cbz(cbz_bytes)
    assert parsed["metadata"]["title"] == "Cyberspace Noir"
    assert parsed["metadata"]["series"] == "Cyber Noir"
    assert parsed["metadata"]["issue"] == "1"


def test_parse_epub():
    # Build a minimal valid epub zip in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0"?>
            <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                <rootfiles>
                    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
                </rootfiles>
            </container>"""
        )
        zf.writestr(
            "content.opf",
            """<?xml version="1.0" encoding="utf-8"?>
            <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
                <metadata>
                    <title>The Silent City</title>
                    <creator>Kirk LaSalle</creator>
                </metadata>
            </package>"""
        )
        zf.writestr(
            "chapter1.xhtml",
            """<html xmlns="http://www.w3.org/1999/xhtml">
            <head><title>Chapter 1</title></head>
            <body>
                <h1>Chapter 1: The Awakening</h1>
                <p>The fog settled heavy across the deserted harbor as Vance adjusted his collar.</p>
            </body>
            </html>"""
        )

    epub_bytes = buf.getvalue()
    result = parse_epub(epub_bytes)

    assert result["metadata"]["title"] == "The Silent City"
    assert result["metadata"]["author"] == "Kirk LaSalle"
    assert len(result["scenes"]) == 1
    assert "Awakening" in result["scenes"][0]["heading"] or "Chapter" in result["scenes"][0]["heading"]

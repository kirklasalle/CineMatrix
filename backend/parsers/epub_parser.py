"""
ePub Digital Publication Parser (Phase 6).
Extracts book metadata, chapters, narrative text, and dialogue from .epub files.
"""
import io
import re
import zipfile
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def parse_epub(file_bytes: bytes) -> Dict[str, Any]:
    """
    Parses an .epub archive and extracts chapters as scene units.
    """
    metadata = {
        "title": "Digital Publication",
        "author": "",
        "language": "en",
        "chapter_count": 0,
    }
    scenes = []

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
            namelist = zf.namelist()

            # 1. Locate root opf file from META-INF/container.xml
            opf_path = ""
            if "META-INF/container.xml" in namelist:
                try:
                    container_xml = zf.read("META-INF/container.xml")
                    c_root = ET.fromstring(container_xml)
                    for elem in c_root.iter():
                        if elem.tag.endswith("rootfile") and "full-path" in elem.attrib:
                            opf_path = elem.attrib["full-path"]
                            break
                except Exception as e:
                    logger.warning(f"Could not parse container.xml: {e}")

            if not opf_path:
                opf_candidates = [n for n in namelist if n.endswith(".opf")]
                if opf_candidates:
                    opf_path = opf_candidates[0]

            # 2. Extract metadata from OPF
            if opf_path and opf_path in namelist:
                try:
                    opf_xml = zf.read(opf_path)
                    opf_root = ET.fromstring(opf_xml)
                    for elem in opf_root.iter():
                        if elem.tag.endswith("title") and elem.text:
                            metadata["title"] = elem.text.strip()
                        elif elem.tag.endswith("creator") and elem.text:
                            metadata["author"] = elem.text.strip()
                except Exception as e:
                    logger.warning(f"Could not parse OPF: {e}")

            # 3. Extract text content from (x)html files
            html_files = [
                n for n in namelist
                if (n.endswith(".xhtml") or n.endswith(".html") or n.endswith(".htm"))
                and not n.lower().endswith("toc.xhtml")
                and not n.lower().endswith("cover.xhtml")
            ]
            html_files.sort()

            for idx, h_file in enumerate(html_files):
                raw_html = zf.read(h_file).decode("utf-8", errors="ignore")
                
                # Strip HTML tags
                clean_text = re.sub(r'<style.*?</style>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<script.*?</script>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                if len(clean_text) < 30:
                    continue  # Skip empty or navigational pages

                chapter_num = len(scenes) + 1
                heading = f"CHAPTER {chapter_num}"
                
                # Check for chapter title in the first 80 characters
                first_line = clean_text[:80]
                if "Chapter" in first_line or "CHAPTER" in first_line or "PROLOGUE" in first_line.upper():
                    heading = first_line.split(".")[0].strip()

                scenes.append({
                    "scene_number": chapter_num,
                    "heading": heading,
                    "content": clean_text,
                    "characters": [],
                })

            metadata["chapter_count"] = len(scenes)

    except Exception as e:
        logger.error(f"Failed to parse ePub archive: {e}")
        raise ValueError(f"Invalid ePub publication: {e}")

    return {
        "metadata": metadata,
        "scenes": scenes,
        "chapter_count": len(scenes),
    }

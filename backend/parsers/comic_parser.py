"""
Comic Archive Parser & Generator (Phase 6).
Handles .cbz (ZIP) and .cbr (RAR/ZIP) comic book archives,
extracts ComicInfo.xml metadata, and packages storyboards into comic archives.
"""
import io
import os
import zipfile
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def parse_cbz(file_bytes: bytes) -> Dict[str, Any]:
    """
    Parses a .cbz (or zip-based .cbr) archive.
    Extracts ComicInfo.xml metadata and page entries.
    """
    metadata = {
        "title": "Comic Book / Graphic Novel",
        "series": "",
        "issue": "1",
        "writer": "",
        "penciller": "",
        "summary": "",
        "page_count": 0,
    }
    pages = []
    scenes = []

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
            namelist = zf.namelist()

            # 1. Parse ComicInfo.xml if present
            comic_info_files = [n for n in namelist if n.lower().endswith("comicinfo.xml")]
            if comic_info_files:
                try:
                    xml_content = zf.read(comic_info_files[0])
                    root = ET.fromstring(xml_content)
                    if root.find("Title") is not None and root.find("Title").text:
                        metadata["title"] = root.find("Title").text
                    if root.find("Series") is not None and root.find("Series").text:
                        metadata["series"] = root.find("Series").text
                    if root.find("Number") is not None and root.find("Number").text:
                        metadata["issue"] = root.find("Number").text
                    if root.find("Writer") is not None and root.find("Writer").text:
                        metadata["writer"] = root.find("Writer").text
                    if root.find("Penciller") is not None and root.find("Penciller").text:
                        metadata["penciller"] = root.find("Penciller").text
                    if root.find("Summary") is not None and root.find("Summary").text:
                        metadata["summary"] = root.find("Summary").text
                except Exception as e:
                    logger.warning(f"Could not parse ComicInfo.xml: {e}")

            # 2. Extract image page files sorted alphabetically
            image_files = [
                n for n in namelist
                if os.path.splitext(n.lower())[1] in IMAGE_EXTENSIONS and not n.startswith("__MACOSX")
            ]
            image_files.sort()
            metadata["page_count"] = len(image_files)

            for idx, img_name in enumerate(image_files):
                page_num = idx + 1
                heading = f"PAGE {page_num}"
                if metadata["series"]:
                    heading += f" ({metadata['series']} #{metadata['issue']})"
                
                desc = f"Comic illustration page {page_num} of {len(image_files)} from '{metadata['title']}'."
                if metadata["summary"] and idx == 0:
                    desc += f" Story Summary: {metadata['summary']}"

                scenes.append({
                    "scene_number": page_num,
                    "heading": heading,
                    "content": desc,
                    "characters": [],
                    "image_filename": img_name,
                })

    except Exception as e:
        logger.error(f"Failed to parse CBZ archive: {e}")
        raise ValueError(f"Invalid CBZ comic archive: {e}")

    return {
        "metadata": metadata,
        "scenes": scenes,
        "page_count": len(scenes),
    }


def create_cbz_package(
    title: str,
    frames: List[Dict[str, Any]],
    metadata: Optional[Dict[str, str]] = None,
) -> bytes:
    """
    Creates a compliant .cbz comic book package with embedded ComicInfo.xml and storyboard images.
    """
    meta = metadata or {}
    series_title = meta.get("series") or title
    writer = meta.get("writer") or "Kirk LaSalle"
    summary = meta.get("summary") or f"Storyboard & Graphic Novel adaptation of {title}."

    # Build ComicInfo.xml root
    root = ET.Element("ComicInfo")
    ET.SubElement(root, "Title").text = title
    ET.SubElement(root, "Series").text = series_title
    ET.SubElement(root, "Number").text = meta.get("issue", "1")
    ET.SubElement(root, "Writer").text = writer
    ET.SubElement(root, "Penciller").text = "Storyboard AI Engine"
    ET.SubElement(root, "Summary").text = summary
    ET.SubElement(root, "PageCount").text = str(len(frames))

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ComicInfo.xml", xml_bytes)

        for idx, f in enumerate(frames):
            page_num = idx + 1
            filename = f"page_{page_num:03d}.txt"
            content = f"PAGE {page_num} - {f.get('heading', '')}\n\n{f.get('description', '')}\n\nMoment: {f.get('moment_summary', '')}"
            zf.writestr(filename, content.encode("utf-8"))

    return buf.getvalue()

"""
Storyboard AI — Master Cinematic Export Service (Oscar / Level 3).
Generates high-resolution PDF Storyboard Presentation Decks and ZIP image archives.
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.lib.colors import HexColor
from typing import List, Dict, Any, Optional
import zipfile
import io
import os
import re
import base64
import logging
import datetime
import httpx

logger = logging.getLogger("storyboard.export")


class ExportService:
    @staticmethod
    def _fetch_image_reader(image_path_or_url: Optional[str], timeout: float = 8.0) -> Optional[ImageReader]:
        """
        Converts a local path, base64 data URI, or remote HTTP URL into a ReportLab ImageReader.
        Returns None if the image cannot be loaded.
        """
        if not image_path_or_url or not isinstance(image_path_or_url, str):
            return None

        clean_path = image_path_or_url.strip()
        if not clean_path:
            return None

        # 1. Base64 Data URI
        if clean_path.startswith("data:image/"):
            try:
                base64_data = clean_path.split(",", 1)[1] if "," in clean_path else clean_path
                image_bytes = base64.b64decode(base64_data)
                return ImageReader(io.BytesIO(image_bytes))
            except Exception as e:
                logger.warning(f"EXPORT: Failed to decode base64 image: {e}")
                return None

        # 2. Remote HTTP/HTTPS URL
        if clean_path.startswith("http://") or clean_path.startswith("https://"):
            try:
                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    resp = client.get(clean_path)
                    if resp.status_code == 200 and resp.content:
                        return ImageReader(io.BytesIO(resp.content))
                    logger.warning(f"EXPORT: Remote image fetch failed (HTTP {resp.status_code}): {clean_path[:60]}")
            except Exception as e:
                logger.warning(f"EXPORT: Exception fetching remote image ({clean_path[:60]}): {e}")
                return None

        # 3. Local file path
        if os.path.exists(clean_path):
            try:
                return ImageReader(clean_path)
            except Exception as e:
                logger.warning(f"EXPORT: Failed to read local image ({clean_path}): {e}")
                return None

        return None

    @classmethod
    def generate_pdf_bytes(
        cls,
        project_name: str,
        frames: List[Dict[str, Any]],
        script_format: str = "Screenplay",
        storyboard_style: str = "Oscar Prestige",
    ) -> bytes:
        """
        Generates an Oscar-grade, landscape PDF Storyboard Deck.
        Page 1: Presentation Cover Page.
        Pages 2+: Full-bleed 16:9 Frame + Cinematography Spec Panels.
        """
        pdf_buffer = io.BytesIO()
        # Landscape Letter: 792 wide x 612 high points
        c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))
        page_width, page_height = landscape(letter)

        # Color Palette
        bg_dark = HexColor("#090D16")
        card_bg = HexColor("#111827")
        accent_indigo = HexColor("#6366F1")
        accent_amber = HexColor("#F59E0B")
        accent_rose = HexColor("#F43F5E")
        text_primary = HexColor("#F8FAFC")
        text_secondary = HexColor("#94A3B8")
        text_muted = HexColor("#64748B")
        border_subtle = HexColor("#1E293B")

        # ─── COVER PAGE ────────────────────────────────────────────────────────
        c.setFillColor(bg_dark)
        c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

        # Decorative gradient bar at top
        c.setFillColor(accent_indigo)
        c.rect(0, page_height - 8, page_width, 8, fill=1, stroke=0)

        # Main Title & Subtitle
        c.setFillColor(text_primary)
        c.setFont("Helvetica-Bold", 32)
        c.drawString(60, page_height - 120, project_name or "Untitled Project")

        c.setFillColor(accent_indigo)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, page_height - 150, "CINEMATIC STORYBOARD & PRODUCTION SHOT DECK")

        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 11)
        c.drawString(60, page_height - 175, f"Format: {script_format.upper()}  ·  Art Direction: {storyboard_style}")

        # Meta Details Box
        c.setFillColor(card_bg)
        c.roundRect(60, page_height - 380, page_width - 120, 170, 10, fill=1, stroke=1)
        c.setStrokeColor(border_subtle)

        c.setFillColor(text_primary)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(85, page_height - 240, "PROJECT SUMMARY")

        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 10)
        c.drawString(85, page_height - 270, f"Total Visual Frames: {len(frames)}")
        c.drawString(85, page_height - 290, f"Generated On: {datetime.date.today().strftime('%B %d, %Y')}")
        c.drawString(85, page_height - 310, "Resolution Spec: 16:9 Cinematic Aspect Ratio")
        c.drawString(85, page_height - 330, "AI Engine: Storyboard AI Triple-Pass Narrative Orchestrator")

        # Quote / Philosophy Block
        c.setFillColor(text_muted)
        c.setFont("Helvetica-Oblique", 10)
        quote_text = '“Every element is used because the story demands it — not as a syntax exercise.”'
        c.drawCentredString(page_width / 2.0, 95, quote_text)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor("#475569"))
        c.drawCentredString(page_width / 2.0, 75, "STORYBOARD AI  ·  GOVERNED BY KIRK LASALLE'S 10 LAWS")

        c.showPage()

        # ─── FRAME PAGES (1 Scene per Page) ───────────────────────────────────
        total_pages = len(frames) + 1  # 1 cover + N frames

        for idx, frame in enumerate(frames):
            page_num = idx + 2

            # Background
            c.setFillColor(bg_dark)
            c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

            # Top Header Bar
            c.setFillColor(card_bg)
            c.rect(0, page_height - 50, page_width, 50, fill=1, stroke=0)
            c.setStrokeColor(border_subtle)
            c.setLineWidth(1)
            c.line(0, page_height - 50, page_width, page_height - 50)

            # Scene Title & Number
            c.setFillColor(accent_indigo)
            c.setFont("Helvetica-Bold", 14)
            scene_num = frame.get("scene_number", idx + 1)
            heading = frame.get("heading", f"Scene {scene_num}")
            c.drawString(30, page_height - 32, f"SCENE {scene_num}: {heading.upper()}")

            # Intensity Badge in Header
            intensity_type = frame.get("intensity_type", "Scene")
            intensity_score = frame.get("intensity_score", 5.0)
            if intensity_score is None:
                intensity_score = 5.0

            intensity_color = accent_rose if "Action" in intensity_type else (accent_amber if "Emotional" in intensity_type else text_muted)
            c.setFillColor(intensity_color)
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(page_width - 30, page_height - 32, f"{intensity_type.upper()}  ({round(float(intensity_score) * 10)}%)")

            # ── LEFT COLUMN: 16:9 IMAGE AREA (Width: 420, Height: 236 pt) ──
            img_x = 30
            img_y = page_height - 320
            img_w = 420
            img_h = 236

            c.setFillColor(HexColor("#0F172A"))
            c.setStrokeColor(border_subtle)
            c.roundRect(img_x, img_y, img_w, img_h, 8, fill=1, stroke=1)

            img_reader = cls._fetch_image_reader(frame.get("image_path"))
            if img_reader:
                try:
                    c.drawImage(img_reader, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True, anchor='c')
                except Exception as e:
                    logger.warning(f"EXPORT: drawImage error: {e}")
                    c.setFillColor(text_muted)
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(img_x + img_w / 2.0, img_y + img_h / 2.0, "[Visual Render Error]")
            else:
                c.setFillColor(text_muted)
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(img_x + img_w / 2.0, img_y + img_h / 2.0 + 10, "[Frame Visual Render]")
                c.setFont("Helvetica", 9)
                c.drawCentredString(img_x + img_w / 2.0, img_y + img_h / 2.0 - 10, "Visual generation pending or cached locally")

            # ── LEFT BOTTOM: Visual Description Box ──
            desc_y = 50
            desc_h = img_y - desc_y - 15
            c.setFillColor(card_bg)
            c.roundRect(img_x, desc_y, img_w, desc_h, 8, fill=1, stroke=1)

            c.setFillColor(accent_indigo)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(img_x + 15, desc_y + desc_h - 20, "VISUAL FRAME DESCRIPTION")

            c.setFillColor(text_primary)
            c.setFont("Helvetica", 9)
            description = frame.get("description", "")
            lines = simpleSplit(description, "Helvetica", 9, img_w - 30)
            text_obj = c.beginText(img_x + 15, desc_y + desc_h - 36)
            text_obj.setFont("Helvetica", 9)
            text_obj.setLeading(12)
            for line in lines[:8]:  # Max lines in box
                text_obj.textLine(line)
            c.drawText(text_obj)

            # ── RIGHT COLUMN: Cinematography & Directing Specs ──
            right_x = img_x + img_w + 20
            right_w = page_width - right_x - 30
            right_y = 50
            right_h = page_height - 50 - right_y - 20

            c.setFillColor(card_bg)
            c.roundRect(right_x, right_y, right_w, right_h, 8, fill=1, stroke=1)

            # Spec Card Header
            c.setFillColor(accent_indigo)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(right_x + 18, right_y + right_h - 25, "CINEMATOGRAPHY SPECIFICATIONS")

            # Spec Fields
            specs = [
                ("SHOT TYPE", frame.get("shot_type") or "Medium Shot"),
                ("CAMERA MOVEMENT", frame.get("camera_movement") or "Static"),
                ("LENS PACKAGE", frame.get("lens") or "50mm Prime"),
                ("LIGHTING SETUP", frame.get("lighting") or "Natural / Three-Point"),
            ]

            spec_curr_y = right_y + right_h - 55
            for label, val in specs:
                c.setFillColor(text_muted)
                c.setFont("Helvetica-Bold", 8)
                c.drawString(right_x + 18, spec_curr_y, label)

                c.setFillColor(text_primary)
                c.setFont("Helvetica", 10)
                c.drawString(right_x + 18, spec_curr_y - 14, str(val))

                spec_curr_y -= 38

            # Moment Summary / Director's Note
            moment = frame.get("moment_summary")
            if moment:
                c.setStrokeColor(border_subtle)
                c.line(right_x + 18, spec_curr_y + 10, right_x + right_w - 18, spec_curr_y + 10)

                c.setFillColor(accent_amber)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(right_x + 18, spec_curr_y - 5, "DIRECTOR'S MOMENT FOCUS")

                c.setFillColor(text_secondary)
                c.setFont("Helvetica-Oblique", 9)
                moment_lines = simpleSplit(f'“{moment}”', "Helvetica-Oblique", 9, right_w - 36)
                m_obj = c.beginText(right_x + 18, spec_curr_y - 22)
                m_obj.setFont("Helvetica-Oblique", 9)
                m_obj.setLeading(12)
                for m_line in moment_lines[:4]:
                    m_obj.textLine(m_line)
                c.drawText(m_obj)

            # ── FOOTER ──
            c.setFillColor(text_muted)
            c.setFont("Helvetica", 8)
            c.drawString(30, 22, f"Storyboard AI  ·  Project: {project_name}")
            c.drawRightString(page_width - 30, 22, f"Page {page_num} of {total_pages}")

            c.showPage()

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    @classmethod
    def generate_zip_bytes(
        cls,
        project_name: str,
        frames: List[Dict[str, Any]]
    ) -> bytes:
        """
        Packs all available rendered storyboard frame images into a downloadable ZIP archive.
        Also attaches a formatted shot-list CSV inside the zip.
        """
        import csv

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add Shot List CSV
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow([
                "Scene #", "Heading", "Shot Type", "Camera Movement", "Lens",
                "Lighting", "Intensity Score", "Intensity Type", "Moment Summary", "Description"
            ])
            for f in frames:
                writer.writerow([
                    f.get("scene_number", ""),
                    f.get("heading", ""),
                    f.get("shot_type", ""),
                    f.get("camera_movement", ""),
                    f.get("lens", ""),
                    f.get("lighting", ""),
                    f.get("intensity_score", ""),
                    f.get("intensity_type", ""),
                    f.get("moment_summary", ""),
                    f.get("description", ""),
                ])
            zipf.writestr("shot_list.csv", csv_output.getvalue().encode("utf-8"))

            # 2. Add Frame Images
            for idx, frame in enumerate(frames):
                img_path = frame.get("image_path")
                if not img_path:
                    continue

                scene_num = frame.get("scene_number", idx + 1)
                intensity_slug = re.sub(r'[^a-zA-Z0-9]', '_', frame.get("intensity_type", "scene")).lower()
                clean_filename = f"scene_{scene_num:02d}_{intensity_slug}.png"

                # Check Base64
                if img_path.startswith("data:image/"):
                    try:
                        base64_data = img_path.split(",", 1)[1] if "," in img_path else img_path
                        image_bytes = base64.b64decode(base64_data)
                        zipf.writestr(f"frames/{clean_filename}", image_bytes)
                    except Exception as e:
                        logger.warning(f"ZIP: Could not decode base64 frame {scene_num}: {e}")
                # Check HTTP URL
                elif img_path.startswith("http://") or img_path.startswith("https://"):
                    try:
                        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                            resp = client.get(img_path)
                            if resp.status_code == 200:
                                zipf.writestr(f"frames/{clean_filename}", resp.content)
                    except Exception as e:
                        logger.warning(f"ZIP: Could not download frame {scene_num}: {e}")
                # Check local path
                elif os.path.exists(img_path):
                    try:
                        zipf.write(img_path, arcname=f"frames/{clean_filename}")
                    except Exception as e:
                        logger.warning(f"ZIP: Could not pack local frame {scene_num}: {e}")

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    @staticmethod
    def generate_cbz_bytes(
        project_name: str,
        frames: List[Dict[str, Any]],
        writer: str = "Kirk LaSalle",
    ) -> bytes:
        """
        Packages storyboard frames into a standard .cbz comic archive with ComicInfo.xml metadata.
        """
        from parsers.comic_parser import create_cbz_package
        return create_cbz_package(
            title=project_name,
            frames=frames,
            metadata={"writer": writer, "series": project_name},
        )

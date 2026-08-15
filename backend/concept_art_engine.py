"""
Storyboard AI — Character Concept Art & Model Sheet Studio (Phase 8).
Generates multi-angle turnarounds, 6-expression matrices, and casting look-book PDFs.
"""
import io
import re
import os
import logging
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

logger = logging.getLogger(__name__)


class ConceptArtEngine:
    """Character model sheets, turnarounds, and executive look-book generator."""

    @staticmethod
    def build_portrait_prompt(character: Dict[str, Any], style_prefix: str = "") -> str:
        """Constructs high-impact cinematic full-body hero portrait prompt."""
        name = character.get("name", "Character")
        desc = character.get("description", "A dramatic character")
        wardrobe = character.get("wardrobe", "Signature cinematic attire")
        role = character.get("role", "Protagonist")

        prompt = (
            f"Cinematic full-body character portrait of {name}, {role}. "
            f"{desc}. Wearing {wardrobe}. "
            "Studio lighting, volumetric atmosphere, 8k resolution, master character concept art, high detail face and wardrobe texture."
        )
        if style_prefix:
            prompt = f"{style_prefix} {prompt}"
        return prompt

    @staticmethod
    def build_expression_matrix_prompt(character: Dict[str, Any]) -> str:
        """Constructs 6-expression model sheet matrix prompt."""
        name = character.get("name", "Character")
        desc = character.get("description", "")
        return (
            f"Character expression model sheet for {name}. {desc}. "
            "Grid of 6 distinct facial expressions: 1. Neutral, 2. Fierce Anger, 3. Genuine Joy, 4. Cold Calculation, 5. Deep Sorrow, 6. Intense Resolve. "
            "Consistent face features across all expressions, clean white/grey studio background, character design sheet."
        )

    @staticmethod
    def build_turnaround_prompt(character: Dict[str, Any]) -> str:
        """Constructs 4-angle turnaround model sheet prompt."""
        name = character.get("name", "Character")
        desc = character.get("description", "")
        wardrobe = character.get("wardrobe", "")
        return (
            f"Character turnaround model sheet of {name}. {desc}. Signature outfit: {wardrobe}. "
            "4 distinct full-body views in a single row: Front view, Three-quarter view, Side profile view, Back view. "
            "Neutral A-pose, accurate character height guide lines, production concept art model sheet."
        )

    @staticmethod
    def generate_lookbook_pdf(
        project_name: str,
        characters: List[Dict[str, Any]],
        writer: str = "Kirk LaSalle",
    ) -> bytes:
        """
        Generates an executive Casting & Character Look-Book PDF deck.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        w, h = landscape(letter)

        # ── Cover Page ──
        c.setFillColor(HexColor("#0F172A"))  # Dark Slate
        c.rect(0, 0, w, h, stroke=0, fill=1)

        # Accent Top Bar
        c.setFillColor(HexColor("#6366F1"))
        c.rect(0, h - 12, w, 12, stroke=0, fill=1)

        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 32)
        c.drawString(60, h - 120, project_name.upper())

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor("#818CF8"))
        c.drawString(60, h - 150, "EXECUTIVE CHARACTER LOOK-BOOK & CASTING DECK")

        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#94A3B8"))
        c.drawString(60, h - 180, f"Created for {writer}  |  Total Cast: {len(characters)} Characters")
        c.drawString(60, 40, "GOVERNED BY THE PRISM SACRED COVENANT & 10 LAWS  ·  STORYBOARD AI")

        c.showPage()

        # ── Character Profile Pages ──
        for char in characters:
            c.setFillColor(HexColor("#0B0F17"))
            c.rect(0, 0, w, h, stroke=0, fill=1)

            c.setFillColor(HexColor("#6366F1"))
            c.rect(0, h - 8, w, 8, stroke=0, fill=1)

            # Name & Role Header
            c.setFillColor(HexColor("#FFFFFF"))
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, h - 60, char.get("name", "CHARACTER").upper())

            c.setFont("Helvetica-Bold", 10)
            role_text = f"ROLE: {char.get('role', 'Cast').upper()}  |  VOICE CASTING: {char.get('voice_id', 'alloy').upper()}"
            if char.get("is_lead"):
                role_text += "  [LEAD PROTAGONIST]"
            c.setFillColor(HexColor("#A855F7"))
            c.drawString(50, h - 80, role_text)

            # Left Column: Description & Wardrobe
            c.setFillColor(HexColor("#1E293B"))
            c.roundRect(50, 70, 360, h - 170, 10, stroke=0, fill=1)

            c.setFillColor(HexColor("#818CF8"))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(70, h - 125, "PHYSICAL PROFILE & VISUAL TRAITS")

            c.setFillColor(HexColor("#E2E8F0"))
            c.setFont("Helvetica", 9)
            desc_text = char.get("description") or "Visual physical profile established in screenplay."
            lines = simpleSplit(desc_text, "Helvetica", 9, 320)
            y_pos = h - 145
            for line in lines[:10]:
                c.drawString(70, y_pos, line)
                y_pos -= 14

            # Wardrobe Section
            c.setFillColor(HexColor("#818CF8"))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(70, y_pos - 15, "SIGNATURE WARDROBE")

            c.setFillColor(HexColor("#CBD5E1"))
            c.setFont("Helvetica", 9)
            wardrobe_text = char.get("wardrobe") or "Standard production attire."
            w_lines = simpleSplit(wardrobe_text, "Helvetica", 9, 320)
            y_pos = y_pos - 35
            for line in w_lines[:6]:
                c.drawString(70, y_pos, line)
                y_pos -= 14

            # Right Column: Visual Prompt Box
            c.setFillColor(HexColor("#1E293B"))
            c.roundRect(430, 70, w - 480, h - 170, 10, stroke=0, fill=1)

            c.setFillColor(HexColor("#10B981"))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(450, h - 125, "IMAGE CONSISTENCY PROMPT")

            c.setFillColor(HexColor("#A7F3D0"))
            c.setFont("Courier", 8)
            vp = char.get("visual_prompt") or f"{char.get('name')}, {desc_text}"
            p_lines = simpleSplit(vp, "Courier", 8, w - 520)
            y_pos = h - 150
            for line in p_lines[:16]:
                c.drawString(450, y_pos, line)
                y_pos -= 12

            # Footer
            c.setFont("Helvetica", 8)
            c.setFillColor(HexColor("#64748B"))
            c.drawString(50, 40, f"Character Look-Book  ·  {project_name}  ·  Storyboard AI Engine")

            c.showPage()

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

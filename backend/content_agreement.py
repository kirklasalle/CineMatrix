"""
Storyboard AI — User Content Agreement.

IMMUTABLE AGREEMENT: Governs all content submitted to Storyboard AI.
Authored in full compliance with Kirk LaSalle's 10 Laws (Permanent Active
Directives), particularly Laws 6, 7, and 8 (data privacy, transparency,
equity). This agreement is embedded in the application and cannot be
modified without a governance review.

Core Principle:
  Storyboard AI processes your submitted writing like a skilled human
  reader and cinematographer — it learns patterns, craft, and storytelling
  wisdom from the material, but retains ONLY distilled insights in its
  knowledge base. Raw content is analyzed and then discarded. The user
  retains all copyright to their original work. No raw text is ever
  stored in the Knowledge Base.

Author: Kirk LaSalle (Governance)
Co-Author: Claude (Anthropic)
Status: ACTIVE AND BINDING — Immutable
"""
import hashlib
from time_utils import utc_now  # type: ignore
import logging

logger = logging.getLogger("governance")

# ══════════════════════════════════════════════════════════════════════════════
# THE CONTENT AGREEMENT — Full Text
# Embedded as an immutable constant. DO NOT MODIFY.
# ══════════════════════════════════════════════════════════════════════════════

CONTENT_AGREEMENT_TEXT = """
STORYBOARD AI — USER CONTENT AGREEMENT
Version 1.0 | Effective: July 3, 2026 | Status: IMMUTABLE

By submitting any written work, screenplay, script, manuscript, treatment,
outline, or any other form of written content to Storyboard AI ("the
Service"), the user ("Submitter") agrees to the following terms, which
are irrevocable and binding upon submission:

1. GRANT OF PROCESSING LICENSE
   The Submitter grants Storyboard AI a perpetual, irrevocable, royalty-free
   license to process the submitted content for the purpose of:
   (a) Generating storyboard analysis and visual representations;
   (b) Extracting distilled cinematic and storytelling insights for the
       purpose of improving the Service's AI knowledge base.

2. WHAT IS RETAINED — THE MEMORY MODEL
   Storyboard AI operates on a "human memory" model:
   (a) Only distilled insights, patterns, and craft wisdom are retained
       in the Cinematic Knowledge Base. These are general, transferable
       lessons — not verbatim content.
   (b) Raw submitted content is NOT stored permanently. It is held only
       for the duration of the active analysis session.
   (c) What the system learns is equivalent to what a human cinematographer
       or story analyst would remember after reading a script: technique,
       pattern, structure, and emotional truth — not the specific words.

3. COPYRIGHT RETENTION
   The Submitter retains full copyright to all submitted original work.
   Storyboard AI makes no claim to ownership of any submitted content.
   This agreement grants a processing license only, not ownership.

4. PRIVACY AND DATA PROTECTION (Law 6 Compliance)
   In full compliance with the Sixth Law of the Permanent Active Directives:
   (a) No personally identifiable information from submitted content is
       stored in the Knowledge Base.
   (b) Story character names, real names of individuals, and personal
       information encountered in submitted content are excluded from
       knowledge retention.
   (c) The Submitter's identity and submission history are handled in
       accordance with applicable data protection regulations.

5. PURPOSE OF KNOWLEDGE RETENTION
   The sole purpose of retaining distilled insights is:
   (a) To improve the quality of storyboard analysis for all users;
   (b) To build a growing library of cinematic craft wisdom that benefits
       the entire creative community;
   (c) To preserve and honor the integrity of cinema, storytelling,
       journalism, and production craft.
   This knowledge belongs to the evolution of the art form itself.

6. EQUITY AND NEUTRALITY (Law 8 Compliance)
   All submitted content is treated with equal dignity regardless of the
   Submitter's identity, origin, belief, or background. No bias shall
   be introduced into the knowledge base from the processing of content.

7. TRANSPARENCY (Law 7 Compliance and Law 9 Compliance)
   The Submitter has the right to request:
   (a) Confirmation that their submission has been processed and discarded;
   (b) A description of what categories of insight (if any) were added to
       the knowledge base as a result of their submission.
   No deception shall be practiced regarding what is retained.

8. IRREVOCABILITY
   Once submitted, the processing license granted herein is irrevocable.
   However, this does not affect the Submitter's right to request deletion
   of their personal data from our systems in accordance with applicable law.

9. GOVERNANCE COMPLIANCE
   This agreement operates under and in full compliance with:
   (a) Kirk LaSalle's Permanent Active Directives — The 10 Laws;
   (b) The PRISM Agentic Prime Directive;
   (c) The PRISM Sacred Covenant.
   In any conflict between this agreement and the 10 Laws, the 10 Laws
   shall govern absolutely.

10. ACCEPTANCE
    Submission of content constitutes acceptance of this agreement in full.
    No signature is required. The act of submission is the agreement.

"Like a human who learns from everything they read,
 remembering the lesson but not the page."
— Storyboard AI Content Philosophy
"""

# ── Integrity fingerprint ─────────────────────────────────────────────────────
CONTENT_AGREEMENT_SHA256 = hashlib.sha256(
    CONTENT_AGREEMENT_TEXT.encode("utf-8")
).hexdigest()

# ── Short summary for UI display ──────────────────────────────────────────────
CONTENT_AGREEMENT_SUMMARY = (
    "By uploading, you grant Storyboard AI an irrevocable license to analyze "
    "your work and learn from it — like a human reader who learns craft and "
    "pattern, not verbatim content. You retain full copyright. Only distilled "
    "cinematic insights are added to our Knowledge Base. Raw content is never "
    "stored permanently. Governed by Kirk LaSalle's 10 Laws."
)

CONTENT_AGREEMENT_BULLET_POINTS = [
    "You keep full copyright to your work",
    "Raw content is analyzed then discarded — never permanently stored",
    "Only distilled craft insights are retained in our Cinematic Knowledge Base",
    "No personally identifiable information is stored",
    "This license is irrevocable upon submission",
    "Governed by the 10 Laws — privacy, equity, and transparency are absolute",
]


def get_agreement() -> dict:
    """Return the full content agreement for API and UI consumption."""
    return {
        "version": "1.0",
        "effective_date": "2026-07-03",
        "status": "IMMUTABLE",
        "integrity_sha256": CONTENT_AGREEMENT_SHA256,
        "full_text": CONTENT_AGREEMENT_TEXT.strip(),
        "summary": CONTENT_AGREEMENT_SUMMARY,
        "bullet_points": CONTENT_AGREEMENT_BULLET_POINTS,
    }


def log_acceptance(project_id: str, filename: str) -> None:
    """
    Record that a user has accepted the content agreement by submitting a file.
    Logs to the governance audit stream (Law 9 — transparent ledger).
    """
    ts = utc_now().isoformat()
    logger.info(
        f"CONTENT_AGREEMENT_ACCEPTED | project={project_id[:8]}... | "
        f"file={filename} | ts={ts} | sha256={CONTENT_AGREEMENT_SHA256[:16]}..."
    )

"""
Cryptographic utilities for Storyboard AI.

Provides symmetric encryption for API keys stored in the database.
Keys are encrypted at rest using Fernet (AES-128-CBC + HMAC-SHA256).
The encryption key is derived from the STORYBOARD_SECRET_KEY environment
variable using PBKDF2-HMAC-SHA256.

SECURITY NOTE: Set STORYBOARD_SECRET_KEY in your environment before first run.
A strong random value of 32+ characters is recommended.
If not set, a development default is used — NOT suitable for production.
"""
import os
import base64
import logging
from typing import Optional

logger = logging.getLogger("storyboard.crypto")

# ── Key derivation ────────────────────────────────────────────────────────────
_SALT = b"storyboard_ai_v1_salt"  # Fixed salt — change only with full re-encryption
_ITERATIONS = 100_000


def _get_fernet():
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

    secret = os.environ.get("STORYBOARD_SECRET_KEY", "")
    if not secret:
        logger.warning(
            "STORYBOARD_SECRET_KEY not set. Using insecure development default. "
            "Set this environment variable before deploying to production."
        )
        secret = "storyboard-ai-dev-key-insecure-change-before-deploy"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode("utf-8")))
    return Fernet(key)


# ── Encryption / Decryption ───────────────────────────────────────────────────
def encrypt_api_key(plaintext: Optional[str]) -> str:
    """
    Encrypt an API key for storage in the database.
    Returns empty string for None/empty input.
    Encrypted values are prefixed with 'enc:' to distinguish from
    legacy plaintext values during migration.
    """
    if not plaintext:
        return ""
    if plaintext.startswith("enc:"):
        # Already encrypted; keep as-is to prevent accidental double encryption.
        return plaintext
    try:
        cipher = _get_fernet()
        token = cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")
        return f"enc:{token}"
    except Exception as e:
        logger.error(f"CRYPTO: Failed to encrypt API key: {e}")
        return plaintext  # Fail open to avoid breaking existing configs


def decrypt_api_key(stored: Optional[str]) -> str:
    """
    Decrypt an API key retrieved from the database.
    Handles both encrypted ('enc:' prefix) and legacy plaintext values
    transparently — no migration step required.
    """
    if not stored:
        return ""
    if not stored.startswith("enc:"):
        # Legacy plaintext key — return as-is (backwards compatible)
        logger.debug("CRYPTO: Reading legacy plaintext API key (not yet encrypted)")
        return stored
    try:
        cipher = _get_fernet()
        token = stored[4:]  # strip 'enc:' prefix
        return cipher.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.error(f"CRYPTO: Failed to decrypt API key: {e}")
        return ""

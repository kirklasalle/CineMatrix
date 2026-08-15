"""
Test suite: Encryption utilities — encrypt/decrypt round-trip, legacy passthrough.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_encrypt_returns_enc_prefix():
    from crypto_utils import encrypt_api_key
    result = encrypt_api_key("sk-test-key-12345")
    assert result.startswith("enc:"), f"Expected 'enc:' prefix, got: {result[:10]}"


def test_decrypt_roundtrip():
    from crypto_utils import encrypt_api_key, decrypt_api_key
    original = "sk-abcdef1234567890"
    encrypted = encrypt_api_key(original)
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == original


def test_empty_string_encrypt():
    from crypto_utils import encrypt_api_key
    assert encrypt_api_key("") == ""
    assert encrypt_api_key(None) == ""


def test_empty_string_decrypt():
    from crypto_utils import decrypt_api_key
    assert decrypt_api_key("") == ""
    assert decrypt_api_key(None) == ""


def test_legacy_plaintext_passthrough():
    """Keys without 'enc:' prefix (legacy) pass through unchanged."""
    from crypto_utils import decrypt_api_key
    legacy_key = "sk-legacy-plaintext-key"
    result = decrypt_api_key(legacy_key)
    assert result == legacy_key


def test_enc_prefix_triggers_decryption():
    """A string with 'enc:' prefix that is not valid Fernet returns empty string."""
    from crypto_utils import decrypt_api_key
    result = decrypt_api_key("enc:notavalidfernettoken")
    assert result == ""


def test_different_keys_produce_different_ciphertext():
    from crypto_utils import encrypt_api_key
    enc1 = encrypt_api_key("key_one")
    enc2 = encrypt_api_key("key_two")
    assert enc1 != enc2


def test_encrypt_same_key_produces_different_ciphertext():
    """Fernet uses random IV — same plaintext produces different ciphertext each time."""
    from crypto_utils import encrypt_api_key
    enc1 = encrypt_api_key("same_key")
    enc2 = encrypt_api_key("same_key")
    assert enc1 != enc2  # Random IV means different each time


def test_long_api_key():
    from crypto_utils import encrypt_api_key, decrypt_api_key
    long_key = "sk-" + ("abcdef1234567890" * 20)
    encrypted = encrypt_api_key(long_key)
    assert decrypt_api_key(encrypted) == long_key


def test_special_characters():
    from crypto_utils import encrypt_api_key, decrypt_api_key
    key_with_special = "api_key!@#$%^&*()_+-={}|[]"
    encrypted = encrypt_api_key(key_with_special)
    assert decrypt_api_key(encrypted) == key_with_special


def test_encrypt_is_idempotent_for_encrypted_values():
    from crypto_utils import encrypt_api_key
    encrypted = encrypt_api_key("sk-stable-key")
    assert encrypt_api_key(encrypted) == encrypted

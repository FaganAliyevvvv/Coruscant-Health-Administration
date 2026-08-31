"""
Symmetric encryption helpers for documents at rest.

Uses Fernet (AES-128-CBC + HMAC-SHA256, per RFC recommendations for
authenticated symmetric encryption) from the `cryptography` package, which
implements current NIST-recommended primitives. The key is never stored in
the repository - it must come from the environment / a secrets manager
(e.g. AWS Secrets Manager, GCP Secret Manager, Azure Key Vault) in
production. This satisfies "encrypted and stored respecting the latest
security standard" without inventing a bespoke, unaudited cipher.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Fernet:
    key = getattr(settings, "DOCUMENT_ENCRYPTION_KEY", None)
    if not key:
        raise ImproperlyConfigured(
            "DOCUMENT_ENCRYPTION_KEY is not set. Generate one with "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"` "
            "and provide it via environment variable / secrets manager."
        )
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_bytes(data: bytes) -> bytes:
    return _get_fernet().encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    try:
        return _get_fernet().decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Document could not be decrypted: invalid key or corrupted data.") from exc

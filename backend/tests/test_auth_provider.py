"""Provider-aware authentication tests."""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from jose import jwt
from jose.backends.cryptography_backend import CryptographyRSAKey

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"lexi_auth_provider_tests_{os.getpid()}.sqlite"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")

from backend import security  # noqa: E402
from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.models import User  # noqa: E402


@pytest.fixture(autouse=True)
def database_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    security._clear_supabase_jwks_cache()

    yield

    Base.metadata.drop_all(bind=engine)
    security._clear_supabase_jwks_cache()


def _supabase_test_token(email: str, subject=None, audience: str = "authenticated"):
    subject = subject or uuid4()
    issuer = "https://lexi-test.supabase.co/auth/v1"
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_jwk = CryptographyRSAKey(key.public_key(), "RS256").to_dict()
    public_jwk.update({"kid": "lexi-test-key", "use": "sig"})

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(subject),
            "email": email,
            "aud": audience,
            "role": "authenticated",
            "iss": issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": "lexi-test-key"},
    )

    return token, {"keys": [public_jwk]}, subject


def _configure_supabase(monkeypatch, jwks):
    monkeypatch.setattr(security.settings, "auth_provider", "supabase")
    monkeypatch.setattr(security.settings, "supabase_url", "https://lexi-test.supabase.co")
    monkeypatch.setattr(security.settings, "supabase_jwt_audience", "authenticated")
    monkeypatch.setattr(security, "_load_supabase_jwks", lambda: jwks)


def test_custom_auth_gate_blocks_private_token_issuance_in_supabase_mode(monkeypatch):
    monkeypatch.setattr(security.settings, "auth_provider", "supabase")

    with pytest.raises(HTTPException) as exc_info:
        security.require_custom_auth_enabled()

    assert exc_info.value.status_code == 403
    assert "AUTH_PROVIDER=supabase" in exc_info.value.detail


def test_supabase_token_maps_subject_to_lexi_user(monkeypatch):
    email = f"supabase-{uuid4().hex}@example.com"
    token, jwks, subject = _supabase_test_token(email)
    _configure_supabase(monkeypatch, jwks)

    db = SessionLocal()
    try:
        user = security._get_supabase_current_user(token, db)
        stored_user = db.query(User).filter(User.id == subject).first()

        assert user.id == subject
        assert user.email == email
        assert stored_user is not None
        assert stored_user.hashed_password == security.SUPABASE_MANAGED_PASSWORD_SENTINEL
    finally:
        db.close()


def test_supabase_identity_conflict_returns_explicit_error(monkeypatch):
    email = f"conflict-{uuid4().hex}@example.com"
    token, jwks, _ = _supabase_test_token(email)
    _configure_supabase(monkeypatch, jwks)

    db = SessionLocal()
    try:
        db.add(User(id=uuid4(), email=email, hashed_password="custom-user"))
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            security._get_supabase_current_user(token, db)

        assert exc_info.value.status_code == 409
    finally:
        db.close()


def test_supabase_token_rejects_unexpected_audience(monkeypatch):
    email = f"wrong-audience-{uuid4().hex}@example.com"
    token, jwks, _ = _supabase_test_token(email, audience="unexpected")
    _configure_supabase(monkeypatch, jwks)

    with pytest.raises(HTTPException) as exc_info:
        security._decode_supabase_token(token)

    assert exc_info.value.status_code == 401

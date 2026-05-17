"""Authentication and JWT utilities."""

from datetime import datetime, timedelta, timezone
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_db
from backend.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SUPPORTED_AUTH_PROVIDERS = {"custom", "supabase"}
SUPABASE_ALLOWED_ALGORITHMS = ("RS256", "RS384", "RS512", "ES256", "ES384", "ES512")
SUPABASE_MANAGED_PASSWORD_SENTINEL = "supabase-auth-managed"

_supabase_jwks_cache: dict[str, Any] = {"url": "", "expires_at": 0.0, "payload": None}


def hash_password(password: str) -> str:
    """Hash plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def auth_provider_name() -> str:
    """Return the normalized configured auth provider."""
    return settings.auth_provider.strip().lower()


def require_custom_auth_enabled() -> None:
    """Reject custom register/login endpoints when another provider is active."""
    provider = auth_provider_name()
    if provider == "custom":
        return

    if provider == "supabase":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Custom auth endpoints are disabled when AUTH_PROVIDER=supabase.",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Unsupported AUTH_PROVIDER configured: {settings.auth_provider}",
    )


async def require_custom_auth_enabled_dependency() -> None:
    """Async FastAPI dependency wrapper for the custom-auth gate."""
    require_custom_auth_enabled()


def _credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _auth_config_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=message,
    )


def _supabase_jwks_url() -> str:
    configured_jwks_url = settings.supabase_jwks_url.strip()
    if configured_jwks_url:
        return configured_jwks_url

    supabase_url = settings.supabase_url.strip().rstrip("/")
    if not supabase_url:
        raise _auth_config_error(
            "Supabase auth is not configured. Set SUPABASE_URL or SUPABASE_JWKS_URL."
        )

    return f"{supabase_url}/auth/v1/.well-known/jwks.json"


def _supabase_issuer() -> str | None:
    supabase_url = settings.supabase_url.strip().rstrip("/")
    if supabase_url:
        return f"{supabase_url}/auth/v1"

    jwks_url = settings.supabase_jwks_url.strip().rstrip("/")
    jwks_suffix = "/.well-known/jwks.json"
    if jwks_url.endswith(jwks_suffix):
        return jwks_url[: -len(jwks_suffix)]

    return None


def _clear_supabase_jwks_cache() -> None:
    _supabase_jwks_cache.update({"url": "", "expires_at": 0.0, "payload": None})


def _load_supabase_jwks() -> dict[str, Any]:
    """Fetch and cache Supabase signing keys."""
    jwks_url = _supabase_jwks_url()
    now = time.monotonic()
    cached_payload = _supabase_jwks_cache.get("payload")

    if (
        cached_payload
        and _supabase_jwks_cache.get("url") == jwks_url
        and float(_supabase_jwks_cache.get("expires_at", 0.0)) > now
    ):
        return cached_payload

    request = Request(jwks_url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise _auth_config_error("Could not load Supabase signing keys.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
        raise _auth_config_error("Supabase JWKS response did not include signing keys.")

    if not payload["keys"]:
        raise _auth_config_error(
            "Supabase JWKS response is empty. Use asymmetric Supabase JWT signing keys "
            "before enabling AUTH_PROVIDER=supabase."
        )

    _supabase_jwks_cache.update(
        {
            "url": jwks_url,
            "expires_at": now + settings.supabase_jwks_cache_seconds,
            "payload": payload,
        }
    )
    return payload


def _decode_custom_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise _credentials_error()
        return UUID(subject)
    except (JWTError, ValueError):
        raise _credentials_error() from None


def _decode_supabase_token(token: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise _credentials_error() from None

    algorithm = str(header.get("alg", ""))
    if algorithm not in SUPABASE_ALLOWED_ALGORITHMS:
        raise _credentials_error()

    kid = header.get("kid")
    jwks = _load_supabase_jwks()
    matching_keys = [
        key for key in jwks["keys"] if kid is None or str(key.get("kid", "")) == str(kid)
    ]

    if not matching_keys and kid:
        _clear_supabase_jwks_cache()
        jwks = _load_supabase_jwks()
        matching_keys = [key for key in jwks["keys"] if str(key.get("kid", "")) == str(kid)]

    if not matching_keys:
        raise _credentials_error()

    audience = settings.supabase_jwt_audience.strip() or None
    issuer = _supabase_issuer()

    try:
        return jwt.decode(
            token,
            {"keys": matching_keys},
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options={"require_exp": True, "require_sub": True},
        )
    except JWTError:
        raise _credentials_error() from None


def _email_from_supabase_claims(payload: dict[str, Any]) -> str:
    email = payload.get("email")
    if not email and isinstance(payload.get("user_metadata"), dict):
        email = payload["user_metadata"].get("email")

    if not isinstance(email, str) or not email.strip():
        raise _credentials_error()

    return email.strip().lower()


def _get_custom_current_user(token: str, db: Session) -> User:
    user_id = _decode_custom_token(token)
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        raise _credentials_error()

    return user


def _get_supabase_current_user(token: str, db: Session) -> User:
    payload = _decode_supabase_token(token)

    try:
        subject_id = UUID(str(payload.get("sub")))
    except (TypeError, ValueError):
        raise _credentials_error() from None

    email = _email_from_supabase_claims(payload)

    user = db.query(User).filter(User.id == subject_id).first()
    if user:
        if not user.is_active:
            raise _credentials_error()

        if user.email != email:
            user.email = email
            db.commit()
            db.refresh(user)

        return user

    existing_email_user = db.query(User).filter(User.email == email).first()
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A Lexi account already exists for this email under a different auth identity.",
        )

    user = User(
        id=subject_id,
        email=email,
        hashed_password=SUPABASE_MANAGED_PASSWORD_SENTINEL,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from the configured auth provider."""
    provider = auth_provider_name()

    if provider == "custom":
        return _get_custom_current_user(token, db)

    if provider == "supabase":
        return _get_supabase_current_user(token, db)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Unsupported AUTH_PROVIDER configured: {settings.auth_provider}",
    )

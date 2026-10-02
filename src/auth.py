"""JWT helpers for API auth."""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import logging

from src.config import settings

logger = logging.getLogger(__name__)


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encode and sign a JWT payload."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


async def verify_token(token: str) -> dict:
    """Validate a JWT and return its payload."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise Exception("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise Exception("Invalid token")


def create_access_token(user_id: str, username: str) -> str:
    """Create a token for a user using the app's JWT settings."""
    payload = {
        "sub": user_id,
        "username": username,
        "iat": datetime.now(timezone.utc)
    }
    return create_token(payload)

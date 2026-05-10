import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException
import jwt

from database import get_user_by_id

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class CurrentUserData(TypedDict):
    id: int
    username: str
    created_at: str


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hash_value = stored_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate, hash_value)


def create_access_token(user_id: int, username: str) -> tuple[str, int]:
    expires_in = JWT_EXPIRE_MINUTES * 60
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expires_at,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_in


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUserData:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        resolved_user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_id(resolved_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    return {"id": user["id"], "username": user["username"], "created_at": user["created_at"]}


CurrentUser = Annotated[CurrentUserData, Depends(get_current_user)]

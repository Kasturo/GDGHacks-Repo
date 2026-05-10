import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import sqlite3
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv

SRC_ROOT = Path(__file__).resolve().parent.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.append(str(SRC_ROOT))

from auth import CurrentUser, create_access_token, get_current_user, hash_password, verify_password
from database import init_db, create_user, get_user_by_email

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

raw_origins = os.getenv("ORIGIN", "")
env_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
allow_origins = env_origins or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "online"}


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignupResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: str
    access_token: str
    token_type: str
    expires_in: int


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: str


protected_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])


@app.post("/api/signup", response_model=SignupResponse, status_code=201)
def signup(payload: SignupRequest):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=422, detail="Email cannot be blank")

    password_hash = hash_password(payload.password)
    try:
        user = create_user(email, password_hash)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")

    return {
        "id": user["id"],
        "email": user["username"],
        "created_at": user["created_at"],
    }


@app.post("/api/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=422, detail="Email cannot be blank")

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token, expires_in = create_access_token(user["id"], user["username"])

    return {
        "id": user["id"],
        "email": user["username"],
        "created_at": user["created_at"],
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@app.get("/api/me", response_model=MeResponse)
def get_me(current_user: CurrentUser):
    return current_user


@protected_router.get("/auth-check")
def auth_check():
    return {"authenticated": True}


app.include_router(protected_router)

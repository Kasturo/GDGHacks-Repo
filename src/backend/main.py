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
from database import (
    create_pet,
    create_or_get_match,
    create_user,
    get_pet_by_id,
    get_pet_owned_by_user,
    get_user_by_email,
    has_like_swipe,
    init_db,
    list_matches_for_pet,
    list_swipe_candidates,
    record_swipe,
)

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


class PetCardResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    species: str
    breed: str | None = None
    age_years: float | None = None
    gender: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    created_at: str


class SwipeRequest(BaseModel):
    swiper_pet_id: int
    swiped_pet_id: int
    direction: str = Field(pattern="^(like|pass)$")


class SwipeResponse(BaseModel):
    swipe_id: int
    direction: str
    is_match: bool
    match_id: int | None = None


class CreatePetRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species: str = Field(min_length=1, max_length=50)
    breed: str | None = Field(default=None, max_length=80)
    age_years: float | None = Field(default=None, ge=0)
    gender: str | None = Field(default=None, max_length=20)
    bio: str | None = Field(default=None, max_length=1000)
    photo_url: str | None = Field(default=None, max_length=500)


class MatchItemResponse(BaseModel):
    match_id: int
    matched_at: str
    other_pet_id: int
    other_owner_id: int
    other_name: str
    other_species: str
    other_breed: str | None = None
    other_age_years: float | None = None
    other_gender: str | None = None
    other_bio: str | None = None
    other_photo_url: str | None = None


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
    return {
        "id": current_user["id"],
        "email": current_user["username"],
        "created_at": current_user["created_at"],
    }


@protected_router.get("/auth-check")
def auth_check():
    return {"authenticated": True}


@protected_router.post("/pets", response_model=PetCardResponse, status_code=201)
def add_pet(payload: CreatePetRequest, current_user: CurrentUser):
    name = payload.name.strip()
    species = payload.species.strip()
    if not name or not species:
        raise HTTPException(status_code=422, detail="Name and species cannot be blank")

    pet = create_pet(
        owner_id=current_user["id"],
        name=name,
        species=species,
        breed=payload.breed.strip() if payload.breed else None,
        age_years=payload.age_years,
        gender=payload.gender.strip() if payload.gender else None,
        bio=payload.bio.strip() if payload.bio else None,
        photo_url=payload.photo_url.strip() if payload.photo_url else None,
    )
    return {
        "id": pet["id"],
        "owner_id": pet["owner_id"],
        "name": pet["name"],
        "species": pet["species"],
        "breed": pet["breed"],
        "age_years": pet["age_years"],
        "gender": pet["gender"],
        "bio": pet["bio"],
        "photo_url": pet["photo_url"],
        "created_at": pet["created_at"],
    }


@protected_router.get("/matches", response_model=list[MatchItemResponse])
def get_matches(pet_id: int, current_user: CurrentUser):
    owned_pet = get_pet_owned_by_user(pet_id, current_user["id"])
    if not owned_pet:
        raise HTTPException(status_code=404, detail="Pet not found for current user")

    matches = list_matches_for_pet(pet_id)
    return [
        {
            "match_id": match["match_id"],
            "matched_at": match["matched_at"],
            "other_pet_id": match["other_pet_id"],
            "other_owner_id": match["other_owner_id"],
            "other_name": match["other_name"],
            "other_species": match["other_species"],
            "other_breed": match["other_breed"],
            "other_age_years": match["other_age_years"],
            "other_gender": match["other_gender"],
            "other_bio": match["other_bio"],
            "other_photo_url": match["other_photo_url"],
        }
        for match in matches
    ]


@protected_router.get("/swipes/candidates", response_model=list[PetCardResponse])
def get_swipe_candidates(swiper_pet_id: int, current_user: CurrentUser):
    owned_pet = get_pet_owned_by_user(swiper_pet_id, current_user["id"])
    if not owned_pet:
        raise HTTPException(status_code=404, detail="Pet not found for current user")

    candidates = list_swipe_candidates(swiper_pet_id, current_user["id"])
    return [
        {
            "id": pet["id"],
            "owner_id": pet["owner_id"],
            "name": pet["name"],
            "species": pet["species"],
            "breed": pet["breed"],
            "age_years": pet["age_years"],
            "gender": pet["gender"],
            "bio": pet["bio"],
            "photo_url": pet["photo_url"],
            "created_at": pet["created_at"],
        }
        for pet in candidates
    ]


@protected_router.post("/swipes", response_model=SwipeResponse, status_code=201)
def create_swipe(payload: SwipeRequest, current_user: CurrentUser):
    if payload.swiper_pet_id == payload.swiped_pet_id:
        raise HTTPException(status_code=400, detail="Cannot swipe on the same pet")

    swiper_pet = get_pet_owned_by_user(payload.swiper_pet_id, current_user["id"])
    if not swiper_pet:
        raise HTTPException(status_code=404, detail="Swiper pet not found for current user")

    swiped_pet = get_pet_by_id(payload.swiped_pet_id)
    if not swiped_pet:
        raise HTTPException(status_code=404, detail="Swiped pet not found")
    if swiped_pet["owner_id"] == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot swipe on your own pet")

    swipe = record_swipe(payload.swiper_pet_id, payload.swiped_pet_id, payload.direction)

    is_match = False
    match_id = None
    if payload.direction == "like" and has_like_swipe(payload.swiped_pet_id, payload.swiper_pet_id):
        match = create_or_get_match(payload.swiper_pet_id, payload.swiped_pet_id)
        is_match = True
        match_id = match["id"]

    return {
        "swipe_id": swipe["id"],
        "direction": swipe["direction"],
        "is_match": is_match,
        "match_id": match_id,
    }


app.include_router(protected_router)

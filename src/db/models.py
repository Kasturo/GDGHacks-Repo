from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class PetCreate(BaseModel):
    owner_id: int
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[float] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None


class PetPublic(BaseModel):
    id: int
    owner_id: int
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[float] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SwipeCreate(BaseModel):
    swiper_pet_id: int
    swiped_pet_id: int
    direction: str  # 'like' | 'pass'


class SwipePublic(SwipeCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MatchPublic(BaseModel):
    id: int
    pet_a_id: int
    pet_b_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationPublic(BaseModel):
    id: int
    match_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParticipantPublic(BaseModel):
    conversation_id: int
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    body: str


class MessagePublic(MessageCreate):
    id: int
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

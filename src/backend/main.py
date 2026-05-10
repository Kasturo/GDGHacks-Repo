import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
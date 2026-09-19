import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from .database import Base, engine
from .routers.application import router as applications_router
from .routers.user import router as users_router
from .routers.interview import router as interviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "1":
        Base.metadata.create_all(bind=engine)

    yield

app = FastAPI(
    title="JobTrack API",
    description="Job Application and Interview Tracking API",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(applications_router)
app.include_router(users_router)
app.include_router(interviews_router)


@app.get("/", tags=["System"])
def root():
    return {"message": "Welcome to JobTrack API"}
# python -m uvicorn app.main:app --reload
# .\venv\Scripts\Activate.ps1
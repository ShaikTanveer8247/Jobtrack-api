import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/", tags=["System"])
def root():
    return {"message": "Welcome to JobTrack API"}


@app.get("/health", tags=["System"], status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


API_V1_PREFIX = "/api/v1"

app.include_router(
    applications_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    users_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    interviews_router,
    prefix=API_V1_PREFIX,
)
# python -m uvicorn app.main:app --reload
# .\venv\Scripts\Activate.ps1
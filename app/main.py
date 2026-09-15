from fastapi import FastAPI

app = FastAPI(
    title="JobTrack API",
    description="Job Application and Interview Tracking API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to JobTrack API"}
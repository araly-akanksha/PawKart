# app.py

from fastapi import FastAPI

app = FastAPI(
    title="PawKart API",
    version="1.0"
)

@app.get("/")
def home():
    return {"message": "PawKart Backend Running"}
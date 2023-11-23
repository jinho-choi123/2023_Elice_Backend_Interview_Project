from fastapi import FastAPI
import os 
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".config", ".env"))

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello world"
    }
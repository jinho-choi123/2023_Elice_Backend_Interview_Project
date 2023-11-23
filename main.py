from fastapi import FastAPI, Depends
# load secrets from dotenv
import config
from src.routers.index import indexRouter

app = FastAPI()

@app.get("/hc")
async def root():
    return {
        "message": "Server is Running!"
    }

## /api Routers
app.include_router(indexRouter)
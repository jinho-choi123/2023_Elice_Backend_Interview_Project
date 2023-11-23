from fastapi import APIRouter

from src.db.database import SessionLocal
from src.db.models import User

authRouter = APIRouter(
    prefix="/auth",
)

@authRouter.post("/signup")
def auth_Signup():
    return {
        "message": "this is signup endpoint"
    }

@authRouter.post("/signin")
def auth_Signin():
    return {
        "message": "this is signin endpoint"
    }

@authRouter.post("/signout")
def auth_Signout():
    return {
        "message": "this is signout endpoint"
    }


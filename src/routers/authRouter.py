from fastapi import APIRouter
from src.types.authTypes import authRequest, authResponse
from src.controller.authController import check_user_exists, user_signup

from src.db.database import SessionLocal
from src.db.models import User

authRouter = APIRouter(
    prefix="/auth",
)

@authRouter.post("/signup")
def auth_Signup(signupForm: authRequest) -> authResponse:
    db = SessionLocal()
    # check if user email is already occupied 
    if(not check_user_exists(db, signupForm.email)):
        # duplicate email! 
        return authResponse(success = False, message = "Signup Failed. Email is already in use.")
    
    # create user object in db 
    user_signup(db, signupForm)
    return authResponse(success = True, message = "signup success")

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


from fastapi import APIRouter, Response
from src.types.authTypes import authSignupRequest, authSigninRequest, authResponse
from src.controller.authController import check_user_exists, user_signin, user_signup

from src.db.database import SessionLocal
from src.db.models import User

authRouter = APIRouter(
    prefix="/auth",
)

@authRouter.post("/signup")
def auth_Signup(signupForm: authSignupRequest) -> authResponse:
    db = SessionLocal()
    # check if user email is already occupied 
    if(not check_user_exists(db, signupForm.email)):
        # duplicate email! 
        return authResponse(success = False, message = "Signup Failed. Email is already in use.")
    
    # create user object in db 
    user_signup(db, signupForm)
    return authResponse(success = True, message = "signup success")

@authRouter.post("/signin")
def auth_Signin(signinForm: authSigninRequest, response: Response) -> authResponse:
    db = SessionLocal()
    if(check_user_exists(db, signinForm.email)):
        return authResponse(success = False, message = "User with given email does not exists.")

    # check password 
    cookie = user_signin(db, signinForm)
    if cookie:
        ## login success 
        ## set cookie 
        response.set_cookie(key='session.id', value=cookie)
        return authResponse(success = True, message = "signin success")
    else:
        return authResponse(success = False, message = "invalid password!")

@authRouter.post("/signout")
def auth_Signout():
    return {
        "message": "this is signout endpoint"
    }


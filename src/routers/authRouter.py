from fastapi import APIRouter, Response, Cookie, Depends
from requests import session
from src.middlewares.authMiddleware import get_current_user
from src.types.authTypes import authSignupRequest, authSigninRequest, authResponse
from src.types.userTypes import userSession
from src.controller.authController import check_user_exists, user_signin, user_signout, user_signup

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
        response.set_cookie(key='session_id', value=cookie)
        return authResponse(success = True, message = "signin success")
    else:
        return authResponse(success = False, message = "invalid password!")

@authRouter.post("/signout")
def auth_Signout(response: Response, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    user_signout(session_id)

    ## then remove cookie 
    response.delete_cookie(key='session_id')
    return authResponse(success = True, message = "logout success")


import os
from sqlalchemy.orm import Session 
from sqlalchemy import select
from src.db import database, models
from src.types.authTypes import authSigninRequest, authSignupRequest
from src.types.userTypes import userCreation
from src.utils.hash import check_password_match, generate_rand_salt, hash_password
from sqlalchemy.exc import SQLAlchemyError
from src.db.database import redis_client
from src.utils.session import generate_cookie
from src.types.userTypes import userSession

# return True if user does not exists
# return False o/w
def check_user_exists(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = db.scalar(stmt)
    if(result):
        return False
    else:
        return True

def get_user_id(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = db.scalar(stmt)
    if(not result):
        return None 
    else:
        return result.id
    
# create user object 
def user_signup(db: Session, signupForm: authSignupRequest):
    try:
        # generate user specific salt 
        hash_salt = generate_rand_salt(256)

        # generate password hash 
        passwordHash = hash_password(signupForm.password, hash_salt)

        user_creation = userCreation(
            fullName = signupForm.fullName,
            email = signupForm.email,
            password_salt = hash_salt,
            password_hash = passwordHash,
            boards = []
        )
        # generate user object 
        newUser = models.User(
            **user_creation.model_dump()
        )
        db.add(newUser)
        db.commit()
        return True
    except SQLAlchemyError as e:
        print(str(e.orig))
        return False

def user_signin(db: Session, signinForm: authSigninRequest):
    # check if user is valid 
    # assume that user record with given email exists
    SESSION_EXP_TIME = int(os.environ["SESSION_EXP_TIME"])

    ## get password hash from db
    stmt = select(models.User).where(models.User.id == 1)
    result = db.scalar(stmt)

    ## must not happen 
    if(not result):
        raise Exception("Invalid email or password.")
    
    stored_passwordHash = result.password_hash
    password_salt = result.password_salt

    if(check_password_match(signinForm.password, stored_passwordHash, password_salt)):
        ## login success!
        ## create cookie and add it to redis 
        user_id = get_user_id(db, signinForm.email)
        cookie = generate_cookie()
        redis_client.set(cookie, user_id, ex=SESSION_EXP_TIME)
        return cookie 
    else:
        ## login Failed!!
        return None
    
# signout user
# expire redis session
def user_signout(cookie: str):
    redis_client.delete(cookie)
    return

def get_user_session(db: Session, user_id: int):
    stmt = select(models.User).where(models.User.id == user_id)
    result = db.execute(stmt).fetchone()
    if not result:
        return None 
    else:
        # get user's owning boards and posts ids
        board_ids = list()
        post_ids = list()
        for board in result[0].boards:
            board_ids.append(int(board.id))

        for post in result[0].posts:
            post_ids.append(int(post.id))

        return userSession(
            fullName = result[0].fullName,
            email =  result[0].email,
            board_ids = board_ids,
            post_ids = post_ids,
            id = user_id
        )

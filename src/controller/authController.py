from sqlalchemy.orm import Session 
from sqlalchemy import select
from src.db import database, models
from src.types.authTypes import authRequest, authResponse
from src.types.userTypes import userCreation
from src.utils.hash import generate_rand_salt, hash_password
from sqlalchemy.exc import SQLAlchemyError

# return True if user does not exists
# return False o/w
def check_user_exists(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = db.scalar(stmt)
    if(result):
        return False
    else:
        return True
    
# create user object 
def user_signup(db: Session, signupForm: authRequest):
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
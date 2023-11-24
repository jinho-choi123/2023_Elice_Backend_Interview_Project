from fastapi import HTTPException, Request, status
from src.controller.authController import get_user_session
from src.types.userTypes import userSession
from src.db.database import SessionLocal, redis_client

def get_current_user(cookie):
    # handle if cookie is None
    if(not cookie):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Cookie does not exists",
        )
    
    # get user id from cookie value 
    user_id = int(redis_client.get(cookie))

    if not user_id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid cookie value",
        )
    
    db = SessionLocal()
    user_session = get_user_session(db, user_id)

    if not user_session:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid cookie value",
        )
    return user_session

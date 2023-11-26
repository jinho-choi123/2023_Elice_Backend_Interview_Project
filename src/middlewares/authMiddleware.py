from fastapi import Cookie, Depends, HTTPException, Request, status
from src.controller.authController import get_user_session
from src.db.database import get_db
from src.db.database import SessionLocal, redis_client

async def get_current_user(session_id: str | None = Cookie(default=None), db = Depends(get_db)):
    # handle if cookie is None
    if not session_id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Cookie does not exists",
        )
    # get user id from cookie value 
    user_id = redis_client.get(session_id)
    user_id = int(user_id)

    if not user_id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid cookie value",
        )
    
    
    user_session = get_user_session(db, user_id)

    if not user_session:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid cookie value",
        )
    return user_session
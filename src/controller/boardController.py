from sqlalchemy.orm import Session

from src.types.userTypes import userSession 
from sqlalchemy import select
from src.db import models, database

## check if current user is board's owner
def is_board_owner(db: Session, board_id: int, userSession: userSession):
    # just check if userSession's board include board_id 
    if board_id in userSession.boards:
        # current user is board's owner 
        return True 
    else:
        return False
    

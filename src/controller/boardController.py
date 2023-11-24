from fastapi import HTTPException, status
import psycopg2
from sqlalchemy.orm import Session

from sqlalchemy.exc import SQLAlchemyError
from src.types.userTypes import userSession 
from sqlalchemy import select
from src.db import models, database
from src.types.boardTypes import boardBaseRequest, boardDeletion, boardGet, boardGetResponse, boardUpdate

## check if current user is board's owner
def is_board_owner(board_id: int, userSession: userSession):
    # just check if userSession's board include board_id 
    if board_id in userSession.boards:
        # current user is board's owner 
        return True 
    else:
        return False
    
def check_board_name_exists(db: Session, board_name: str):
    stmt = select(models.Board).where(models.Board.name == board_name)
    result = db.scalar(stmt)
    if(result):
        return True 
    else:
        return False

# check board name exists except the given board id
def check_board_name_exists_except(db: Session, board_name: str, board_id: int):
    stmt = select(models.Board).where(models.Board.id != board_id).where(models.Board.name == board_name)
    result = db.scalar(stmt)
    
    if(result):
        return True 
    else:
        return False

def check_board_id_exists(db: Session, board_id: int):
    stmt = select(models.Board).where(models.Board.id == board_id)
    result = db.scalar(stmt)

    if(result):
        return True 
    else:
        return False

def is_board_viewable(db: Session, user_session: userSession, board_id: int):
    stmt = select(models.Board).where(models.Board.id == board_id)
    result = db.scalar(stmt)

    # if board does not exists
    if not result:
        return False, None 
    
    is_Viewable = result.isPublic

    ## if user is board owner, then board is viewable
    if is_board_owner(board_id, user_session):
        is_Viewable = True
    
    return is_Viewable, result
    
    
def board_create(db: Session, boardForm: boardBaseRequest, user_session: userSession):
    try:
        board_creation = boardForm

        newBoard = models.Board(
            **board_creation.model_dump(),
            creator_id = user_session.id
        )
        db.add(newBoard)
        db.commit()
        return True
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = str(e.orig)
        )
    
def board_update(db: Session, boardForm: boardUpdate):
    stmt = select(models.Board).where(models.Board.id == boardForm.id)
    updating_board = db.scalar(stmt)

    # will not reach due to is_board_owner function
    if not updating_board:
        # board with given name and id does not exist
        return False 
    
    updating_board.name = boardForm.name 
    updating_board.isPublic = boardForm.isPublic
    db.commit()
    return True


def board_delete(db: Session, boardForm: boardDeletion):
    stmt = select(models.Board).where(models.Board.id == boardForm.id)
    deleting_board = db.scalar(stmt)

    # will not reach due to is_board_owner function
    if not deleting_board:
        return False
    
    db.delete(deleting_board)
    db.commit()
    return True

def board_get(db: Session, user_session: userSession, boardForm: boardGet):
    isViewable, board = is_board_viewable(db, user_session, boardForm.id)

    if not isViewable:
        return None 
    
    boardInfo = boardGetResponse(id = board.id, name = board.name, isPublic = board.isPublic, posts = board.posts)

    return boardInfo

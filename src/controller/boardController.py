from itertools import count
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy.exc import SQLAlchemyError
from src.types.userTypes import userSession 
from sqlalchemy import asc, delete, desc, select, func, update
from src.db import models, database
from src.types.boardTypes import boardBaseRequest, boardDeletion, boardGet, boardObj, boardPagination, boardUpdate
import math

## check if current user is board's owner
def is_board_owner(board_id: int, userSession: userSession):
    owner_boards_ids = list(map(lambda board: board.id, userSession.boards))
    # just check if userSession's board include board_id 
    if board_id in owner_boards_ids:
        # current user is board's owner 
        return True 
    else:
        return False

def get_board_by_id(db: Session, board_id: int)->boardObj:
    stmt = select(models.Board).where(models.Board.id == board_id)
    result = db.execute(stmt).fetchone()
    if not result:
        return None 
    else:
        returnObj = boardObj(id = result[0].id, name = result[0].name, isPublic = result[0].isPublic, posts = result[0].posts, creator_id = result[0].creator_id)
        return returnObj

def get_board_by_name(db: Session, board_name: str)->boardObj:
    stmt = select(models.Board).where(models.Board.name == board_name)
    result = db.execute(stmt).fetchone()
    if not result:
        return None 
    else:
        returnObj = boardObj(id = result[0].id, name = result[0].name, isPublic = result[0].isPublic, posts = result[0].posts, creator_id = result[0].creator_id)
        return returnObj

# check board name exists except the given board id
def check_board_name_exists_except(db: Session, board_name: str, board_id: int):
    same_name_board = get_board_by_name(db, board_name)
    if not same_name_board:
        return False 
    if same_name_board.id == board_id:
        return False
    else:
        return True

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
    try:
        stmt = (
            update(models.Board)
                .where(models.Board.id == boardForm.id)
                .values(
                    {
                        models.Board.name: boardForm.name,
                        models.Board.isPublic: boardForm.isPublic
                    }
                )
        )
        db.execute(stmt)
        db.commit()
        return True
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = str(e.orig)
        )


def board_delete(db: Session, boardForm: boardDeletion):
    stmt = delete(models.Board).where(models.Board.id == boardForm.id)
    db.execute(stmt)
    db.commit()
    return True

def board_get(db: Session, user_session: userSession, boardForm: boardGet):
    board = get_board_by_id(db, boardForm.id)

    # check if current user is board's owner 
    if board.creator_id == user_session.id or board.isPublic == True:
        return board

    return None

def boards_pagination(db: Session, board_pagination: boardPagination, total_boards_size: int, user_session: userSession):
    pageNum = board_pagination.page
    pageSize = board_pagination.pageSize
    # if pageNum <= 0 then set pageNum to 1
    if pageNum <= 0:
        pageNum = 1

    lastPageNum = math.ceil(total_boards_size / pageSize)

    # if pageNum exceeds boards_size/pageSize, then return end page
    if pageNum > lastPageNum:
        pageNum = lastPageNum

    # calculate offset and limit
    offset = (pageNum - 1) * pageSize
    limit = pageSize

    # query boards 
    # order by desc order of # of posts in board
    stmt = select(models.Board, func.count(models.Post.id).label("count")) \
        .outerjoin(models.Post) \
        .where((models.Board.creator_id == user_session.id) | (models.Board.isPublic == True)) \
        .group_by(models.Board.id) \
        .order_by(desc("count")) \
        .offset(offset) \
        .limit(limit)
    
    boards_list = db.execute(stmt).fetchall()
    boards_result = list()

    for board in list(boards_list):
        boards_result.append(
            boardObj(
                id = board[0].id,
                name = board[0].name,
                isPublic = board[0].isPublic,
                posts = board[0].posts,
                creator_id = board[0].creator_id
            )
        )

    return boards_result

def total_boards_size(db: Session):
    boardSize = db.query(models.Board).count()
    return boardSize
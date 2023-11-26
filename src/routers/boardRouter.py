from fastapi import APIRouter, Cookie, Response, status, Depends
from sqlalchemy.orm import Session
from src.controller.boardController import board_create, board_delete, board_update, boards_pagination, check_board_name_exists_except, get_board_by_id, get_board_by_name, is_board_owner, total_boards_size
from src.db.database import get_db

from src.middlewares.authMiddleware import get_current_user
from src.types.boardTypes import boardBaseRequest, boardDeletion, boardListResponse, boardObjResponse, boardPagination, boardResponse, boardUpdate

boardRouter = APIRouter(
    prefix="/board",
)

@boardRouter.post("/")
def board_Create(boardForm: boardBaseRequest, response: Response, db: Session = Depends(get_db), user = Depends(get_current_user)):
    # check if board name is already occupied 
    if get_board_by_name(db, boardForm.name):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return boardObjResponse(
            success = False,
            message = "Board name already in use",
            board = None
        )

    # create board
    if board_create(db, boardForm, user):
        # get board object from db 
        newBoard = get_board_by_name(db, boardForm.name)
        return boardObjResponse(
            success = True,
            message = "Board Creation Success!",
            board = newBoard
        )

@boardRouter.patch("/{board_id}")
def board_Update(board_id: int, boardForm: boardBaseRequest, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ## check if current user is board owner 
    if not is_board_owner(board_id, user):
        return boardObjResponse(
            success = False,
            message = "LoggedIn user is not board owner.",
            board = None 
        )
    
    if check_board_name_exists_except(db, boardForm.name, board_id):
        return boardObjResponse(
            success = False,
            message = "Given board name is already occupied.",
            board = None
        )
    
    boardForm = boardUpdate(
        **boardForm.model_dump(),
        id = board_id
    )
    if board_update(db, boardForm):
        updatedBoard = get_board_by_id(db, board_id)
        return boardObjResponse(
            success = True,
            message = "Board update success!",
            board = updatedBoard
        )
    else:
        return boardObjResponse(
            success = False, 
            message = "Board update failed. Please try again.",
            board = None
        )

@boardRouter.delete("/{board_id}")
def board_Delete(board_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not get_board_by_id(db, board_id):
        return boardResponse(
            success = False,
            message = "Board does not exists."
        )

    ## check if current user is board owner 
    if not is_board_owner(board_id, user):
        return boardResponse(
            success = False,
            message = "User is not board owner."
        )
    
    boardForm = boardDeletion(
        id = board_id
    )
    
    board_delete(db, boardForm)

    return boardResponse(
        success = True,
        message = "Board deletion success!"
    )

# should be front of get /. 
# else, this endpoint wouldnt be reached
@boardRouter.get("/list")
def board_List(page: int = 0, pageSize: int = 10, db: Session = Depends(get_db), user = Depends(get_current_user)):
    board_pagination = boardPagination(page = page, pageSize = pageSize)
    total_boards = total_boards_size(db)
    showing_boards = boards_pagination(db, board_pagination, total_boards, user)
    return boardListResponse(
        success = True,
        message = "Board getting list success!",
        boards = showing_boards
    )

@boardRouter.get("/{board_id}")
def board_Get(board_id: int, response: Response, db: Session = Depends(get_db), user = Depends(get_current_user)):
    board = get_board_by_id(db, board_id)

    if not board:
        return boardObjResponse(
            success = False,
            message = "Board does not exists",
            board = None
        )

    if is_board_owner(board_id, user) or board.isPublic == True:
        return boardObjResponse(
            success = True,
            message = "Board get success",
            board = board
        )
    else:
        return boardObjResponse(
            success = False,
            message = "Board get failed. Board is not accessible.",
            board = None
        )




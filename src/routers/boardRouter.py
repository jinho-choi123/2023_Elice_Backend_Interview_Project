from fastapi import APIRouter, Cookie, Response, status
from src.controller.boardController import board_create, board_delete, board_update, boards_pagination, check_board_name_exists_except, get_board_by_id, get_board_by_name, is_board_owner, total_boards_size
from src.db.database import SessionLocal

from src.middlewares.authMiddleware import get_current_user
from src.types.boardTypes import boardBaseRequest, boardDeletion, boardListResponse, boardObjResponse, boardPagination, boardResponse, boardUpdate

boardRouter = APIRouter(
    prefix="/board",
)

@boardRouter.post("/")
def board_Create(boardForm: boardBaseRequest, response: Response, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

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
def board_Update(board_id: int, boardForm: boardBaseRequest, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

    ## check if current user is board owner 
    if not is_board_owner(board_id, user):
        return boardResponse(
            success = False,
            message = "LoggedIn user is not board owner."
        )
    
    if check_board_name_exists_except(db, boardForm.name, board_id):
        return boardResponse(
            success = False,
            message = "Given board name is already occupied."
        )
    
    boardForm = boardUpdate(
        **boardForm.model_dump(),
        id = board_id
    )
    if board_update(db, boardForm):
        return boardResponse(
            success = True,
            message = "Board update success!"
        )
    else:
        return boardResponse(
            success = False, 
            message = "Board update failed. Please try again."
        )

@boardRouter.delete("/{board_id}")
def board_Delete(board_id: int, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

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
def board_List(page: int = 0, pageSize: int = 10, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)

    board_pagination = boardPagination(page = page, pageSize = pageSize)
    db = SessionLocal()
    total_boards = total_boards_size(db)
    showing_boards = boards_pagination(db, board_pagination, total_boards, user)
    return boardListResponse(
        success = True,
        message = "Board getting list success!",
        boards = showing_boards
    )

@boardRouter.get("/{board_id}")
def board_Get(board_id: int, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()
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
            message = "Board get failed",
            board = None
        )



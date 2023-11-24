from fastapi import APIRouter, Cookie, Response, status
from src.db.database import SessionLocal
from src.controller.boardController import board_create, board_update, check_board_name_exists, check_board_name_exists_except, is_board_owner

from src.middlewares.authMiddleware import get_current_user
from src.types.boardTypes import boardBaseRequest, boardResponse, boardUpdate

boardRouter = APIRouter(
    prefix="/board",
)

@boardRouter.post("/")
def board_Create(boardForm: boardBaseRequest, response: Response, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

    # check if board name is already occupied 
    if check_board_name_exists(db, boardForm.name):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return boardResponse(
            success = False,
            message = "Board name already in use",
        )

    # create board
    if board_create(db, boardForm, user):
        return boardResponse(
            success = True,
            message = "Board Creation Success!"
        )

@boardRouter.patch("/{board_id}")
def board_Update(board_id: int, boardForm: boardBaseRequest, session_id: str | None = Cookie(default=None)):
    user = get_current_user(session_id)
    db = SessionLocal()

    ## check if current user is board owner 
    if is_board_owner(board_id, user):
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

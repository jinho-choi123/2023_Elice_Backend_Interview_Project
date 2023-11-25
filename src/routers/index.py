from fastapi import APIRouter
from .authRouter import authRouter
from .boardRouter import boardRouter
from .postRouter import postRouter
indexRouter = APIRouter(
    prefix="/api",
)

indexRouter.include_router(authRouter)
indexRouter.include_router(boardRouter)
indexRouter.include_router(postRouter)
from fastapi import APIRouter
from .authRouter import authRouter
from .boardRouter import boardRouter
indexRouter = APIRouter(
    prefix="/api",
)

indexRouter.include_router(authRouter)
indexRouter.include_router(boardRouter)
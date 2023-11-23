from fastapi import APIRouter
from .authRouter import authRouter

indexRouter = APIRouter(
    prefix="/api",
)

indexRouter.include_router(authRouter)
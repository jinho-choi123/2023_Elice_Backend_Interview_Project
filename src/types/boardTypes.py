from typing import List
from pydantic import BaseModel

from src.types.postTypes import postObj

class boardBaseRequest(BaseModel):
    isPublic: bool
    name: str 

class boardUpdate(boardBaseRequest):
    id: int

class boardDeletion(BaseModel):
    id: int

class boardGet(boardDeletion):
    pass

class boardResponse(BaseModel):
    success: bool
    message: str 

class boardObj(BaseModel):
    id: int
    name: str
    isPublic: bool 
    post_ids: List[int]
    creator_id: int

class boardObjResponse(boardResponse):
    board: boardObj | None

class boardListResponse(boardResponse):
    boards: List[boardObj] | None 

class boardPagination(BaseModel):
    # page number 
    page: int 
    # amount of boards in single page
    pageSize: int 
    
from typing import List
from pydantic import BaseModel

class postObj(BaseModel):
    id: int 
    title: str 
    content: str 
    creator_id: int 
    board_id: int
    isPublic: bool

class postObjResponse(BaseModel):
    success: bool 
    message: str 
    post: postObj | None

class postBaseRequest(BaseModel):
    id: int
    title: str 
    content: str 
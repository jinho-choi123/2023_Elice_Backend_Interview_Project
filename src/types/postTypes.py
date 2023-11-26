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


class postUpdateRequest(BaseModel):
    title: str 
    content: str 

class postBaseRequest(postUpdateRequest):
    id: int

    
class postResponse(BaseModel):
    success: bool
    message: str 

class postDeletion(BaseModel):
    id: int

class postPagination(BaseModel):
    # page number 
    page: int 
    # amount of posts in single page
    pageSize: int 
    boardId: int

class postListResponse(postResponse):
    posts: List[postObj] | None 
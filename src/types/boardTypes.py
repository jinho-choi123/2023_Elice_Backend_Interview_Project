from pydantic import BaseModel

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

class boardGetResponse(BaseModel):
    id: int
    name: str
    isPublic: bool 
    posts: list 
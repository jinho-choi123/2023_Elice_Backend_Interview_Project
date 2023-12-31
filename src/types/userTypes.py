from typing import List
from pydantic import BaseModel

class userCreation(BaseModel):
    fullName: str 
    email: str 
    password_salt: str 
    password_hash: str 
    boards: list

class userSession(BaseModel):
    id: int
    fullName: str 
    email: str 
    board_ids: List[int]
    post_ids: List[int]
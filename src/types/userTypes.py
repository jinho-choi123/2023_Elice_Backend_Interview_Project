from pydantic import BaseModel

class userCreation(BaseModel):
    fullName: str 
    email: str 
    password_salt: str 
    password_hash: str 
    boards: list

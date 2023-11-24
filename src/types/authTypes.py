from pydantic import BaseModel

## add pydantic's model 
class authRequest(BaseModel):
    fullName: str
    email: str 
    password: str 

## add response type
class authResponse(BaseModel):
    success: bool
    message: str 

from pydantic import BaseModel

## add pydantic's model 
class authSigninRequest(BaseModel):
    email: str 
    password: str 

class authSignupRequest(authSigninRequest):
    fullName: str


## add response type
class authResponse(BaseModel):
    success: bool
    message: str 

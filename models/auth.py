from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str

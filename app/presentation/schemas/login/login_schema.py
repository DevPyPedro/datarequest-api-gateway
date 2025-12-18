from pydantic import BaseModel, EmailStr, Field

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=6, max_length=50)
    useremail: EmailStr
    userpassword: str

class UserRegisterResponseSchema(BaseModel):
    status: str
    message: str = Field(..., example="User created successfully.")

class UserLoginSchema(BaseModel):
    useremail: EmailStr
    userpassword: str
    code_verification: int

class UserLoginResponseSchema(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str = Field(..., example="bearer")


from pydantic import BaseModel, EmailStr, Field

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=6, max_length=50)
    useremail: EmailStr
    userpassword: str

class UserRegisterResponseSchema(BaseModel):
    status: str
    message: str = Field(..., example="User created successfully.")


from dataclasses import dataclass

@dataclass
class RegisterUserDTO:
    username: str
    useremail: str
    userpassword: str

@dataclass
class LoginUserDTO:
    useremail: str
    userpassword: str
    code_verification: int
    
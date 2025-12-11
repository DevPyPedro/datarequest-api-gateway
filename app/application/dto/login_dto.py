from dataclasses import dataclass

@dataclass
class RegisterUserDTO:
    username: str
    useremail: str
    userpassword: str
    
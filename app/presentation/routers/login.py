from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.db import get_db
from sqlalchemy.orm import Session
import random

from app.application.dto.login_dto import RegisterUserDTO, LoginUserDTO
from app.application.user_use_case import UserRegisterUseCase
from app.presentation.depends.auth import get_current_token
from app.presentation.schemas.login.login_schema import (
    UserRegisterSchema,
    UserRegisterResponseSchema,
    UserLoginSchema,
    UserLoginResponseSchema

)
from app.presentation.depends.login_depends import *

router = APIRouter()

@router.post(
    "/register",
    response_model=UserRegisterResponseSchema,
    tags=["Authentication"],
    summary="Register a new user"
)
def register_user(
    data: UserRegisterSchema,
    db: Session = Depends(get_db),
    use_case: UserRegisterUseCase = Depends(get_user_register_use_case)
):
    try:
        dto = RegisterUserDTO(
            useremail=data.useremail,
            username=data.username,
            userpassword=data.userpassword
        )

        result = use_case.execute(dto)

        db.commit()
        return result

    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve)
            }
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred during user registration."
            }
        )
    
@router.post(
    "/login",
    response_model=UserLoginResponseSchema,
    tags=["Authentication"],
    summary="Login a user"
)
def login_user(
    data: UserLoginSchema,
    db: Session = Depends(get_db),
    use_case: UserLoginUseCase = Depends(get_user_login_use_case)
):
    try:
        dto = LoginUserDTO(
            useremail=data.useremail,
            userpassword=data.userpassword,
            code_verification=data.code_verification
        )

        result = use_case.execute(dto)

        return result

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve)
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred during user login."
            }
        )
    

@router.get(
    "/generate-code",
    tags=["Authentication"],
    summary="Generate a verification code for a user"
)
def generate_verification_code(
    useremail: str,
    db_code: RedisCache = Depends(get_redis_cache_code),
    email_service = Depends(get_email_service)
):
    try:
        if not db_code.get(useremail) is None:
            raise ValueError("A verification code has already been sent to this email.")
        
        EXPIRATION_TIME = 300  # 5 minutes in seconds

        code = str(random.randint(100000, 999999))
        db_code.set(useremail, code)
        db_code.expire(useremail, EXPIRATION_TIME) # Code valid for 5 minutes

        email_service.send_email(
            to_email=useremail,
            subject="Your Verification Code",
            body=f"Your verification code is: {code}",
            html=False
        )

        return {
            "status": "success",
            "message": f"Verification code generated and stored for {useremail}."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred while generating the verification code"
            }
        )
    
@router.get("/me")
def get_me(token: str = Depends(get_current_token)):
    return {
        "message": "Você está autenticado 🎉",
        "token": token
    }

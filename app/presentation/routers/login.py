from fastapi import APIRouter, Depends, HTTPException

from app.application.user_use_case import UserRegisterUseCase
from app.application.dto.login_dto import RegisterUserDTO
from app.presentation.schemas.login_schema import (
    UserRegisterSchema,
    UserRegisterResponseSchema
)
from app.presentation.depends.login_depends import get_user_register_use_case

router = APIRouter()

@router.post(
    "/register",
    response_model=UserRegisterResponseSchema,
    tags=["Authentication"],
    summary="Register a new user"
)
def register_user(
    data: UserRegisterSchema,
    use_case: UserRegisterUseCase = Depends(get_user_register_use_case)
):
    try:
        dto = RegisterUserDTO(
            useremail=data.useremail,
            username=data.username,
            userpassword=data.userpassword
        )
        print('ok')
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"An error occurred during user registration. : {3}"
            }
        )
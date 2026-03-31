import random

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.application.dto.login_dto import LoginUserDTO, RefreshTokenDTO, RegisterUserDTO
from app.application.user_use_case import (
    UserLoginUseCase,
    UserLogoutUseCase,
    UserRefreshTokenUseCase,
    UserRegisterUseCase,
)
from app.infrastructure.db import get_db
from app.infrastructure.redis_service import RedisCache
from app.presentation.depends.auth import get_current_session, get_current_token
from app.presentation.depends.login_depends import (
    get_email_service,
    get_redis_cache_code,
    get_user_login_use_case,
    get_user_logout_use_case,
    get_user_refresh_token_use_case,
    get_user_register_use_case,
)
from app.presentation.schemas.login.login_schema import (
    LogoutResponseSchema,
    RefreshTokenSchema,
    UserLoginResponseSchema,
    UserLoginSchema,
    UserRegisterResponseSchema,
    UserRegisterSchema,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponseSchema,
    tags=["Authentication"],
    summary="Register a new user",
)
def register_user(
    data: UserRegisterSchema,
    db: Session = Depends(get_db),
    use_case: UserRegisterUseCase = Depends(get_user_register_use_case),
):
    try:
        dto = RegisterUserDTO(
            useremail=data.useremail,
            username=data.username,
            userpassword=data.userpassword,
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
                "message": str(ve),
            },
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred during user registration.",
            },
        )


def _issue_token(
    data: UserLoginSchema,
    use_case: UserLoginUseCase,
):
    dto = LoginUserDTO(
        useremail=data.useremail,
        userpassword=data.userpassword,
        code_verification=data.code_verification,
    )

    return use_case.execute(dto)


def _refresh_token(
    data: RefreshTokenSchema,
    use_case: UserRefreshTokenUseCase,
):
    dto = RefreshTokenDTO(refresh_token=data.refresh_token)
    return use_case.execute(dto)


@router.post(
    "/login",
    response_model=UserLoginResponseSchema,
    tags=["Authentication"],
    summary="Login a user",
)
def login_user(
    data: UserLoginSchema,
    use_case: UserLoginUseCase = Depends(get_user_login_use_case),
):
    try:
        return _issue_token(data, use_case)

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred during user login.",
            },
        )


@router.post(
    "/token",
    response_model=UserLoginResponseSchema,
    tags=["Authentication"],
    summary="Generate an access token for a user",
)
def generate_user_token(
    data: UserLoginSchema,
    use_case: UserLoginUseCase = Depends(get_user_login_use_case),
):
    try:
        return _issue_token(data, use_case)

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred while generating the user token.",
            },
        )


@router.post(
    "/refresh",
    response_model=UserLoginResponseSchema,
    tags=["Authentication"],
    summary="Refresh access token",
)
def refresh_user_token(
    data: RefreshTokenSchema,
    use_case: UserRefreshTokenUseCase = Depends(get_user_refresh_token_use_case),
):
    try:
        return _refresh_token(data, use_case)

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred while refreshing the token.",
            },
        )


@router.post(
    "/logout",
    response_model=LogoutResponseSchema,
    tags=["Authentication"],
    summary="Logout user and revoke session",
)
def logout_user(
    token: str = Depends(get_current_token),
    use_case: UserLogoutUseCase = Depends(get_user_logout_use_case),
):
    try:
        return use_case.execute(token)

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred while performing logout.",
            },
        )


@router.get(
    "/generate-code",
    tags=["Authentication"],
    summary="Generate a verification code for a user",
)
def generate_verification_code(
    useremail: str,
    db_code: RedisCache = Depends(get_redis_cache_code),
    email_service=Depends(get_email_service),
):
    try:
        if db_code.get(useremail) is not None:
            raise ValueError("A verification code has already been sent to this email.")

        expiration_time = 300
        code = str(random.randint(100000, 999999))

        db_code.set(useremail, code, ttl=expiration_time)

        email_service.send_email(
            to_email=useremail,
            subject="Your Verification Code",
            body=f"Your verification code is: {code}",
            html=False,
        )

        return {
            "status": "success",
            "message": f"Verification code generated and stored for {useremail}.",
        }

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(ve),
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An error occurred while generating the verification code",
            },
        )


@router.get("/me")
def get_me(current_session: dict = Depends(get_current_session)):
    return {
        "message": "Usuario autenticado com sessao ativa no Redis.",
        "user": {
            "userid": current_session["session"]["user_id"],
            "username": current_session["session"]["username"],
            "useremail": current_session["session"]["useremail"],
            "userposition": current_session["session"]["userposition"],
        },
    }

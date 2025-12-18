from fastapi import Depends

from app.infrastructure.repositories.user_repository import UserRepository
from app.application.user_use_case import UserRegisterUseCase, UserLoginUseCase
from app.infrastructure.db import get_db as get_db_session
from app.application.services.jwt_service import JWTService
from app.infrastructure.redis_service import RedisCache
from app.infrastructure.email_service import SMTPService

def _get_jwt_service() -> JWTService:
    return JWTService()

def _get_redis_cache_token() -> RedisCache:
    return RedisCache(dbc=0)

def get_redis_cache_code() -> RedisCache:
    return RedisCache(dbc=1)

def get_user_repository(db_session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session)


def get_user_register_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserRegisterUseCase:
    return UserRegisterUseCase(user_repository)

def get_user_login_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service = Depends(_get_jwt_service),
    db_token = Depends(_get_redis_cache_token),
    db_code = Depends(get_redis_cache_code),
) -> UserLoginUseCase:
    return UserLoginUseCase(
        user_repository,
        jwt_service,
        db_token,
        db_code,
    )

def get_email_service() -> SMTPService:
    return SMTPService()
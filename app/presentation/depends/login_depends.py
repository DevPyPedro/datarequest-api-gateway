from fastapi import Depends

from app.infrastructure.repositories.user_repository import UserRepository
from app.application.user_use_case import UserRegisterUseCase
from app.infrastructure.db import get_db as get_db_session


def get_user_repository(db_session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session)


def get_user_register_use_case(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserRegisterUseCase:
    return UserRegisterUseCase(user_repository)

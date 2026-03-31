from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.application.services.jwt_service import JWTService
from app.application.dto.login_dto import RegisterUserDTO, LoginUserDTO, RefreshTokenDTO
from app.infrastructure.redis_service import RedisCache
from app.infrastructure.hash_service import PasswordService
from datetime import timedelta
from uuid import uuid4

class UserRegisterUseCase:
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    def execute(self, user_data: RegisterUserDTO):
        
        if  self._user_exists(user_data.useremail):
            raise ValueError("User already exists")
    
        new_user = self.user_repository.create_user(user_data)

        if new_user is None:
            raise Exception("User creation failed")
        
        return {"status": str(new_user) , "message": "User created successfully."}
    
    def _user_exists(self, email: str) -> bool:
        return self.user_repository.user_exists(email)
        
    
class UserLoginUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        jwt_service: JWTService,
        db_token: RedisCache,
        db_code: RedisCache,
    ):
        self.user_repository = user_repository
        self.jwt_service = jwt_service
        self.db_token = db_token
        self.db_code = db_code

    def execute(self, login_data: LoginUserDTO) -> dict:
        user = self.user_repository.get_user_by_email(login_data.useremail)
        if user is None:
            raise ValueError("User does not exist")

        if not self._check_code(login_data.useremail, login_data.code_verification):
            raise ValueError("Invalid verification code")

        if not self._check_password(login_data.userpassword, user.userpassword):
            raise ValueError("Invalid credentials")

        access_token, refresh_token, session_id = self._generate_tokens(user)
        self._store_session(user, session_id, access_token, refresh_token)
        self.db_code.delete(login_data.useremail)

        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def _user_exists(self, email: str) -> bool:
        return self.user_repository.user_exists(email)

    def _generate_tokens(self, user) -> tuple[str, str, str]:
        session_id = str(uuid4())
        access_token = self.jwt_service.create_access_token(
            data={
                "sub": user.useremail,
                "user_id": user.userid,
                "username": user.username,
                "user_position": user.userposition,
                "sid": session_id,
                "token_type": "access",
            },
            expires_delta=timedelta(minutes=self.jwt_service.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = self.jwt_service.create_access_token(
            data={
                "sub": user.useremail,
                "user_id": user.userid,
                "sid": session_id,
                "token_type": "refresh",
            },
            expires_delta=timedelta(minutes=self.jwt_service.REFRESH_TOKEN_EXPIRE_MINUTES),
        )
        return access_token, refresh_token, session_id

    def _store_session(self, user, session_id: str, access_token: str, refresh_token: str):
        ttl_seconds = self.jwt_service.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        self.db_token.set_json(
            f"session:{session_id}",
            {
                "user_id": user.userid,
                "username": user.username,
                "useremail": user.useremail,
                "userposition": user.userposition,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            ttl=ttl_seconds,
        )
    
    def _check_code(self, email: str, code: int) -> bool:
        stored_code = self.db_code.get(email)
        return stored_code is not None and int(stored_code) == code

    def _check_password(self, password: str, hashed_password: str) -> bool:
        return PasswordService.verify_password(password, hashed_password)


class UserRefreshTokenUseCase:
    def __init__(
        self,
        jwt_service: JWTService,
        db_token: RedisCache,
    ):
        self.jwt_service = jwt_service
        self.db_token = db_token

    def execute(self, refresh_data: RefreshTokenDTO) -> dict:
        payload = self.jwt_service.decode_access_token(refresh_data.refresh_token)
        if payload is None:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("token_type") != "refresh":
            raise ValueError("Invalid token type")

        session_id = payload.get("sid")
        if not session_id:
            raise ValueError("Session information missing from token")

        session_key = f"session:{session_id}"
        session = self.db_token.get_json(session_key)
        if session is None:
            raise ValueError("Session expired or revoked")

        if session.get("refresh_token") != refresh_data.refresh_token:
            raise ValueError("Refresh token revoked")

        access_token = self.jwt_service.create_access_token(
            data={
                "sub": session["useremail"],
                "user_id": session["user_id"],
                "username": session["username"],
                "user_position": session["userposition"],
                "sid": session_id,
                "token_type": "access",
            },
            expires_delta=timedelta(minutes=self.jwt_service.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        rotated_refresh_token = self.jwt_service.create_access_token(
            data={
                "sub": session["useremail"],
                "user_id": session["user_id"],
                "sid": session_id,
                "token_type": "refresh",
            },
            expires_delta=timedelta(minutes=self.jwt_service.REFRESH_TOKEN_EXPIRE_MINUTES),
        )

        self.db_token.set_json(
            session_key,
            {
                **session,
                "access_token": access_token,
                "refresh_token": rotated_refresh_token,
            },
            ttl=self.jwt_service.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {
            "status": "success",
            "message": "Token refreshed successfully",
            "access_token": access_token,
            "refresh_token": rotated_refresh_token,
            "token_type": "bearer",
        }


class UserLogoutUseCase:
    def __init__(
        self,
        jwt_service: JWTService,
        db_token: RedisCache,
    ):
        self.jwt_service = jwt_service
        self.db_token = db_token

    def execute(self, access_token: str) -> dict:
        payload = self.jwt_service.decode_access_token(access_token)
        if payload is None:
            raise ValueError("Invalid or expired token")

        if payload.get("token_type") != "access":
            raise ValueError("Invalid token type")

        session_id = payload.get("sid")
        if not session_id:
            raise ValueError("Session information missing from token")

        self.db_token.delete(f"session:{session_id}")

        return {
            "status": "success",
            "message": "Logout completed successfully",
        }

from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.application.services.jwt_service import JWTService
from app.application.dto.login_dto import RegisterUserDTO, LoginUserDTO
from app.infrastructure.redis_service import RedisCache

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
        return not self.user_repository.user_exists(email).empty
        
    
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
        if not self._user_exists(login_data.useremail):
            raise ValueError("User does not exist")

        token = self._generate_token(login_data)
        self._store_token(login_data.useremail, token)

        if not self._check_code(login_data.useremail, login_data.code_verification):
            raise ValueError("Invalid verification code")
        
        self.db_code.delete(login_data.useremail)
        

        return {"status": "success", "message": "Login successful", "access_token": token, "token_type": "bearer"}

    def _user_exists(self, email: str) -> bool:
        return not self.user_repository.user_exists(email).empty

    def _generate_token(self, login_data: LoginUserDTO) -> str:
        return self.jwt_service.create_access_token(
            data={"sub": login_data.useremail},
            expires_delta=60,
        )
    
    def _store_token(self, email: str, token: str):
        self.db_token.set(email, token) # Token expires in 30 minutes
        self.db_token.expire(email, 1800)
    
    def _check_code(self, email: str, code: int) -> bool:
        stored_code = self.db_code.get(email)
        return stored_code is not None and int(stored_code) == code

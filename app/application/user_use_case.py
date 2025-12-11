from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.application.services.jwt_service import JWTService
from app.application.dto.login_dto import RegisterUserDTO

class UserRegisterUseCase:
    
    def __init__(self, user_repository: UserRepositoryInterface, db: any = None):
        self.user_repository = user_repository
        self.db = db # Optigonal database session if needed (db using for transactions commit/rollback)

    def execute(self, user_data: RegisterUserDTO):
        try:
            result = self.user_repository.user_exists(user_data.useremail)
            if not result.empty:
                raise ValueError("User already exists")
        
            new_user = self.user_repository.create_user(user_data)

            if new_user is None:
                raise Exception("User creation failed")
            
            self.db.commit()  # Commit the transaction if using a DB session
            return {"status": str(new_user) , "message": "User created successfully."}
        except Exception as e:
            self.db.rollback()  # Rollback in case of error
            raise e
    
class UserLoginUseCase:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.jwt_service = JWTService()

    def execute(self, user_data: RegisterUserDTO):

        try:
            # Verify if user exists
            result = self.user_repository.user_exists(user_data.useremail)
            if not result.empty:
                raise ValueError("User already exists")
            
            # Create token payload
            self.jwt_service.create_access_token(
                data={"sub": user_data.useremail, "username": user_data.username},
                expires_delta=60
            )

            return {"status": "success", "message": "User logged in successfully.", "token": self.jwt_service.token}
        except Exception as e:
            raise e
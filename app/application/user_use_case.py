from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.application.services.jwt_service import JWTService

class UserReistertionUseCase:
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.jwt_service = JWTService()

    def execute(self, user_data):
        try:
            if self.user_repository.user_exists(user_data['useremail']):
                raise ValueError("User already exists")
        
            new_user = self.user_repository.create_user(user_data)

            if new_user is None:
                raise Exception("User creation failed")
            
            return {"username": new_user, "response": "User created successfully."}
        except Exception as e:
            raise e
    
    



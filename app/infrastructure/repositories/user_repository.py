import pandas as pd 

from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.infrastructure.logs_service import LogService
from app.infrastructure.hash_service import PasswordService
from app.domain.entities.users import User
class UserRepository(UserRepositoryInterface):
    
    def __init__(self, db_session: any):
        self.db_session = db_session
        self.logger = LogService(name="UserRepository")

    def get_user_by_id(self, user_id: int):
        """Logic to retrieve a user by their ID from the database"""
        try:
            result = pd.read_sql(self.db_session.query(User).filter(User.userid == user_id).statement, self.db_session.bind)
            if result.empty:
                return None
            return result.to_dict(orient="records")[0]
        except Exception as e:
            raise e

    def create_user(self, user_data):
        """Logic to create a new user in the database"""
        try:
            hashed_password = PasswordService.hash_password(user_data.userpassword)
            user_data.userpassword = hashed_password

            new_user = User(
                username=user_data.username,
                useremail=user_data.useremail,
                userpassword=user_data.userpassword
            )
            self.db_session.add(new_user)
            return True
        except Exception as e:
            raise e
        
    def user_exists(self, email: str) -> bool:
        """Check if a user with the given email already exists"""
        try:
            result = pd.read_sql(self.db_session.query(User).filter(User.useremail == email).statement, self.db_session.bind)
            return result
        except Exception as e:
            self.logger.error(f"Error checking if user exists: {e}")
            raise e
        
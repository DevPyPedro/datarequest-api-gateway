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
            user = self.db_session.query(User).filter(User.userid == user_id).first()
            if user is None:
                return None
            return {
                "userid": user.userid,
                "username": user.username,
                "useremail": user.useremail,
                "userposition": user.userposition,
            }
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
            user = self.db_session.query(User).filter(User.useremail == email).first()
            return user is not None
        except Exception as e:
            bind = self.db_session.get_bind()
            db_name = getattr(bind.url, "database", "unknown")
            db_host = getattr(bind.url, "host", "unknown")

            self.logger.error(
                f"Error checking if user exists (database={db_name}, host={db_host}): {e}"
            )
            raise e

    def get_user_by_email(self, email: str):
        """Retrieve the full user entity by email."""
        try:
            return self.db_session.query(User).filter(User.useremail == email).first()
        except Exception as e:
            bind = self.db_session.get_bind()
            db_name = getattr(bind.url, "database", "unknown")
            db_host = getattr(bind.url, "host", "unknown")

            self.logger.error(
                f"Error retrieving user by email (database={db_name}, host={db_host}): {e}"
            )
            raise e
        

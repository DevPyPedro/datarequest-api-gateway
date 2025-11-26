import pandas as pd 

from app.domain.repositories.user_repository_interface import UserRepositoryInterface
from app.domain.entities.users import User
class UserRepository(UserRepositoryInterface):
    
    def __init__(self, db_session: any):
        self.db_session = db_session

    def get_user_by_id(self, user_id: int):
        """Logic to retrieve a user by their ID from the database"""
        try:
            result = pd.read_sql(self.db_session.query(User).filter(User.userid == user_id).statement, self.db_session.bind)
            print(result.to_dict(orient="records")[0])
            if result.empty:
                return None
            return result.to_dict(orient="records")[0]
        except Exception as e:
            raise e

    def create_user(self, user_data):
        """Logic to create a new user in the database"""
        try:
            new_user = User(**user_data)
            self.db_session.add(new_user)
            self.db_session.commit()
            return new_user
        except Exception as e:
            self.db_session.rollback()
            raise e
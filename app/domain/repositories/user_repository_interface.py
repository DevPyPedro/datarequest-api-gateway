from abc import ABC, abstractmethod
from typing import Optional

class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Retrieve a user by their ID."""
        pass

    @abstractmethod
    def create_user(self, user_data: dict) -> dict:
        """Create a new user with the provided data."""
        pass

    @abstractmethod
    def user_exists(self, email: str) -> bool:
        """Check if a user exists by their email."""
        pass
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from dotenv import load_dotenv

load_dotenv()


class JWTService:
    """
    Service for handling JSON Web Tokens (JWT) for authentication.
    """
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a new JWT access token.

        Args:
            data: The payload to encode into the token.
            expires_delta: The lifespan of the token. Defaults to configured minutes.

        Returns:
            The encoded JWT token as a string.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodes and validates a JWT access token.

        Args:
            token: The JWT token string to decode.

        Returns:
            The decoded payload as a dictionary if the token is valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # Handle expired token
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None
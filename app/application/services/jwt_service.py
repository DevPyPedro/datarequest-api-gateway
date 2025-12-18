import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import jwt

load_dotenv()


class JWTService:
    """
    Service responsável por criar e validar JSON Web Tokens (JWT).
    """

    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    ISSUER = os.getenv("JWT_ISSUER")  # opcional
    AUDIENCE = os.getenv("JWT_AUDIENCE")  # opcional

    @classmethod
    def _validate_config(cls) -> None:
        if not cls.SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY não está configurada.")

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria um token JWT assinado.

        :param data: Dados que serão inseridos no payload
        :param expires_delta: Tempo de expiração customizado
        :return: Token JWT em formato string
        """
        cls._validate_config()

        to_encode = data.copy()

        now = str(datetime.now(timezone.utc))
        expire = now + str((expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)))

        to_encode.update({
            "exp": expire,
            "iat": now
        })

        # campos opcionais
        if cls.ISSUER:
            to_encode["iss"] = cls.ISSUER

        if cls.AUDIENCE:
            to_encode["aud"] = cls.AUDIENCE

        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica e valida um token JWT.

        :param token: Token JWT
        :return: Payload se for válido, senão None
        """
        cls._validate_config()

        try:
            options = {"verify_aud": bool(cls.AUDIENCE)}

            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM],
                audience=cls.AUDIENCE,
                issuer=cls.ISSUER,
                options=options
            )
            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

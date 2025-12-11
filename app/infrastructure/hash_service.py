import bcrypt

class PasswordService:

    @staticmethod
    def hash_password(password: str) -> str:
        # Gera salt + hash de forma segura
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

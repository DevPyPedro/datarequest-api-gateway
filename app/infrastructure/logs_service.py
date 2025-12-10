import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LogService:
    """
    Serviço de logging centralizado.
    Encapsula a configuração do logger e expõe métodos simples para logar.
    """

    def __init__(
        self,
        name: str = "app",
        level: int = logging.INFO,
        log_file: str = "logs/app.log",
        max_bytes: int = 5_000_000,   # 5MB
        backup_count: int = 5
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # Evita log duplicado

        # Garantir diretório existente
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        # Handler de arquivo com rotação
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )

        # Formatação
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"
        )
        file_handler.setFormatter(formatter)

        # Console handler (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Adicionar handlers
        if not self.logger.handlers:  # evita múltiplos handlers ao recriar
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    # Métodos de conveniência
    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def exception(self, message: str):
        """Loga o stacktrace automaticamente"""
        self.logger.exception(message)

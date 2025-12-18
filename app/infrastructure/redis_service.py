from typing import Any, Optional, Union
import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

configCache : dict = {
    'host': os.getenv('REDIS_HOST'),
    'port': int(os.getenv('REDIS_PORT')),
    'password': os.getenv('REDIS_PASSWORD')
}

class RedisCache:
    """
    Classe que implementa o repositório de cache utilizando Redis como backend.
    
    Fornece métodos para armazenar, recuperar e gerenciar dados em cache,
    com suporte a operações de chave-valor simples e estruturas de hash.
    """

    def __init__(
        self, 
        dbc: int, 
        host=configCache['host'], 
        port=configCache['port'], 
        password=configCache['password']
    ):
        """
        Inicializa a conexão com o servidor Redis.

        Args:
            dbc (int): Número do banco Redis a ser utilizado.
            host (str): Endereço do servidor Redis.
            port (int): Porta de conexão com o servidor Redis.
            password (str): Senha para autenticação no Redis.
        """
        self.client = redis.Redis(
            host=host, 
            port=port, 
            password=password, 
            db=dbc, 
            decode_responses=True
        )

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena um valor no Redis com uma chave opcionalmente expirada.

        Args:
            key (str): Chave para armazenar o valor.
            value (Any): Valor a ser armazenado.
            ttl (Optional[int]): Tempo de expiração em segundos. Se None, o valor não expira.
        """
        return self.client.set(key, value, ex=ttl)

    def get(self, key: str) -> Union[str, dict]:
        """
        Recupera um valor do Redis com base na chave.

        Args:
            key (str): Chave do valor a ser recuperado.

        Returns:
            Union[str, dict]: Valor armazenado ou None se não encontrado.
        """
        return self.client.get(key)

    def delete(self, key: str) -> None:
        """
        Remove uma chave e seu valor correspondente do Redis.

        Args:
            key (str): Chave a ser removida.
        """
        self.client.delete(key)

    def hset(self, id_session: str, key_values: dict) -> bool:
        """
        Armazena múltiplos pares chave-valor em uma hash no Redis.

        Se os valores forem listas ou dicionários, são serializados como JSON.

        Args:
            id_session (str): Identificador da hash no Redis.
            key_values (dict): Dicionário contendo os pares chave-valor.

        Returns:
            bool: True se ao menos um campo foi atualizado, False caso contrário.
        """
        serialized_key_values = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else v 
            for k, v in key_values.items()
        }
        return self.client.hset(id_session, mapping=serialized_key_values)

    def hgetall(self, id_session: str) -> dict:
        """
        Recupera todos os pares chave-valor de uma hash no Redis.

        Args:
            id_session (str): Identificador da hash no Redis.

        Returns:
            dict: Dicionário com os pares armazenados na hash.
        """
        result = self.client.hgetall(id_session)
        return {k: json.loads(v) for k, v in result.items()}

    def expire(self, id_session: str, timeout: int) -> None:
        """
        Define um tempo de expiração para uma chave no Redis.

        Args:
            id_session (str): Chave que terá a expiração definida.
            timeout (int): Tempo de expiração em segundos.
        """
        self.client.expire(id_session, timeout)
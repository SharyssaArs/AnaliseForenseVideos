import logging
from typing import Optional

import redis
from redis.exceptions import RedisError

from core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Retorna uma instância única do cliente Redis.
    Se o Redis estiver indisponível, retorna None sem derrubar a aplicação.
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
        _redis_client.ping()
        return _redis_client

    except RedisError as error:
        logger.warning("Redis indisponível: %s", error)
        _redis_client = None
        return None


def set_cache(key: str, value: str, ttl: int = 60) -> bool:
    """
    Salva um valor no cache pelo tempo informado em segundos.
    """
    client = get_redis_client()

    if client is None:
        return False

    try:
        client.setex(key, ttl, value)
        return True

    except RedisError as error:
        logger.warning("Erro ao salvar cache no Redis: %s", error)
        return False


def get_cache(key: str) -> Optional[str]:
    """
    Busca um valor no cache.
    Retorna None se a chave não existir ou se o Redis estiver indisponível.
    """
    client = get_redis_client()

    if client is None:
        return None

    try:
        return client.get(key)

    except RedisError as error:
        logger.warning("Erro ao buscar cache no Redis: %s", error)
        return None


def delete_cache(key: str) -> bool:
    """
    Remove uma chave do cache.
    """
    client = get_redis_client()

    if client is None:
        return False

    try:
        return bool(client.delete(key))

    except RedisError as error:
        logger.warning("Erro ao remover cache no Redis: %s", error)
        return False
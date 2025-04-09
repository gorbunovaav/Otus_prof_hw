import redis
import json
import time
import logging

logger = logging.getLogger(__name__)


class Store:
    def __init__(self, host='localhost', port=6379, db=0, reconnect_attempts=3, timeout=1.0):
        self.host = host
        self.port = port
        self.db = db
        self.reconnect_attempts = reconnect_attempts
        self.timeout = timeout
        self._connect()

    def _connect(self):
        self._client = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db,
            socket_connect_timeout=self.timeout,
            socket_timeout=self.timeout,
            decode_responses=True,
        )

    def _with_retries(self, func, *args, critical=True, **kwargs):
        attempts = self.reconnect_attempts
        while attempts > 0:
            try:
                return func(*args, **kwargs)
            except redis.exceptions.RedisError as e:
                logger.warning(f"Redis error: {e}. Attempts left: {attempts-1}")
                attempts -= 1
                time.sleep(0.1)
                try:
                    self._connect()
                except Exception as conn_e:
                    logger.error(f"Reconnect failed: {conn_e}")
        if critical:
            raise ConnectionError("Failed to connect to Redis after several attempts.")
        return None

    def cache_get(self, key):
        return self._with_retries(self._client.get, key, critical=False)

    def cache_set(self, key, value, ex=3600):
        return self._with_retries(self._client.set, key, value, ex=ex, critical=False)

    def get(self, key):
        result = self._with_retries(self._client.get, key, critical=True)
        if result is None:
            raise ValueError("No data found in persistent store")
        return result

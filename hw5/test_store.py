import pytest
from unittest.mock import MagicMock, patch
from store import Store
import redis


def test_cache_get_success():
    mock_redis = MagicMock()
    mock_redis.get.return_value = "cached-value"
    
    with patch("store.redis.StrictRedis", return_value=mock_redis):
        store = Store()
        result = store.cache_get("some-key")
        assert result == "cached-value"
        mock_redis.get.assert_called_once_with("some-key")


def test_cache_get_retry_and_fail_gracefully():
    mock_redis = MagicMock()
    mock_redis.get.side_effect = redis.exceptions.ConnectionError("fail")

    with patch("store.redis.StrictRedis", return_value=mock_redis):
        store = Store(reconnect_attempts=2)
        result = store.cache_get("key")
        assert result is None


def test_get_retry_and_raise():
    mock_redis = MagicMock()
    mock_redis.get.side_effect = redis.exceptions.TimeoutError("boom")

    with patch("store.redis.StrictRedis", return_value=mock_redis):
        store = Store(reconnect_attempts=2)
        with pytest.raises(ConnectionError):
            store.get("key")


def test_get_retry_then_success():
    mock_redis = MagicMock()
    mock_redis.get.side_effect = [redis.exceptions.TimeoutError("1"), "final-result"]

    with patch("store.redis.StrictRedis", return_value=mock_redis):
        store = Store(reconnect_attempts=2)
        result = store.get("key")
        assert result == "final-result"
        assert mock_redis.get.call_count == 2


def test_connect_called_on_error():
    first_client = MagicMock()
    second_client = MagicMock()
    first_client.get.side_effect = redis.exceptions.RedisError("fail")

    with patch("store.redis.StrictRedis", side_effect=[first_client, second_client]) as redis_class:
        store = Store(reconnect_attempts=2)
        store.get("key") 
        assert redis_class.call_count >= 2

import pytest
from store import Store


@pytest.fixture(scope="module")
def real_store():
    store = Store(host="localhost", port=6379, db=15, reconnect_attempts=1)
    store._client.flushdb()
    return store


def test_cache_set_and_get(real_store):
    key, value = "some-key", "some-value"
    assert real_store.cache_set(key, value, ex=10)
    result = real_store.cache_get(key)
    assert result == value


def test_get_existing_key(real_store):
    key, value = "persist-key", "important"
    real_store._client.set(key, value)
    assert real_store.get(key) == value


def test_get_missing_key_raises(real_store):
    with pytest.raises(ValueError):
        real_store.get("nonexistent-key")


def test_cache_get_missing_key_returns_none(real_store):
    assert real_store.cache_get("missing") is None


def test_cache_expiry(real_store):
    real_store.cache_set("temp", "data", ex=1)
    assert real_store.cache_get("temp") == "data"
    import time
    time.sleep(1.1)
    assert real_store.cache_get("temp") is None

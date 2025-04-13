# tests/test_scoring.py
import pytest
from scoring import get_score, get_interests
from datetime import datetime
import json

class DummyStore:
    def __init__(self, cache=None, persistent=None):
        self.cache = cache or {}
        self.persistent = persistent or {}

    def cache_get(self, key):
        return self.cache.get(key)

    def cache_set(self, key, value, ex=3600):
        self.cache[key] = value

    def get(self, key):
        if key in self.persistent:
            return self.persistent[key]
        raise ValueError("No data")

def test_get_score_cached():
    store = DummyStore(cache={"uid:abc": "5.0"})
    score = get_score(store, first_name="Ivan", last_name="Ivanov", phone="71234567890")
    assert score == 5.0

def test_get_score_calc_and_cache():
    store = DummyStore()
    score = get_score(store, first_name="Ivan", last_name="Ivanov", phone="71234567890", email="test@example.com")
    assert score == 3.5
    assert len(store.cache) == 1

def test_get_score_cache_failure_ok():
    class FailingCacheStore(DummyStore):
        def cache_get(self, key): raise Exception("cache down")
        def cache_set(self, key, value, ex=3600): pass

    store = FailingCacheStore()
    score = get_score(store, phone="71234567890", email="test@example.com")
    assert score == 3.0  

def test_get_interests_success():
    store = DummyStore(persistent={"i:42": json.dumps(["books", "music"])})
    interests = get_interests(store, "42")
    assert interests == ["books", "music"]

def test_get_interests_fail_on_store():
    store = DummyStore()
    with pytest.raises(ValueError):
        get_interests(store, "999")

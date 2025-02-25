"""
TODO:

Define a decorator that wraps a function and returns a function with the same signature.
"""
from typing import Callable, TypeVar
import functools

T = TypeVar("T", bound=Callable)

def decorator(func: T) -> T:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrapper  # type: ignore
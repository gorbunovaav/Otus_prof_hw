"""
TODO:

The function `add` accepts two arguments and returns a value, they all have the same type.
The type can only be str or int.
"""
from typing import TypeVar, List

T = TypeVar("T", int, str)

def add(a: T, b: T) -> T:
    return a + b 
"""
TODO:

The function `add` accepts one argument and returns a value, they all have the same type.
The type can only be int or subclasses of int.
"""

from typing import TypeVar, List

T = TypeVar("T", bound=int)

def add(a: T) -> T:
    return a 
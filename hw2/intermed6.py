from typing import TypeVar, List

T = TypeVar("T", int, str, List[str])

def add(a: T, b: T) -> T:
    return a + b  
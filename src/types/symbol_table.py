from collections import UserDict
from dataclasses import dataclass

from src.types.types import Type

@dataclass
class SymbolTable(UserDict):
    def __init__(self, data={}):
        super().__init__(data)

from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class Type:
    pass


@dataclass
class BaseType(Type, Enum):
    INT = "int"
    BOOL = "bool"
    # varchar, etc.


@dataclass
class Schema(Type):
    fields: Dict[str, Type]

    def is_subtype(self, other: Schema) -> bool:
        for field_name, field_type in other.fields:
            if field_name not in self.fields or self.fields[field_name] != field_type:
                return False
        return True


@dataclass
class Expression(Type):
    inputs: Schema
    output: BaseType


class TypeCheckingError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


@dataclass
class RedefinedNameError(TypeCheckingError):
    name: str

    def __init__(self, name: str):
        super().__init__(name)


@dataclass
class TypeMismatchError(TypeCheckingError):
    want: Type
    got: Type

    def __init__(self, want: Type, got: Type):
        super().__init__(f"want {want}, got {got}")

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class Type:
    pass


class BaseType(Type, Enum):
    INT = "INT"
    BOOL = "BOOL"
    VARCHAR = "VARCHAR"


TableFieldPair = Tuple[str, str]


@dataclass
class Schema(Type):
    fields: Dict[str, BaseType]

    def is_subtype(self, other) -> bool:
        for field_name, field_type in other.fields:
            if field_name not in self.fields or self.fields[field_name] != field_type:
                return False
        return True

    @classmethod
    def concat(cls, left, right):
        new_fields = left.fields
        new_fields.update(right.fields)
        return Schema(new_fields)


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


@dataclass
class NameMissingError(TypeCheckingError):
    name: str

    def __init__(self, name: str):
        super().__init__(name)

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import DefaultDict, Dict, Tuple


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

    def is_subtype(self, other: Schema) -> bool:
        for field_name, field_type in other.fields.items():
            if field_name not in self.fields or self.fields[field_name] != field_type:
                return False
        return True

    @classmethod
    def concat(cls, left: Schema, right: Schema, keep_all=False):
        new_fields = {}

        total_field_name_counts: DefaultDict[str, int] = defaultdict(int)
        current_field_name_counts: DefaultDict[str, int] = defaultdict(int)
        for field in left.fields:
            total_field_name_counts[field] += 1
        for field in right.fields:
            total_field_name_counts[field] += 1

        for field in left.fields:
            if keep_all and total_field_name_counts[field] > 1:
                current_field_name_counts[field] += 1
                new_fields[f"{field}_{current_field_name_counts[field]}"] = left.fields[field]
            else:
                new_fields[field] = left.fields[field]
        for field in right.fields:
            if total_field_name_counts[field] > 1:
                if keep_all:
                    current_field_name_counts[field] += 1
                    new_fields[f"{field}_{current_field_name_counts[field]}"] = right.fields[field]
                elif new_fields[field] != right.fields[field]:
                    raise SchemaConcatConflictError(
                        field, new_fields[field], right.fields[field])
            else:
                new_fields[field] = right.fields[field]

        return Schema(new_fields)

    def expand(self, table_name: str) -> Schema:
        new_fields = {}
        for field in self.fields:
            new_fields[f"{table_name}.{field}"] = self.fields[field]
        return Schema(new_fields)

    def simplify(self) -> Schema:
        new_fields = {}
        field_name_counts: DefaultDict[str, int] = defaultdict(int)
        for field in self.fields:
            field_name = field.split(".")[-1]
            field_name_counts[field_name] += 1
        for field in self.fields:
            field_name = field.split(".")[-1]
            if field_name_counts[field_name] > 1:
                new_fields[field] = self.fields[field]
            else:
                new_fields[field_name] = self.fields[field]
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
class SchemaConcatConflictError(TypeCheckingError):
    field: str
    previous: BaseType
    new_type: BaseType

    def __init__(self, field: str, previous: BaseType, new_type: BaseType):
        super().__init__(
            f"Schema already has field {field} with type {previous}, cannot add with type {new_type}")

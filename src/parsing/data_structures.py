from dataclasses import dataclass
from typing import Optional

from src.types.symbol_table import SymbolTable
from src.types.types import Expression, Type, TypeMismatchError


@dataclass
class Expr():
    # Class is here instead of expr.py to avoid circular import

    def type_check(self, st: SymbolTable) -> Expression:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")

    def expect_type(self, st: SymbolTable, expected: Type) -> Type:
        actual = self.type_check(st)
        if actual != expected:
            raise TypeMismatchError(expected, actual)
        return actual

    def get_name(self) -> str:
        raise NotImplementedError(f"TODO: write get_name() for {type(self)}")


@dataclass
class SExpr():
    expr: Expr
    name: Optional[str] = None

    def type_check(self, st: SymbolTable) -> Expression:
        return self.expr.type_check(st)

    def get_name(self) -> str:
        return self.name or self.expr.get_name()

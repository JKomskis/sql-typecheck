from dataclasses import dataclass

from src.types.symbol_table import SymbolTable
from src.types.types import Type, TypeMismatchError


@dataclass
class Expr():
    # Class is here instead of expr.py to avoid circular import

    def type_check(self, st: SymbolTable) -> Type:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")

    def expect_type(self, st: SymbolTable, expected: Type) -> Type:
        actual = self.type_check(st)
        if actual != expected:
            raise TypeMismatchError(expected, actual)
        return actual

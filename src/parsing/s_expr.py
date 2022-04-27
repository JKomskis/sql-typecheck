from dataclasses import dataclass
from typing import Optional

from parsy import generate, whitespace
from src.parsing.expr import Expr, expr
from src.parsing.terminals import identifier, string_ignore_case
from src.types.symbol_table import SymbolTable
from src.types.types import Expression


@dataclass
class SExpr():
    expr: Expr
    name: Optional[str] = None

    def type_check(self, st: SymbolTable) -> Expression:
        return self.expr.type_check(st)

    def get_name(self) -> str:
        return self.name or self.expr.get_name()


@generate
def s_expr():
    internal_expr = yield expr
    name = yield (whitespace >> string_ignore_case("AS") >> whitespace >> identifier).optional()
    return SExpr(internal_expr, name)

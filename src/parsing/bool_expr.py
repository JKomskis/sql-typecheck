from dataclasses import dataclass
from parsy import generate, whitespace, eof

from src.parsing.terminals import bool_literal, string_ignore_case, lparen, rparen

@dataclass
class BExpr():
    pass

@dataclass
class BExprBoolLiteral(BExpr):
    value: bool

@dataclass
class BExprAnd(BExpr):
    left: BExpr
    right: BExpr

@dataclass
class BExprNot(BExpr):
    node: BExpr

@generate
def b_expr_bool_literal():
    value = yield bool_literal

    return BExprBoolLiteral(value)

@generate
def b_expr() -> BExpr:
    node = yield b_expr_internal

    while True:
        more_to_parse = yield whitespace.optional()
        if more_to_parse == None:
            break

        yield string_ignore_case("AND")
        yield whitespace
        right = yield b_expr_internal

        node = BExprAnd(node, right)

    return node

@generate
def b_expr_internal() -> BExpr:
    negate = yield (string_ignore_case("NOT") << whitespace).optional()
    node = yield b_expr_internal_internal
    if negate != None:
        node = BExprNot(node)
    return node

@generate
def b_expr_internal_internal() -> BExpr:
    node = yield lparen >> b_expr << rparen | b_expr_bool_literal | b_expr
    return node

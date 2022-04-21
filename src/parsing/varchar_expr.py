from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string

from src.parsing.data_structures import Expr
from src.parsing.expr import expr
from src.parsing.int_expr import IExpr, i_expr, i_expr_int_literal
from src.parsing.terminals import string_ignore_case, varchar_literal, lparen, rparen, c_name, padding, sep

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TableFieldPair, TypeMismatchError


@dataclass
class VExpr(Expr):
    pass


@dataclass
class VExprVarcharLiteral(VExpr):
    value: str

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.VARCHAR
        )


@dataclass
class VExprColumn(VExpr):
    table_column_name: TableFieldPair

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]

        if table_schema.fields[col] != BaseType.VARCHAR:
            raise TypeMismatchError(BaseType.VARCHAR, table_schema.fields[col])

        return Expression(
            Schema({f"{table}.{col}": BaseType.VARCHAR}),
            BaseType.VARCHAR
        )


# class VarcharOp(Enum):
#     CONCAT = 1
#     SUBSTR = 2


@dataclass
class VExprConcat(VExpr):
    left: VExpr
    right: VExpr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        if left_type.output != BaseType.VARCHAR:
            raise TypeMismatchError(BaseType.VARCHAR, left_type)
        right_type = self.right.type_check(st)
        if right_type.output != BaseType.VARCHAR:
            raise TypeMismatchError(BaseType.VARCHAR, right_type)
        return Expression(
            Schema.concat(left_type.inputs, right_type.inputs),
            BaseType.VARCHAR
        )


@dataclass
class VExprSubstr(VExpr):
    input: VExpr
    start: IExpr
    end: IExpr

    def type_check(self, st: SymbolTable) -> Expression:
        input_type = self.left.type_check(st)
        if input_type.output != BaseType.VARCHAR:
            raise TypeMismatchError(BaseType.VARCHAR, input_type)
        start_type = self.start.type_check(st)
        if start_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, start_type)
        end_type = self.end.type_check(st)
        if end_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, end_type)
        return Expression(
            Schema.concat(input_type.inputs),
            BaseType.VARCHAR
        )


@generate
def v_expr_varchar_literal():
    value = yield string('"') >> varchar_literal << string('"')
    return VExprVarcharLiteral(value)


@generate
def v_expr_column():
    name = yield c_name

    return VExprColumn(name)


@generate
def v_expr():
    node = yield v_expr_paren_terminal
    return node


@generate
def v_expr_concat():
    yield (string_ignore_case("CONCAT(") >> padding)
    left = yield (v_expr_varchar_literal | v_expr_column | v_expr_substr | v_expr_concat)
    yield padding >> string(",") >> padding
    right = yield (v_expr_varchar_literal | v_expr_column | v_expr_substr | v_expr_concat)
    yield padding >> string(")")
    return VExprConcat(left, right)


@generate
def v_expr_substr():
    yield (string_ignore_case("SUBSTR(") >> padding)
    input = yield (v_expr_varchar_literal | v_expr_column | v_expr_concat | v_expr_substr)
    yield padding >> string(",") >> padding
    start = yield i_expr
    yield padding >> string(",") >> padding
    end = yield i_expr
    yield padding >> string(")")
    return VExprSubstr(input, start, end)


@generate
def v_expr_paren_terminal():
    node = yield v_expr_varchar_literal \
        | v_expr_concat \
        | v_expr_substr
    return node


# TODO: Concat within concat/concat within substr, can be nested,
# and concat(literal , col) is valid.

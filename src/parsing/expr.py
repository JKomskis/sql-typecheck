from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from parsy import generate, string, whitespace
from src.parsing.terminals import (bool_literal, c_name, int_literal, lparen,
                                   padding, rparen, string_ignore_case,
                                   varchar_literal)
from src.types.symbol_table import SymbolTable
from src.types.types import AggregationMismatchError, AggregationStatus, BaseType, Expression, Schema, TypeCheckingError, TypeMismatchError


@dataclass
class Expr():
    # Class is here instead of expr.py to avoid circular import

    def type_check(self, st: SymbolTable) -> Expression:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")

    def get_name(self) -> str:
        raise NotImplementedError(f"TODO: write get_name() for {type(self)}")

    def aggregation_status(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        if self in group_by_exprs:
            if isinstance(self, ExprColumn):
                return AggregationStatus.EITHER
            return AggregationStatus.AGGREGATED

        return self.aggregation_status_internal(group_by_exprs)

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        raise NotImplementedError(
            f"TODO: write aggregation_status_internal() for {type(self)}")


@dataclass
class ExprColumn(Expr):
    table_column_name: Tuple[str, str]

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]

        return Expression(
            Schema({f"{table}.{col}": table_schema.fields[col]}),
            table_schema.fields[col]
        )

    def get_name(self) -> str:
        return self.table_column_name[1]

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        # If the column was aggregated it would have been caught in aggregation_status
        return AggregationStatus.NOT_AGGREGATED


@dataclass
class ExprIntLiteral(Expr):
    value: int

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.INT
        )

    def get_name(self) -> str:
        return str(self.value)

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        # Literals can always be viewed as an aggregation
        return AggregationStatus.EITHER


@dataclass
class ExprBoolLiteral(Expr):
    value: bool

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.BOOL
        )

    def get_name(self) -> str:
        return str(self.value).lower()

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        # Literals can always be viewed as an aggregation
        return AggregationStatus.EITHER


@dataclass
class ExprVarcharLiteral(Expr):
    value: str

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.VARCHAR
        )

    def get_name(self) -> str:
        return self.value

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        # Literals can always be viewed as an aggregation
        return AggregationStatus.EITHER


@dataclass
class ExprConcat(Expr):
    left: Expr
    right: Expr

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

    def get_name(self) -> str:
        return f'{self.left.get_name()}_{self.right.get_name()}'

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        return AggregationStatus.combine(
            self.left.aggregation_status(group_by_exprs),
            self.right.aggregation_status(group_by_exprs)
        )


@dataclass
class ExprSubstr(Expr):
    input: Expr
    start: Expr
    end: Expr

    def type_check(self, st: SymbolTable) -> Expression:
        input_type = self.input.type_check(st)
        if input_type.output != BaseType.VARCHAR:
            raise TypeMismatchError(BaseType.VARCHAR, input_type)
        start_type = self.start.type_check(st)
        if start_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, start_type)
        end_type = self.end.type_check(st)
        if end_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, end_type)
        final_schema = Schema.concat(input_type.inputs, start_type.inputs)
        final_schema = Schema.concat(final_schema, end_type.inputs)
        return Expression(
            final_schema, 
            BaseType.VARCHAR
        )

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        # For simplicity, don't consider substring ever as an aggregate
        return AggregationStatus.NOT_AGGREGATED


class BinaryOp(Enum):
    MULTIPLICATION = "times"
    ADDITION = "plus"
    AND = "and"
    EQUALS = "equals"
    LESS_THAN = "lessthan"


@dataclass
class ExprBinaryOp(Expr):
    left: Expr
    op: BinaryOp
    right: Expr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        right_type = self.right.type_check(st)
        return_schema = Schema.concat(left_type.inputs, right_type.inputs)
        if self.op == BinaryOp.ADDITION or self.op == BinaryOp.MULTIPLICATION:
            if left_type.output != BaseType.INT:
                raise TypeMismatchError(BaseType.INT, left_type)
            if right_type.output != BaseType.INT:
                raise TypeMismatchError(BaseType.INT, right_type)
            return Expression(return_schema, BaseType.INT)
        elif self.op == BinaryOp.AND:
            if left_type.output != BaseType.BOOL:
                raise TypeMismatchError(BaseType.BOOL, left_type)
            if right_type.output != BaseType.BOOL:
                raise TypeMismatchError(BaseType.BOOL, right_type)
            return Expression(return_schema, BaseType.BOOL)
        elif self.op == BinaryOp.EQUALS:
            if left_type.output != right_type.output:
                raise TypeMismatchError(left_type.output, right_type.output)
            return Expression(return_schema, BaseType.BOOL)
        elif self.op == BinaryOp.LESS_THAN:
            if left_type.output != BaseType.INT and left_type.output != BaseType.VARCHAR:
                raise TypeCheckingError(
                    f"Cannot apply operator {self.op} to type {left_type}")
            if left_type.output != right_type.output:
                raise TypeMismatchError(left_type.output, right_type.output)
            return Expression(return_schema, BaseType.BOOL)
        else:
            raise TypeCheckingError(f"Unknown binary operator {self.op}")

    def get_name(self) -> str:
        return f"{self.left.get_name()}_{self.op.value}_{self.right.get_name()}"

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        return AggregationStatus.combine(
            self.left.aggregation_status(group_by_exprs),
            self.right.aggregation_status(group_by_exprs)
        )


@dataclass
class ExprNot(Expr):
    node: Expr

    def type_check(self, st: SymbolTable) -> Expression:
        node_type = self.node.type_check(st)
        if node_type.output != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, node_type)
        return node_type

    def get_name(self) -> str:
        return f"not_{self.node.get_name()}"

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        return self.node.aggregation_status(group_by_exprs)


class AggOp(Enum):
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    COUNT = "count"


@dataclass
class ExprAgg(Expr):
    op: AggOp
    node: Expr

    def get_name(self) -> str:
        return f"{self.op.value}_{self.node.get_name()}"

    def type_check(self, st: SymbolTable) -> Expression:
        node_type = self.node.type_check(st)
        if self.op == AggOp.MIN or self.op == AggOp.MAX:
            if node_type.output == BaseType.BOOL:
                raise TypeMismatchError(BaseType.INT, BaseType.BOOL)
            return Expression(node_type.inputs, node_type.output)
        elif self.op == AggOp.AVG:
            if node_type.output != BaseType.INT:
                raise TypeMismatchError(BaseType.INT, node_type.output)
            return Expression(node_type.inputs, node_type.output)
        elif self.op == AggOp.COUNT:
            return Expression(node_type.inputs, BaseType.INT)
        else:
            raise TypeCheckingError(f"Unknown aggregation operation {self.op}")

    def aggregation_status_internal(self, group_by_exprs: List[Expr]) -> AggregationStatus:
        if self.node.aggregation_status(group_by_exprs) != AggregationStatus.NOT_AGGREGATED:
            raise AggregationMismatchError(
                f'Cannot aggregate an already aggregated expression {self.node}')
        return AggregationStatus.AGGREGATED


@generate
def expr():
    node = yield expr_negation

    while True:
        res = yield (whitespace >> string_ignore_case("AND") << whitespace).optional()
        if res == None:
            break
        right = yield expr_negation

        node = ExprBinaryOp(node, BinaryOp.AND, right)

    return node


@generate
def expr_negation():
    negate = yield (string_ignore_case("NOT") << whitespace).optional()
    node = yield expr_equality
    if negate != None:
        node = ExprNot(node)
    return node


@generate
def expr_equality():
    left = yield expr_add
    op_str = yield (padding >> (string("=") | string("<")) << padding).optional()
    if op_str == None:
        return left
    op = BinaryOp.EQUALS
    if op_str == "=":
        op = BinaryOp.EQUALS
    elif op_str == "<":
        op = BinaryOp.LESS_THAN
    right = yield expr_add

    return ExprBinaryOp(left, op, right)


@generate
def expr_add():
    node = yield expr_mult

    while True:
        res = yield (padding >> string("+") << padding).optional()
        if res == None:
            break
        right = yield expr_mult

        node = ExprBinaryOp(node, BinaryOp.ADDITION, right)

    return node


@generate
def expr_mult():
    node = yield expr_paren_terminal

    while True:
        res = yield (padding >> string("*") << padding).optional()
        if res == None:
            break
        right = yield expr_paren_terminal

        node = ExprBinaryOp(node, BinaryOp.MULTIPLICATION, right)

    return node


@generate
def expr_paren_terminal():
    node = yield expr_column\
        | expr_int_literal \
        | expr_bool_literal \
        | expr_varchar_literal \
        | expr_concat \
        | expr_substr \
        | expr_agg \
        | lparen >> expr << rparen
    return node


@generate
def expr_column():
    name = yield c_name

    return ExprColumn(name)


@generate
def expr_int_literal():
    value = yield int_literal

    return ExprIntLiteral(value)


@generate
def expr_bool_literal():
    value = yield bool_literal

    return ExprBoolLiteral(value)


@generate
def expr_varchar_literal():
    value = yield string('"') >> varchar_literal << string('"')
    return ExprVarcharLiteral(value)


@generate
def expr_concat():
    yield (string_ignore_case("CONCAT(") >> padding)
    left = yield expr
    yield padding >> string(",") >> padding
    right = yield expr
    yield padding >> string(")")
    return ExprConcat(left, right)


@generate
def expr_substr():
    yield (string_ignore_case("SUBSTR(") >> padding)
    input = yield expr
    yield padding >> string(",") >> padding
    start = yield expr
    yield padding >> string(",") >> padding
    end = yield expr
    yield padding >> string(")")
    return ExprSubstr(input, start, end)


@generate
def expr_agg():
    op = yield expr_agg_op
    node = yield lparen >> expr << rparen

    return ExprAgg(op, node)


expr_agg_op = (string_ignore_case("MIN")
               | string_ignore_case("MAX")
               | string_ignore_case("AVG")
               | string_ignore_case("COUNT")).map(lambda x: AggOp(x))

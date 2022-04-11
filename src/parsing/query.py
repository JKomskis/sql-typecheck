from dataclasses import dataclass
from typing import List
from parsy import generate, whitespace, string

from src.parsing.bool_expr import BExpr, b_expr
from src.parsing.data_structures import Expr
from src.parsing.expr import expr
from src.parsing.terminals import string_ignore_case, padding, t_name, lparen, rparen, sep

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, RedefinedNameError, Schema, Type, TypeMismatchError


@dataclass
class Query():
    def type_check(self, st: SymbolTable) -> Type:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")


@dataclass
class QueryTable(Query):
    table_name: str
    output_table_name: str = None

    def type_check(self, st: SymbolTable) -> Schema:
        schema = st[self.table_name]
        if self.output_table_name is None:
            return schema
        if self.output_table_name in st:
            raise RedefinedNameError(self.output_table_name)
        return schema  # maybe add to symbol table?


@dataclass
class QueryJoin(Query):
    left: Query
    right: Query
    condition: BExpr
    output_name: str

    def type_check(self, st: SymbolTable) -> Type:
        left_schema = self.left.type_check(st)
        right_schema = self.right.type_check(st)
        concat_schema = left_schema | right_schema
        self.condition.expect_type(st, BaseType.BOOL)
        if not concat_schema.is_subtype(cond_type.inputs):
            raise TypeMismatchError(concat_schema, cond_type.inputs)
        return concat_schema


@dataclass
class QuerySelect(Query):
    select_list: List[Expr]
    from_query: Query
    condition: BExpr = None

@dataclass
class QueryIntersect(Query):
    queries: List[QuerySelect]

    def type_check(self, st: SymbolTable) -> Type:
        ty = self.queries[0].type_check(st)
        for query in self.queries:
            newty = query.type_check(st)
            if not newty == ty:
                raise TypeMismatchError(ty, newty)
        return ty

@dataclass
class QueryIntersectUnion(Query):
    queries: List[QueryIntersect]
    # shoudl be QuerySelect OR QueryIntersect

    def type_check(self, st: SymbolTable) -> Type:
        ty = self.queries[0].type_check(st)
        for query in self.queries:
            newty = query.type_check(st)
            if not newty == ty:
                raise TypeMismatchError(ty, newty)
        return ty

@dataclass
class QueryUnion(Query):
    queries: List[QuerySelect]
    # shoudl be QuerySelect OR QueryIntersect

    def type_check(self, st: SymbolTable) -> Type:
        ty = self.queries[0].type_check(st)
        for query in self.queries:
            newty = query.type_check(st)
            if not newty == ty:
                raise TypeMismatchError(ty, newty)
        return ty


@generate
def query() -> Query:
    node = yield query_terminal

    while True:
        res = yield (whitespace >> string_ignore_case("JOIN") << whitespace).optional()
        if res == None:
            break
        right = yield query_terminal
        yield (whitespace >> string_ignore_case("ON") << whitespace)
        condition = yield b_expr
        yield (whitespace >> string_ignore_case("AS") << whitespace)
        output_table_name = yield t_name

        node = QueryJoin(node, right, condition, output_table_name)

    return node


@generate
def query_terminal() -> Query:
    node = yield query_table \
        | query_intersect_union \
        | query_union \
        | query_intersect \
        | query_select \
        | lparen >> query << rparen
    return node


@generate
def query_table() -> QueryTable:
    table_name = yield t_name
    output_table_name = None
    as_token = yield (whitespace >> string_ignore_case("AS") << whitespace).optional()
    if as_token != None:
        output_table_name = yield t_name
    return QueryTable(table_name, output_table_name)


@generate
def query_select() -> QuerySelect:
    yield (padding >> string_ignore_case("SELECT") << whitespace)
    expressions = yield expr.sep_by(sep(","), min=1)
    yield (whitespace >> string_ignore_case("FROM") << whitespace)
    from_query = yield query

    condition = None
    where_token = yield (whitespace >> string_ignore_case("WHERE") << whitespace).optional()
    if where_token != None:
        condition = yield b_expr
    return QuerySelect(expressions, from_query, condition)


@generate
def query_intersect() -> QueryIntersect:
    queries = yield query_select.sep_by(sep("INTERSECT"), min=2)
    return QueryIntersect(queries)

@generate
def query_union() -> QueryUnion:
    queries = yield  query_select.sep_by(sep("UNION"), min=2) 
    # string("ALL").optional() -> handle "UNION ALL" separator as well 
    # (is there a way to have several tokenizer strings?)
    return QueryUnion(queries)

@generate
def query_intersect_union() -> QueryIntersectUnion:
    queries = yield query_intersect.sep_by(sep("UNION"), min=2)
    return QueryIntersectUnion(queries)


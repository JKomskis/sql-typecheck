from dataclasses import dataclass
from typing import List
from parsy import generate, whitespace, string

from src.parsing.bool_expr import BExpr, b_expr
from src.parsing.data_structures import Expr
from src.parsing.expr import expr
from src.parsing.terminals import string_ignore_case, padding, t_name, lparen, rparen, sep


@dataclass
class Query():
    pass


@dataclass
class QueryTable(Query):
    table_name: str
    output_table_name: str = None


@dataclass
class QueryJoin(Query):
    left: Query
    right: Query
    condition: BExpr
    output_name: str


@dataclass
class QuerySelect(Query):
    select_list: List[Expr]
    from_query: Query
    condition: BExpr = None


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

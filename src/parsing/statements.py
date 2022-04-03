from dataclasses import dataclass
from typing import List
from parsy import generate, whitespace

from src.parsing.query import Query, query
from src.parsing.terminals import identifier, string_ignore_case, t_name, c_name, lparen, rparen, type_literal, sep, padding


@dataclass
class Stmt():
    pass


@dataclass
class TableElement():
    column_name: str
    type_str: str


@generate
def table_element() -> TableElement:
    column_name = yield identifier
    yield whitespace
    type_str = yield type_literal
    return TableElement(column_name, type_str)


@dataclass
class StmtCreateTable(Stmt):
    table_name: str
    table_elements: List[TableElement]


@dataclass
class StmtQuery(Stmt):
    query: Query


@dataclass
class StmtSequence(Stmt):
    stmts: List[Stmt]


@generate
def stmt_create_table() -> StmtCreateTable:
    yield padding + string_ignore_case("CREATE") + whitespace + string_ignore_case("TABLE") + whitespace
    table_name = yield t_name
    yield (padding + lparen + padding)
    table_elements = yield table_element.sep_by(sep(","), min=1)
    yield (padding + rparen)
    return StmtCreateTable(table_name, table_elements)


@generate
def stmt_query() -> StmtQuery:
    node = yield query
    return StmtQuery(node)


stmt = stmt_create_table | stmt_query


@generate
def stmt_sequence() -> StmtSequence:
    stmts = yield stmt.sep_by(sep(";"), min=1)
    return StmtSequence(stmts)

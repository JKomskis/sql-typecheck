from dataclasses import dataclass
from typing import List
from parsy import generate, whitespace, string

from src.parsing.query import Query, query
from src.parsing.terminals import identifier, string_ignore_case, t_name, c_name, lparen, rparen, type_literal, sep, padding

from src.types.symbol_table import SymbolTable
from src.types.types import Schema, Type, TypeMismatchError


@dataclass
class Stmt():
    def type_check(self, st: SymbolTable) -> Type:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")


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

    def type_check(self, st: SymbolTable) -> Type:
        return query.type_check(st)
        

@dataclass
class StmtSequence(Stmt):
    stmts: List[Stmt]

    def type_check(self) -> Schema:
        ty = None
        for stmt in self.stmts:
            ty = stmt.type_check(st)
        return ty


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
    stmts = yield stmt.sep_by(sep(";"), min=1) << string(";").optional()
    return StmtSequence(stmts)

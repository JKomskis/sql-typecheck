from src.types.types import BaseType, RedefinedNameError, Schema, Type
from src.types.types import Schema, Type, TypeMismatchError
from dataclasses import dataclass
from typing import List, Tuple
from parsy import generate, whitespace, string

from src.parsing.query import Query, query
from src.parsing.terminals import identifier, string_ignore_case, t_name, c_name, lparen, rparen, type_literal, sep, padding

from src.types.symbol_table import SymbolTable


@dataclass
class Stmt():
    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")


@dataclass
class TableElement():
    column_name: str
    base_type: BaseType


@generate
def table_element():
    column_name = yield identifier
    yield whitespace
    type_str = yield type_literal

    return TableElement(column_name, BaseType(type_str))


@dataclass
class StmtCreateTable(Stmt):
    table_name: str
    table_elements: List[TableElement]

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        schema_fields = {}
        for table_element in self.table_elements:
            if table_element.column_name in schema_fields:
                raise RedefinedNameError(table_element.column_name)
            schema_fields[table_element.column_name] = table_element.base_type
        if self.table_name in st:
            raise RedefinedNameError(self.table_name)
        st[self.table_name] = Schema(schema_fields)
        return (self.table_name, Schema(schema_fields))


@dataclass
class StmtQuery(Stmt):
    query: Query

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        return self.query.type_check(st)


@dataclass
class StmtSequence(Stmt):
    stmts: List[Stmt]

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        table_name = ""
        schema = Schema({})
        for stmt in self.stmts:
            table_name, schema = stmt.type_check(st)
        return table_name, schema


@generate
def stmt_create_table():
    yield padding + string_ignore_case("CREATE") + whitespace + string_ignore_case("TABLE") + whitespace
    table_name = yield t_name
    yield (padding + lparen + padding)
    table_elements = yield table_element.sep_by(sep(","), min=1)
    yield (padding + rparen)
    return StmtCreateTable(table_name, table_elements)


@generate
def stmt_query():
    node = yield query
    return StmtQuery(node)


stmt = stmt_create_table | stmt_query


@generate
def stmt_sequence():
    stmts = yield stmt.sep_by(sep(";"), min=1) << string(";").optional()
    return StmtSequence(stmts)

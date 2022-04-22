from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from parsy import generate, whitespace, string

from src.parsing.bool_expr import BExpr, b_expr
from src.parsing.data_structures import Expr, SExpr
from src.parsing.expr import expr, s_expr
from src.parsing.terminals import string_ignore_case, padding, t_name, lparen, rparen, sep

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, RedefinedNameError, Schema, Type, TypeMismatchError


@dataclass
class Query():
    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        raise NotImplementedError(f"TODO: write typing rule for {type(self)}")

    def get_output_table_name(self) -> str:
        raise NotImplementedError(
            f"TODO: write get_output_table_name for {type(self)}")


@dataclass
class QueryTable(Query):
    table_name: str
    output_table_name: Optional[str] = None

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        schema = st[self.table_name]
        if self.output_table_name is None:
            return self.table_name, schema

        if self.output_table_name in st:
            raise RedefinedNameError(self.output_table_name)
        return self.output_table_name, schema

    def get_output_table_name(self) -> str:
        return self.output_table_name or self.table_name


@dataclass
class QueryJoin(Query):
    left: Query
    right: Query
    condition: BExpr
    output_name: str

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        left_table_name, left_schema = self.left.type_check(st)
        left_schema_expanded = left_schema.expand(left_table_name)
        right_table_name, right_schema = self.right.type_check(st)
        right_schema_expanded = right_schema.expand(right_table_name)
        concat_schema = Schema.concat(
            left_schema_expanded, right_schema_expanded, keep_all=True)

        # The join condition can only reference the two tables being joined
        join_st = SymbolTable(
            {left_table_name: left_schema, right_table_name: right_schema})
        condition_type = self.condition.type_check(join_st)

        if condition_type.output != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, condition_type.output)
        if not concat_schema.is_subtype(condition_type.inputs):
            raise TypeMismatchError(concat_schema, condition_type.inputs)
        return (self.get_output_table_name(), concat_schema.simplify())

    def get_output_table_name(self) -> str:
        return self.output_name


@dataclass
class QuerySelect(Query):
    select_list: List[SExpr]
    from_query: Query
    condition: Optional[BExpr] = None
    groupby: Optional[str] = None

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        output_schema_fields: Dict[str, BaseType] = {}
        from_name, from_schema = self.from_query.type_check(st)
        from_schema_expanded = from_schema.expand(from_name)
        for select_expr in self.select_list:
            # Select expression must only reference from query schema
            select_expr_type = select_expr.type_check(
                SymbolTable({from_name: from_schema}))
            if not from_schema_expanded.is_subtype(select_expr_type.inputs):
                raise TypeMismatchError(
                    from_schema_expanded, select_expr_type.inputs)
            output_schema_fields[select_expr.get_name()
                                 ] = select_expr_type.output

        return (from_name, Schema(output_schema_fields))


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

    def type_check(self, st: SymbolTable) -> Tuple[str, Schema]:
        from_schema = self.from_query.type_check(st)
        condition_type = self.condition.type_check(st)
        # Todo: check if from_schema is a subtype of condition type schema

        schema = Schema({})
        for select_expr in self.select_list:
            expr_type = select_expr.type_check(st)
            # Todo: check if from_schema is a subtype of expression schema

        return self.get_output_table_name(), schema

    def get_output_table_name(self) -> str:
        return self.from_query.get_output_table_name()


@generate
def query():
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
def query_terminal():
    node = yield query_table \
        | query_intersect_union \
        | query_union \
        | query_intersect \
        | query_select \
        | lparen >> query << rparen
    return node


@generate
def query_table():
    table_name = yield t_name
    output_table_name = None
    as_token = yield (whitespace >> string_ignore_case("AS") << whitespace).optional()
    if as_token != None:
        output_table_name = yield t_name
    return QueryTable(table_name, output_table_name)


@generate
def query_select():
    yield (padding >> string_ignore_case("SELECT") << whitespace)
    expressions = yield s_expr.sep_by(sep(","), min=1)
    yield (whitespace >> string_ignore_case("FROM") << whitespace)
    from_query = yield query

    condition = None
    where_token = yield (whitespace >> string_ignore_case("WHERE") << whitespace).optional()
    if where_token != None:
        condition = yield b_expr

    groupby = None
    groupby_token = yield (whitespace >> string_ignore_case("GROUP BY") << whitespace).optional()
    if groupby_token != None:
        groupby = yield t_name

    return QuerySelect(expressions, from_query, condition, groupby)


@generate
def query_intersect():
    queries = yield query_select.sep_by(sep("INTERSECT"), min=2)
    return QueryIntersect(queries)


@generate
def query_union():
    queries = yield query_select.sep_by(sep("UNION"), min=2)
    # string("ALL").optional() -> handle "UNION ALL" separator as well
    # (is there a way to have several tokenizer strings?)
    return QueryUnion(queries)


@generate
def query_intersect_union():
    queries = yield query_intersect.sep_by(sep("UNION"), min=2)
    return QueryIntersectUnion(queries)

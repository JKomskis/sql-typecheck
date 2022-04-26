import unittest

from src.parsing.bool_expr import BExprColumn, BExprEquality, EqualityOperator
from src.parsing.expr import ExprColumn
from src.parsing.int_expr import IExprColumn
from src.parsing.query import QueryJoin, QuerySelect, QueryTable
from src.parsing.statements import (StmtCreateTable, StmtQuery, StmtSequence,
                                    TableElement)
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, RedefinedNameError, Schema


class TestStmtCreate(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })
    student_create_table_ast = StmtCreateTable(
        "students",
        [
            TableElement("ssn", BaseType.INT),
            TableElement("gpa", BaseType.INT),
            TableElement("year", BaseType.INT),
            TableElement("graduate", BaseType.BOOL),
        ]
    )

    enrolled_table_schema = Schema({
        "id": BaseType.INT,
        "grade": BaseType.INT,
        "dropped": BaseType.BOOL,
    })
    enrolled_create_table_ast = StmtCreateTable(
        "enrolled",
        [
            TableElement("id", BaseType.INT),
            TableElement("grade", BaseType.INT),
            TableElement("dropped", BaseType.BOOL),
        ]
    )

    def test_stmt_create(self):
        st = SymbolTable()
        self.assertEqual(
            StmtSequence([TestStmtCreate.student_create_table_ast]
                         ).type_check(st),
            ("students", TestStmtCreate.student_table_schema)
        )
        self.assertEqual(st,
                         SymbolTable({"students": TestStmtCreate.student_table_schema}))

        st = SymbolTable()
        self.assertEqual(
            StmtSequence([TestStmtCreate.student_create_table_ast,
                          TestStmtCreate.enrolled_create_table_ast]
                         ).type_check(st),
            ("enrolled", TestStmtCreate.enrolled_table_schema)
        )
        self.assertEqual(st,
                         SymbolTable({"students": TestStmtCreate.student_table_schema,
                                      "enrolled": TestStmtCreate.enrolled_create_table_ast}))

    def test_stmt_create_redefine_table(self):
        st = SymbolTable()
        with self.assertRaises(RedefinedNameError):
            StmtSequence([TestStmtCreate.student_create_table_ast,
                          TestStmtCreate.student_create_table_ast]
                         ).type_check(st)

    def test_stmt_create_redefine_column(self):
        st = SymbolTable()
        with self.assertRaises(RedefinedNameError):
            StmtSequence([StmtCreateTable(
                "a",
                [
                    TableElement("b", BaseType.INT),
                    TableElement("b", BaseType.BOOL),
                ]
            )]).type_check(st)


class TestStmtQuery(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })
    student_create_table_ast = StmtCreateTable(
        "students",
        [
            TableElement("ssn", BaseType.INT),
            TableElement("gpa", BaseType.INT),
            TableElement("year", BaseType.INT),
            TableElement("graduate", BaseType.BOOL),
        ]
    )

    enrolled_table_schema = Schema({
        "id": BaseType.INT,
        "grade": BaseType.INT,
        "dropped": BaseType.BOOL,
    })
    enrolled_create_table_ast = StmtCreateTable(
        "enrolled",
        [
            TableElement("id", BaseType.INT),
            TableElement("grade", BaseType.INT),
            TableElement("dropped", BaseType.BOOL),
        ]
    )

    def test_stmt_query(self):
        st = SymbolTable()
        self.assertEqual(
            StmtSequence([
                self.student_create_table_ast,
                StmtQuery(QueryTable("students"))
            ]).type_check(st),
            ("students", self.student_table_schema)
        )

        st = SymbolTable()
        self.assertEqual(
            StmtSequence([
                self.student_create_table_ast,
                StmtQuery(QuerySelect(
                    [ExprColumn(("s", "ssn"))],
                    QueryTable("students", "s"),
                    BExprColumn(("s", "graduate"))))
            ]).type_check(st),
            ("s", Schema({
                "ssn": BaseType.INT
            }))
        )

        st = SymbolTable()
        self.assertEqual(
            StmtSequence([
                self.student_create_table_ast,
                self.enrolled_create_table_ast,
                StmtQuery(QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    BExprEquality(
                        IExprColumn(("students", "ssn")),
                        EqualityOperator.EQUALS,
                        IExprColumn(("enrolled", "id"))
                    ),
                    "s_e"
                ))
            ]).type_check(st),
            ("s_e", Schema({
                "ssn": BaseType.INT,
                "gpa": BaseType.INT,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "id": BaseType.INT,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL,
            }))
        )

import unittest
from src.parsing.bool_expr import BExprColumn, BExprEquality, EqualityOperator
from src.parsing.int_expr import IExprColumn

from src.parsing.statements import StmtCreateTable, StmtQuery, StmtSequence, TableElement, stmt_create_table, stmt_sequence
from src.parsing.query import QueryJoin, QuerySelect, QueryTable
from src.parsing.expr import ExprColumn
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, RedefinedNameError, Schema


class TestQueryTable(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })

    def test_query_table(self):
        st = SymbolTable({"students": TestQueryTable.student_table_schema})
        self.assertEqual(QueryTable("students").type_check(st),
                         ("students", TestQueryTable.student_table_schema))

    def test_missing_table(self):
        st = SymbolTable({"students": TestQueryTable.student_table_schema})
        with self.assertRaises(KeyError):
            QueryTable("enrolled").type_check(st)

    def test_query_rename(self):
        st = SymbolTable({"students": TestQueryTable.student_table_schema})
        self.assertEqual(QueryTable("students", "s").type_check(st),
                         ("s", TestQueryTable.student_table_schema))

        st = SymbolTable({"students": TestQueryTable.student_table_schema,
                          "s": TestQueryTable.student_table_schema})
        with self.assertRaises(RedefinedNameError):
            QueryTable("students", "s").type_check(st)


class TestQueryJoin(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })

    enrolled_table_schema = Schema({
        "ssn": BaseType.INT,
        "grade": BaseType.INT,
        "dropped": BaseType.BOOL,
    })

    student_enrolled_table_schema = Schema({
        "students.ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
        "enrolled.ssn": BaseType.INT,
        "grade": BaseType.INT,
        "dropped": BaseType.BOOL,
    })

    def test_join_table(self):
        st = SymbolTable({"students": TestQueryJoin.student_table_schema,
                          "enrolled": TestQueryJoin.enrolled_table_schema})
        self.assertEqual(QueryJoin(
            QueryTable("students"),
            QueryTable("enrolled"),
            BExprEquality(
                IExprColumn(("students", "ssn")),
                EqualityOperator.EQUALS,
                IExprColumn(("enrolled", "ssn"))
            ),
            "students_enrolled"
        ).type_check(st), ("students_enrolled", TestQueryJoin.student_enrolled_table_schema))

        self.assertEqual(QueryJoin(
            QueryTable("students"),
            QueryTable("enrolled"),
            BExprEquality(
                IExprColumn(("students", "gpa")),
                EqualityOperator.EQUALS,
                IExprColumn(("enrolled", "grade"))
            ),
            "students_enrolled"
        ).type_check(st), ("students_enrolled", TestQueryJoin.student_enrolled_table_schema))

    def test_self_join(self):
        st = SymbolTable({"students": TestQueryJoin.student_table_schema})
        self.assertEqual(QueryJoin(
            QueryTable("students", "s1"),
            QueryTable("students", "s2"),
            BExprEquality(
                IExprColumn(("s1", "ssn")),
                EqualityOperator.EQUALS,
                IExprColumn(("s2", "ssn"))
            ),
            "students_self_join"
        ).type_check(st), ("students_self_join", Schema({
            "s1.ssn": BaseType.INT,
            "s1.gpa": BaseType.INT,
            "s1.year": BaseType.INT,
            "s1.graduate": BaseType.BOOL,
            "s2.ssn": BaseType.INT,
            "s2.gpa": BaseType.INT,
            "s2.year": BaseType.INT,
            "s2.graduate": BaseType.BOOL,
        })))

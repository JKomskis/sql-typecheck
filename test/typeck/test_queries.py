import unittest
from src.parsing.bool_expr import BExprBoolLiteral, BExprColumn, BExprEquality, BExprNot, EqualityOperator
from src.parsing.data_structures import SExpr
from src.parsing.int_expr import BinaryIntOp, IExprBinaryOp, IExprColumn, IExprIntLiteral

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


class TestQuerySelect(unittest.TestCase):
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

    def test_select(self):
        st = SymbolTable({"students": TestQuerySelect.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students")
            ).type_check(st),
            ("students", Schema({
                "ssn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")), "mySsn")],
                QueryTable("students")
            ).type_check(st),
            ("students", Schema({
                "mySsn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn")],
                QueryTable("students", "myStudents")
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn"),
                 SExpr(ExprColumn(("myStudents", "graduate")))],
                QueryTable("students", "myStudents")
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn": BaseType.INT,
                "graduate": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("s", "ssn")), "mySsn"),
                 SExpr(BExprNot(BExprColumn(("s", "graduate"))))],
                QueryTable("students", "s")
            ).type_check(st),
            ("s", Schema({
                "mySsn": BaseType.INT,
                "not_graduate": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "graduate")), "g"),
                 SExpr(IExprIntLiteral(0)),
                 SExpr(IExprBinaryOp(
                     IExprIntLiteral(1),
                     BinaryIntOp.ADDITION,
                     IExprIntLiteral(2))),
                 SExpr(BExprBoolLiteral(True))],
                QueryTable("students")
            ).type_check(st),
            ("students", Schema({
                "g": BaseType.BOOL,
                "0": BaseType.INT,
                "1_plus_2": BaseType.INT,
                "true": BaseType.BOOL
            }))
        )

    def test_select_nested(self):
        st = SymbolTable({"students": TestQuerySelect.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "mySsn")), "mySsn2")],
                QuerySelect(
                    [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn"),
                     SExpr(ExprColumn(("myStudents", "graduate")))],
                    QueryTable("students", "myStudents")
                )
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn2": BaseType.INT
            }))
        )

    def test_query_join_select(self):
        st = SymbolTable({"students": TestQuerySelect.student_table_schema,
                          "enrolled": TestQuerySelect.enrolled_table_schema})
        self.assertEqual(
            QueryJoin(
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn"))),
                     SExpr(ExprColumn(("students", "graduate")))],
                    QueryTable("students"),
                ),
                QueryTable("enrolled"),
                BExprEquality(
                    IExprColumn(("students", "ssn")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "ssn"))
                ),
                "s_e"
            ).type_check(st), ("s_e", Schema({
                "students.ssn": BaseType.INT,
                "graduate": BaseType.BOOL,
                "enrolled.ssn": BaseType.INT,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QueryJoin(
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")), "ssn_2"),
                     SExpr(ExprColumn(("students", "graduate")))],
                    QueryTable("students"),
                ),
                QueryTable("enrolled"),
                BExprEquality(
                    IExprColumn(("students", "ssn_2")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "ssn"))
                ),
                "s_e"
            ).type_check(st), ("s_e", Schema({
                "ssn_2": BaseType.INT,
                "graduate": BaseType.BOOL,
                "ssn": BaseType.INT,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )

    def test_select_from_join(self):
        st = SymbolTable({"students": TestQuerySelect.student_table_schema,
                          "enrolled": TestQuerySelect.enrolled_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("s_e", "students.ssn"))),
                 SExpr(ExprColumn(("s_e", "grade")))],
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    BExprEquality(
                        IExprColumn(("students", "ssn")),
                        EqualityOperator.EQUALS,
                        IExprColumn(("enrolled", "ssn"))
                    ),
                    "s_e"
                )
            ).type_check(st), ("s_e", Schema({
                "students.ssn": BaseType.INT,
                "grade": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("s_e", "students.ssn")), "ssn"),
                 SExpr(ExprColumn(("s_e", "grade")))],
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    BExprEquality(
                        IExprColumn(("students", "ssn")),
                        EqualityOperator.EQUALS,
                        IExprColumn(("enrolled", "ssn"))
                    ),
                    "s_e"
                )
            ).type_check(st), ("s_e", Schema({
                "ssn": BaseType.INT,
                "grade": BaseType.INT
            }))
        )

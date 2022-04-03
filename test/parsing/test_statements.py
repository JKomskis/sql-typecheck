import unittest
from src.parsing.bool_expr import BExprColumn, BExprEquality, EqualityOperator
from src.parsing.int_expr import IExprColumn

from src.parsing.statements import StmtCreateTable, StmtQuery, StmtSequence, TableElement, stmt_create_table, stmt_sequence
from src.parsing.query import QueryJoin, QuerySelect, QueryTable
from src.parsing.expr import ExprColumn


class TestStmtCreate(unittest.TestCase):
    def test_stmt_create(self):
        self.assertEqual(
            stmt_sequence.parse(
                "CREATE TABLE students (ssn INT, gpa INT, year INT, graduate BOOL)"),
            StmtSequence([StmtCreateTable(
                "students",
                [
                    TableElement("ssn", "INT"),
                    TableElement("gpa", "INT"),
                    TableElement("year", "INT"),
                    TableElement("graduate", "BOOL"),
                ]
            )])
        )


class TestStmtQuery(unittest.TestCase):
    def test_stmt_query(self):
        self.assertEqual(
            stmt_sequence.parse(
                "students"),
            StmtSequence([StmtQuery(QueryTable("students"))])
        )
        self.assertEqual(
            stmt_sequence.parse(
                "SELECT students.ssn FROM students WHERE students.graduate"),
            StmtSequence([StmtQuery(QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprColumn(("students", "graduate"))
            ))])
        )
        self.assertEqual(
            stmt_sequence.parse(
                "students join enrolled ON students.id = enrolled.id AS s_e"),
            StmtSequence([StmtQuery(QueryJoin(
                QueryTable("students"),
                QueryTable("enrolled"),
                BExprEquality(
                    IExprColumn(("students", "id")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "id"))
                ),
                "s_e"
            ))])
        )


class TestStmtSequence(unittest.TestCase):
    def test_stmt_sequence(self):
        self.assertEqual(
            stmt_sequence.parse(
                """CREATE TABLE students (ssn INT, gpa INT, year INT, graduate BOOL);
                   SELECT students.ssn FROM students WHERE students.graduate"""),
            StmtSequence([
                StmtCreateTable(
                    "students",
                    [
                        TableElement("ssn", "INT"),
                        TableElement("gpa", "INT"),
                        TableElement("year", "INT"),
                        TableElement("graduate", "BOOL"),
                    ]
                ),
                StmtQuery(QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprColumn(("students", "graduate"))
                ))
            ])
        )
        self.assertEqual(
            stmt_sequence.parse(
                """CREATE TABLE students (id INT, gpa INT, year INT, graduate BOOL);
                   CREATE TABLE enrolled (id INT, grade INT, dropped BOOL);
                   students join enrolled ON students.id = enrolled.id AS s_e"""),
            StmtSequence([
                StmtCreateTable(
                    "students",
                    [
                        TableElement("id", "INT"),
                        TableElement("gpa", "INT"),
                        TableElement("year", "INT"),
                        TableElement("graduate", "BOOL"),
                    ]
                ),
                StmtCreateTable(
                    "enrolled",
                    [
                        TableElement("id", "INT"),
                        TableElement("grade", "INT"),
                        TableElement("dropped", "BOOL"),
                    ]
                ),
                StmtQuery(QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    BExprEquality(
                        IExprColumn(("students", "id")),
                        EqualityOperator.EQUALS,
                        IExprColumn(("enrolled", "id"))
                    ),
                    "s_e"
                ))
            ])
        )

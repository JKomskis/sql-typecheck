import unittest

from src.parsing.expr import (AggOp, BinaryOp, ExprAgg, ExprBinaryOp,
                              ExprColumn, ExprIntLiteral, ExprNot)
from src.parsing.query import QuerySelect, QueryTable, query
from src.parsing.s_expr import SExpr


class TestQueryGroupBy(unittest.TestCase):
    def test_query_groupby(self):
        self.assertEqual(
            query.parse(
                "SELECT students.gpa FROM students GROUP BY students.gpa"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "gpa")))],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.gpa, NOT students.graduate FROM students GROUP BY students.gpa, not students.graduate"),
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprNot(ExprColumn(("students", "graduate"))))],
                QueryTable("students"),
                None,
                [
                    ExprColumn(("students", "gpa")),
                    ExprNot(ExprColumn(("students", "graduate")))
                ]
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.gpa FROM students WHERE students.graduate GROUP BY students.gpa"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "gpa")))],
                QueryTable("students"),
                ExprColumn(("students", "graduate")),
                [ExprColumn(("students", "gpa"))]
            )
        )

    def test_query_aggregation(self):
        self.assertEqual(
            query.parse(
                "SELECT MIN(students.year), AVG(students.year) + -4 FROM students GROUP BY students.gpa"),
            QuerySelect(
                [
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(("students", "year")))),
                    SExpr(ExprBinaryOp(
                        ExprAgg(AggOp.AVG, ExprColumn(("students", "year"))),
                        BinaryOp.ADDITION,
                        ExprIntLiteral(-4)))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.year, COUNT(students.ssn) FROM students GROUP BY students.year, not students.graduate"),
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "year"))),
                    SExpr(ExprAgg(AggOp.COUNT, ExprColumn(("students", "ssn"))))],
                QueryTable("students"),
                None,
                [
                    ExprColumn(("students", "year")),
                    ExprNot(ExprColumn(("students", "graduate")))
                ]
            )
        )


class TestQueryHaving(unittest.TestCase):
    def test_query_having(self):
        self.assertEqual(
            query.parse(
                "SELECT students.gpa\
                 FROM students\
                 GROUP BY students.gpa\
                 HAVING students.gpa < 3"),
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))],
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                )
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.gpa, MIN(students.year)\
                 FROM students\
                 GROUP BY students.gpa\
                 HAVING students.gpa < 3 AND MIN(students.year) < 2015"),
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(("students", "year"))))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))],
                ExprBinaryOp(
                    ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.LESS_THAN,
                        ExprIntLiteral(3)
                    ),
                    BinaryOp.AND,
                    ExprBinaryOp(
                        ExprAgg(AggOp.MIN, ExprColumn(("students", "year"))),
                        BinaryOp.LESS_THAN,
                        ExprIntLiteral(2015)
                    )
                )
            )
        )



import unittest

from src.parsing.expr import (AggOp, BinaryOp, ExprAgg, ExprBinaryOp,
                              ExprColumn, ExprIntLiteral, ExprNot)
from src.parsing.query import QuerySelect, QueryTable
from src.parsing.s_expr import SExpr
from src.types.symbol_table import SymbolTable
from src.types.types import AggregationMismatchError, BaseType, Schema, TypeMismatchError


class TestQueryGroupBy(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
        "name": BaseType.VARCHAR
    })

    def test_query_groupby(self):
        st = SymbolTable({"students": TestQueryGroupBy.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "gpa")))],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [SExpr(ExprColumn(("students", "gpa")))],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "no_such_field"))]
            ).type_check(st)
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprColumn(("students", "name")))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)

        self.assertEqual(
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
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT,
                "not_graduate": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprNot(ExprColumn(("students", "graduate"))))],
                QueryTable("students"),
                None,
                [
                    ExprColumn(("students", "gpa")),
                    ExprColumn(("students", "graduate"))
                ]
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT,
                "not_graduate": BaseType.BOOL
            }))
        )
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprColumn(("students", "graduate")))],
                QueryTable("students"),
                None,
                [
                    ExprColumn(("students", "gpa")),
                    ExprNot(ExprColumn(("students", "graduate")))
                ]
            ).type_check(st)

    def test_query_aggregation(self):
        st = SymbolTable({"students": TestQueryGroupBy.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(("students", "year")))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT,
                "min_year": BaseType.INT
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(
                        ("students", "no_such_field")))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)
        with self.assertRaises(TypeMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(
                        ("students", "graduate")))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)
        with self.assertRaises(TypeMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.AVG, ExprColumn(
                        ("students", "graduate")))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)
        with self.assertRaises(TypeMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprAgg(AggOp.AVG, ExprColumn(
                        ("students", "name")))),
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)

        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprBinaryOp(
                        ExprAgg(AggOp.AVG, ExprColumn(("students", "year"))),
                        BinaryOp.ADDITION,
                        ExprIntLiteral(-4)), "avg_start_year"),
                    SExpr(ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.MULTIPLICATION,
                        ExprAgg(AggOp.MIN, ExprColumn(("students", "year")))
                    ))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT,
                "avg_start_year": BaseType.INT,
                "gpa_times_min_year": BaseType.INT
            }))
        )
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprAgg(AggOp.MIN, ExprColumn(("students", "gpa"))))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprAgg(AggOp.AVG,
                                  ExprAgg(AggOp.MIN, ExprColumn(("students", "year")))))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)
        with self.assertRaises(TypeMismatchError):
            QuerySelect(
                [
                    SExpr(ExprNot(ExprAgg(AggOp.MIN, ExprColumn(("students", "year")))))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))]
            ).type_check(st)

        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                    SExpr(ExprColumn(("students", "year"))),
                    SExpr(ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.LESS_THAN,
                        ExprColumn(("students", "year")))),
                    SExpr(ExprAgg(AggOp.MAX, ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.ADDITION,
                        ExprColumn(("students", "ssn"))
                    )))
                ],
                QueryTable("students"),
                None,
                [
                    ExprColumn(("students", "gpa")),
                    ExprColumn(("students", "year"))]
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT,
                "year": BaseType.INT,
                "gpa_lessthan_year": BaseType.BOOL,
                "max_gpa_plus_ssn": BaseType.INT
            }))
        )


class TestQueryHaving(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
        "name": BaseType.VARCHAR
    })

    def test_query_having(self):
        st = SymbolTable({"students": TestQueryHaving.student_table_schema})
        self.assertEqual(
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
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
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
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [SExpr(ExprColumn(("students", "gpa")))],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))],
                ExprColumn(("students", "no_such_field"))
            ).type_check(st)
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa")))
                ],
                QueryTable("students"),
                None,
                [ExprColumn(("students", "gpa"))],
                ExprColumn(("students", "graduate"))
            ).type_check(st)

    def test_query_where_having(self):
        st = SymbolTable({"students": TestQueryHaving.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                ],
                QueryTable("students"),
                ExprColumn(("students", "graduate")),
                [ExprColumn(("students", "gpa"))],
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                )
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                ],
                QueryTable("students"),
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                ),
                [ExprColumn(("students", "gpa"))],
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                )
            ).type_check(st),
            ("students", Schema({
                "gpa": BaseType.INT
            }))
        )
        with self.assertRaises(AggregationMismatchError):
            QuerySelect(
                [
                    SExpr(ExprColumn(("students", "gpa"))),
                ],
                QueryTable("students"),
                ExprBinaryOp(
                    ExprAgg(AggOp.MIN, ExprColumn(("students", "year"))),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(2015)
                ),
                [ExprColumn(("students", "gpa"))],
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                )
            ).type_check(st)

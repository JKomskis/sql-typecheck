import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprBoolLiteral,
                              ExprColumn, ExprIntLiteral, ExprNot)
from src.parsing.query import QueryJoin, QuerySelect, QueryTable, QueryUnion, QueryIntersect
from src.parsing.s_expr import SExpr
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, RedefinedNameError, Schema, TypeMismatchError


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
            ExprBinaryOp(
                ExprColumn(("students", "ssn")),
                BinaryOp.EQUALS,
                ExprColumn(("enrolled", "ssn"))
            ),
            "students_enrolled"
        ).type_check(st), ("students_enrolled", TestQueryJoin.student_enrolled_table_schema))

        self.assertEqual(QueryJoin(
            QueryTable("students"),
            QueryTable("enrolled"),
            ExprBinaryOp(
                ExprColumn(("students", "gpa")),
                BinaryOp.EQUALS,
                ExprColumn(("enrolled", "grade"))
            ),
            "students_enrolled"
        ).type_check(st), ("students_enrolled", TestQueryJoin.student_enrolled_table_schema))

    def test_self_join(self):
        st = SymbolTable({"students": TestQueryJoin.student_table_schema})
        self.assertEqual(QueryJoin(
            QueryTable("students", "s1"),
            QueryTable("students", "s2"),
            ExprBinaryOp(
                ExprColumn(("s1", "ssn")),
                BinaryOp.EQUALS,
                ExprColumn(("s2", "ssn"))
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
                 SExpr(ExprNot(ExprColumn(("s", "graduate"))))],
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
                 SExpr(ExprIntLiteral(0)),
                 SExpr(ExprBinaryOp(
                     ExprIntLiteral(1),
                     BinaryOp.ADDITION,
                     ExprIntLiteral(2))),
                 SExpr(ExprBoolLiteral(True))],
                QueryTable("students")
            ).type_check(st),
            ("students", Schema({
                "g": BaseType.BOOL,
                "0": BaseType.INT,
                "1_plus_2": BaseType.INT,
                "true": BaseType.BOOL
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [SExpr(ExprColumn(("students", "nofield")))],
                QueryTable("students")
            ).type_check(st)

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
                ExprBinaryOp(
                    ExprColumn(("students", "ssn")),
                    BinaryOp.EQUALS,
                    ExprColumn(("enrolled", "ssn"))
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
                ExprBinaryOp(
                    ExprColumn(("students", "ssn_2")),
                    BinaryOp.EQUALS,
                    ExprColumn(("enrolled", "ssn"))
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
                    ExprBinaryOp(
                        ExprColumn(("students", "ssn")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "ssn"))
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
                    ExprBinaryOp(
                        ExprColumn(("students", "ssn")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "ssn"))
                    ),
                    "s_e"
                )
            ).type_check(st), ("s_e", Schema({
                "ssn": BaseType.INT,
                "grade": BaseType.INT
            }))
        )


class TestQuerySelectWhere(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })

    def test_select(self):
        st = SymbolTable(
            {"students": TestQuerySelectWhere.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students"),
                ExprBoolLiteral(True)
            ).type_check(st),
            ("students", Schema({
                "ssn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")), "mySsn")],
                QueryTable("students"),
                ExprBinaryOp(
                    ExprColumn(("students", "gpa")),
                    BinaryOp.LESS_THAN,
                    ExprIntLiteral(3)
                )
            ).type_check(st),
            ("students", Schema({
                "mySsn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn")],
                QueryTable("students", "myStudents"),
                ExprBinaryOp(
                    ExprColumn(("myStudents", "mySsn")),
                    BinaryOp.EQUALS,
                    ExprColumn(("myStudents", "gpa"))
                )
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn": BaseType.INT
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn"),
                 SExpr(ExprColumn(("myStudents", "graduate")))],
                QueryTable("students", "myStudents"),
                ExprBinaryOp(
                    ExprColumn(("myStudents", "graduate")),
                    BinaryOp.AND,
                    ExprBinaryOp(
                        ExprColumn(("myStudents", "ssn")),
                        BinaryOp.LESS_THAN,
                        ExprIntLiteral(1000000)
                    )
                )
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn": BaseType.INT,
                "graduate": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("s", "ssn")), "mySsn"),
                 SExpr(ExprNot(ExprColumn(("s", "graduate"))))],
                QueryTable("students", "s"),
                ExprBinaryOp(
                    ExprColumn(("s", "graduate")),
                    BinaryOp.AND,
                    ExprColumn(("s", "not_graduate"))
                )
            ).type_check(st),
            ("s", Schema({
                "mySsn": BaseType.INT,
                "not_graduate": BaseType.BOOL
            }))
        )
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("students", "graduate")), "g"),
                 SExpr(ExprIntLiteral(0)),
                 SExpr(ExprBinaryOp(
                     ExprIntLiteral(1),
                     BinaryOp.ADDITION,
                     ExprIntLiteral(2))),
                 SExpr(ExprBoolLiteral(True))],
                QueryTable("students"),
                ExprBinaryOp(
                    ExprColumn(("students", "0")),
                    BinaryOp.LESS_THAN,
                    ExprColumn(("students", "1_plus_2"))
                )
            ).type_check(st),
            ("students", Schema({
                "g": BaseType.BOOL,
                "0": BaseType.INT,
                "1_plus_2": BaseType.INT,
                "true": BaseType.BOOL
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [SExpr(ExprColumn(("students", "nofield")))],
                QueryTable("students"),
                ExprColumn(("ssn", "graduate"))
            ).type_check(st)

    def test_select_nested(self):
        st = SymbolTable(
            {"students": TestQuerySelectWhere.student_table_schema})
        self.assertEqual(
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "mySsn")), "mySsn2")],
                QuerySelect(
                    [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn"),
                     SExpr(ExprColumn(("myStudents", "graduate")))],
                    QueryTable("students", "myStudents"),
                    ExprBinaryOp(
                        ExprColumn(("myStudents", "mySsn")),
                        BinaryOp.LESS_THAN,
                        ExprColumn(("myStudents", "gpa")),
                    )
                ),
                ExprColumn(("myStudents", "graduate"))
            ).type_check(st),
            ("myStudents", Schema({
                "mySsn2": BaseType.INT
            }))
        )
        with self.assertRaises(KeyError):
            QuerySelect(
                [SExpr(ExprColumn(("myStudents", "mySsn")), "mySsn2")],
                QuerySelect(
                    [SExpr(ExprColumn(("myStudents", "ssn")), "mySsn"),
                     SExpr(ExprColumn(("myStudents", "graduate")))],
                    QueryTable("students", "myStudents"),
                    ExprBinaryOp(
                        ExprColumn(("myStudents", "gpa")),
                        BinaryOp.LESS_THAN,
                        ExprIntLiteral(3)
                    )
                ),
                ExprColumn(("myStudents", "gpa"))
            ).type_check(st)


class TestQueryUnion(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "grade": BaseType.INT,
        "graduate": BaseType.BOOL,
        "undergraduate": BaseType.BOOL
    })

    student_wrong_schema = Schema({
        "ssn": BaseType.BOOL,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL,
    })

    def test_table_union(self):
        st = SymbolTable(
            {"students": TestQueryUnion.student_table_schema,
             "students_2": TestQueryUnion.student_table_schema})

        st_nomatch = SymbolTable(
            {"students": TestQueryUnion.student_table_schema,
             "students_2": TestQueryUnion.student_wrong_schema})

        self.assertEqual(QueryUnion([
            QueryTable("students"),
            QueryTable("students_2")
        ]).type_check(st),
            ("ss_s2", Schema.merge_fields(
                TestQueryUnion.student_table_schema,
                TestQueryUnion.student_table_schema)
             )
        )

        with self.assertRaises(TypeMismatchError):
            QueryUnion([
                QueryTable("students"),
                QueryTable("students_2")
            ]).type_check(st_nomatch)

    def test_select_union(self):
        st = SymbolTable(
            {"students": TestQueryUnion.student_table_schema})

        self.assertEqual(QueryUnion([
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students"),
                ExprColumn(("students", "graduate"))
            ),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students"),
                ExprColumn(("students", "undergraduate"))
            )
        ]).type_check(st),

            ("ss_ss", Schema({
                "ssn_ssn": BaseType.INT
            }))
        )

    def test_join_union(self):
        st = SymbolTable(
            {"students": TestQueryUnion.student_table_schema,
             "enrolled": TestQueryUnion.student_table_schema})

        self.assertEqual(
            QueryUnion([
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    ExprBinaryOp(
                        ExprColumn(("students", "ssn")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "ssn"))
                    ),
                    "s_e"
                ),
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "grade"))
                    ),
                    "s_e2"
                )
            ]).type_check(st),

            ("se_s2", Schema({
                "students.ssn_students.ssn": BaseType.INT,
                "students.gpa_students.gpa": BaseType.INT,
                "students.year_students.year": BaseType.INT,
                "students.grade_students.grade": BaseType.INT,
                "students.graduate_students.graduate": BaseType.BOOL,
                "students.undergraduate_students.undergraduate": BaseType.BOOL,
                "enrolled.ssn_enrolled.ssn": BaseType.INT,
                "enrolled.gpa_enrolled.gpa": BaseType.INT,
                "enrolled.year_enrolled.year": BaseType.INT,
                "enrolled.grade_enrolled.grade": BaseType.INT,
                "enrolled.graduate_enrolled.graduate": BaseType.BOOL,
                "enrolled.undergraduate_enrolled.undergraduate": BaseType.BOOL
            })
            ))

    def test_mixed_union(self):
        st = SymbolTable(
            {"students": TestQueryUnion.student_table_schema})
        with self.assertRaises(TypeMismatchError):
            QueryUnion([
                QueryTable("students"),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                )
            ]).type_check(st)
        # the above should not type check because each side of the union
        # does not have the same amount of cols


class TestQueryIntersect(unittest.TestCase):
    student_table_schema = Schema({
        "ssn": BaseType.INT,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "grade": BaseType.INT,
        "graduate": BaseType.BOOL,
        "undergraduate": BaseType.BOOL,
    })

    student_wrong_schema = Schema({
        "ssn": BaseType.BOOL,
        "gpa": BaseType.INT,
        "year": BaseType.INT,
        "graduate": BaseType.BOOL
    })

    def test_table_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema,
             "students_2": TestQueryIntersect.student_table_schema})

        st_nomatch = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema,
             "students_2": TestQueryIntersect.student_wrong_schema})

        self.assertEqual(QueryIntersect([
            QueryTable("students"),
            QueryTable("students_2")
        ]).type_check(st),
            ("ss_s2", Schema.merge_fields(TestQueryIntersect.student_table_schema,
                                          TestQueryIntersect.student_table_schema))
        )

        with self.assertRaises(TypeMismatchError):
            QueryIntersect([
                QueryTable("students"),
                QueryTable("students_2")
            ]).type_check(st_nomatch),

    def test_select_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema})

        self.assertEqual(
            QueryIntersect([
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                ),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "undergraduate"))
                )
            ]).type_check(st),
            ("ss_ss", Schema({
                "ssn_ssn": BaseType.INT
            }))
        )

    def test_join_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema,
             "enrolled": TestQueryIntersect.student_table_schema})
        self.assertEqual(
            QueryIntersect([
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    ExprBinaryOp(
                        ExprColumn(("students", "ssn")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "ssn"))
                    ),
                    "s_e"
                ),
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "grade"))
                    ),
                    "s_e2"
                )
            ]).type_check(st),
            ("se_s2", Schema({
                "students.ssn_students.ssn": BaseType.INT,
                "students.gpa_students.gpa": BaseType.INT,
                "students.year_students.year": BaseType.INT,
                "students.grade_students.grade": BaseType.INT,
                "students.graduate_students.graduate": BaseType.BOOL,
                "students.undergraduate_students.undergraduate": BaseType.BOOL,
                "enrolled.ssn_enrolled.ssn": BaseType.INT,
                "enrolled.gpa_enrolled.gpa": BaseType.INT,
                "enrolled.year_enrolled.year": BaseType.INT,
                "enrolled.grade_enrolled.grade": BaseType.INT,
                "enrolled.graduate_enrolled.graduate": BaseType.BOOL,
                "enrolled.undergraduate_enrolled.undergraduate": BaseType.BOOL
            }))

        )

    def test_mixed_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema})

        with self.assertRaises(TypeMismatchError):
            QueryIntersect([
                QueryTable("students"),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                )
            ]).type_check(st)
        # the above should not type check because each side of the intersect
        # does not have the same amount of cols


class TestQueryIntersectUnion(unittest.TestCase):
    def test_table_union_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema,
             "students_2": TestQueryIntersect.student_table_schema,
             "students_3": TestQueryIntersect.student_table_schema})
        self.assertEqual(
            QueryUnion([
                QueryTable("students"),
                QueryIntersect([
                    QueryTable("students_2"),
                    QueryTable("students_3")
                ])
            ]).type_check(st),
            ("ss_s3", Schema.merge_fields(Schema.merge_fields(TestQueryIntersect.student_table_schema,
                                                              TestQueryIntersect.student_table_schema), TestQueryIntersect.student_table_schema))
        )

    def test_select_union_intersect(self):
        st = SymbolTable(
            {"students": TestQueryIntersect.student_table_schema})
        self.assertEqual(
            QueryUnion([
                QueryIntersect([
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "graduate"))
                    ),
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "undergraduate"))
                    )
                ]),
                QueryIntersect([
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "undergraduate"))
                    ),
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "graduate"))
                    )
                ])
            ]).type_check(st),
            ("ss_ss", Schema({
                "ssn_ssn_ssn_ssn": BaseType.INT
            }))

        )

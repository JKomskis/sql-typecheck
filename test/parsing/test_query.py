import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprBoolLiteral,
                              ExprColumn, ExprIntLiteral, ExprNot)
from src.parsing.query import (QueryIntersect, QueryJoin, QuerySelect,
                               QueryTable, QueryUnion, query)
from src.parsing.s_expr import SExpr


class TestQueryTable(unittest.TestCase):
    def test_query_table(self):
        self.assertEqual(query.parse("a"), QueryTable("a"))
        self.assertEqual(query.parse("a AS b"), QueryTable("a", "b"))


class TestQuerySelect(unittest.TestCase):
    def test_query_select(self):
        self.assertEqual(
            query.parse("SELECT students.ssn FROM students"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students")
            )
        )
        self.assertEqual(
            query.parse("SELECT students.ssn AS s FROM students"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")), "s")],
                QueryTable("students")
            )
        )
        self.assertEqual(
            query.parse("SELECT students.ssn, students.year FROM students"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn"))),
                 SExpr(ExprColumn(("students", "year")))],
                QueryTable("students")
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn AS s, students.year AS y FROM students"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")), "s"),
                 SExpr(ExprColumn(("students", "year")), "y")],
                QueryTable("students")
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.graduate AS g, 0,1+2, true FROM students"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "graduate")), "g"),
                 SExpr(ExprIntLiteral(0)),
                 SExpr(ExprBinaryOp(
                     ExprIntLiteral(1),
                     BinaryOp.ADDITION,
                     ExprIntLiteral(2))),
                 SExpr(ExprBoolLiteral(True))],
                QueryTable("students")
            )
        )

    def test_query_select_where(self):
        self.assertEqual(
            query.parse("SELECT students.ssn FROM students WHERE true"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn")))],
                QueryTable("students"),
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn, students.year FROM students WHERE students.ssn = students.year"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "ssn"))),
                 SExpr(ExprColumn(("students", "year")))],
                QueryTable("students"),
                ExprBinaryOp(
                    ExprColumn(("students", "ssn")),
                    BinaryOp.EQUALS,
                    ExprColumn(("students", "year"))
                )
            )
        )

    def test_query_select_nested(self):
        self.assertEqual(
            query.parse(
                "SELECT s.ssn FROM SELECT s.ssn, s.gpa FROM students AS s"),
            QuerySelect(
                [SExpr(ExprColumn(("s", "ssn")))],
                QuerySelect(
                    [SExpr(ExprColumn(("s", "ssn"))),
                     SExpr(ExprColumn(("s", "gpa")))],
                    QueryTable("students", "s"),

                )
            )
        )


class TestQueryUnion(unittest.TestCase):
    def test_table_union(self):
        self.assertEqual(
            query.parse("students UNION students_2"),
            QueryUnion([
                QueryTable("students"),
                QueryTable("students_2")
            ])
        )
        self.assertEqual(
            query.parse("students UNION students_2 UNION students_3"),
            QueryUnion([
                QueryTable("students"),
                QueryTable("students_2"),
                QueryTable("students_3")
            ])
        )

    def test_select_union(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    UNION SELECT students.ssn FROM students WHERE students.undergraduate"),
            QueryUnion([
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
            ])
        )

    def test_join_union(self):
        self.assertEqual(
            query.parse(
                "students join enrolled on students.ssn = enrolled.ssn as s_e\
                    UNION students join enrolled on students.gpa = enrolled.grade as s_e2"),
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
            ])
        )

    def test_mixed_union(self):
        self.assertEqual(
            query.parse("students UNION\
                SELECT students.ssn FROM students WHERE students.graduate"),
            QueryUnion([
                QueryTable("students"),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                )
            ])
        )


class TestQueryIntersect(unittest.TestCase):
    def test_table_intersect(self):
        self.assertEqual(
            query.parse("students INTERSECT students_2"),
            QueryIntersect([
                QueryTable("students"),
                QueryTable("students_2")
            ])
        )
        self.assertEqual(
            query.parse("students INTERSECT students_2 INTERSECT students_3"),
            QueryIntersect([
                QueryTable("students"),
                QueryTable("students_2"),
                QueryTable("students_3")
            ])
        )

    def test_select_intersect(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    INTERSECT SELECT students.ssn FROM students WHERE students.undergraduate"),
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
            ])
        )

    def test_join_intersect(self):
        self.assertEqual(
            query.parse(
                "students join enrolled on students.ssn = enrolled.ssn as s_e\
                    INTERSECT students join enrolled on students.gpa = enrolled.grade as s_e2"),
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
            ])
        )

    def test_mixed_intersect(self):
        self.assertEqual(
            query.parse("students INTERSECT\
                SELECT students.ssn FROM students WHERE students.graduate"),
            QueryIntersect([
                QueryTable("students"),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                )
            ])
        )


class TestQueryIntersectUnion(unittest.TestCase):
    def test_table_union_intersect(self):
        self.assertEqual(
            query.parse("students union students_2 intersect students_3"),
            QueryUnion([
                QueryTable("students"),
                QueryIntersect([
                    QueryTable("students_2"),
                    QueryTable("students_3")
                ])
            ])
        )

    def test_select_union_intersect(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    INTERSECT SELECT students.ssn FROM students WHERE students.undergraduate\
                    UNION \
                    SELECT students.ssn FROM students WHERE students.enrolled\
                    INTERSECT SELECT students.ssn FROM students WHERE students.graduate"),
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
                        ExprColumn(("students", "enrolled"))
                    ),
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "graduate"))
                    )
                ])
            ])
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                INTERSECT (SELECT students.ssn FROM students WHERE students.undergraduate\
                UNION \
                SELECT students.ssn FROM students WHERE students.enrolled)\
                INTERSECT SELECT students.ssn FROM students WHERE students.graduate"),
            QueryIntersect([
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                ),
                QueryUnion([
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "undergraduate"))
                    ),
                    QuerySelect(
                        [SExpr(ExprColumn(("students", "ssn")))],
                        QueryTable("students"),
                        ExprColumn(("students", "enrolled"))
                    ),
                ]),
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprColumn(("students", "graduate"))
                )
            ])
        )


class TestQueryJoin(unittest.TestCase):
    def test_query_join(self):
        self.assertEqual(
            query.parse(
                "students join enrolled ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QueryTable("students"),
                QueryTable("enrolled"),
                ExprBinaryOp(
                    ExprColumn(("students", "id")),
                    BinaryOp.EQUALS,
                    ExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )

    def test_query_join_select(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.gpa < 3 join enrolled ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QuerySelect(
                    [SExpr(ExprColumn(("students", "ssn")))],
                    QueryTable("students"),
                    ExprBinaryOp(
                        ExprColumn(("students", "gpa")),
                        BinaryOp.LESS_THAN,
                        ExprIntLiteral(3)
                    )
                ),
                QueryTable("enrolled"),
                ExprBinaryOp(
                    ExprColumn(("students", "id")),
                    BinaryOp.EQUALS,
                    ExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.gpa < 3 join enrolled ON students.id = enrolled.id AS s_e"),
            query.parse(
                "(SELECT students.ssn FROM students WHERE students.gpa < 3) join enrolled ON students.id = enrolled.id AS s_e"),
        )
        self.assertEqual(
            query.parse(
                "students join SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QueryTable("students"),
                QuerySelect(
                    [SExpr(ExprColumn(("enrolled", "id")))],
                    QueryTable("enrolled"),
                    ExprNot(
                        ExprColumn(("enrolled", "dropped"))
                    )
                ),
                ExprBinaryOp(
                    ExprColumn(("students", "id")),
                    BinaryOp.EQUALS,
                    ExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )
        self.assertEqual(
            query.parse(
                "students join SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped ON students.id = enrolled.id AS s_e"),
            query.parse(
                "students join (SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped) ON students.id = enrolled.id AS s_e"),
        )

    def test_select_from_join(self):
        self.assertEqual(
            query.parse(
                "SELECT students.id, enrolled.grade FROM students join enrolled ON students.id = enrolled.id AS s_e WHERE students.graduate"),
            QuerySelect(
                [SExpr(ExprColumn(("students", "id"))),
                 SExpr(ExprColumn(("enrolled", "grade")))],
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    ExprBinaryOp(
                        ExprColumn(("students", "id")),
                        BinaryOp.EQUALS,
                        ExprColumn(("enrolled", "id"))
                    ),
                    "s_e"
                ),
                ExprColumn(("students", "graduate"))
            )
        )

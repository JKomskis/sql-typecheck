import unittest
from test.e2e.tables import (course_create_table_statement,
                             enrolled_create_table_statement,
                             student_create_table_statement)

from src.parsing.statements import stmt_sequence
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema


class TestNestedSelect(unittest.TestCase):
    def test_nested_select(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, CONCAT(s.name, "!"), s.year + -4 AS start_year, not s.graduate as undergraduate
                    FROM SELECT s.student_id, s.name, s.year, s.graduate
                        FROM student as s"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR,
                "start_year": BaseType.INT,
                "undergraduate": BaseType.BOOL
            }))
        )


class TestSelectFromJoin(unittest.TestCase):
    def test_select_from_join(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s_e.student.student_id as s_id, s_e.course_id, s_e.grade
                    FROM student JOIN enrolled ON student.student_id = enrolled.student_id AS s_e"""
            ).type_check(SymbolTable()),
            ("s_e", Schema({
                "s_id": BaseType.INT,
                "course_id": BaseType.INT,
                "grade": BaseType.INT
            }))
        )


class TestJoinFromSelect(unittest.TestCase):
    def test_join_from_select(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    (SELECT c.course_id, c.name FROM course AS c)
                    JOIN
                    (SELECT e.course_id, e.grade from enrolled AS e)
                    ON c.course_id = e.course_id as c_e"""
            ).type_check(SymbolTable()),
            ("c_e", Schema({
                "c.course_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "e.course_id": BaseType.INT,
                "grade": BaseType.INT
            }))
        )


class TestGroupByJoin(unittest.TestCase):
    def test_group_by_join(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT c_e.course.course_id as course_id, COUNT(c_e.student_id)
                    FROM (course JOIN enrolled on course.course_id = enrolled.course_id as c_e)
                    WHERE 5000 < c_e.course.course_id
                    GROUP BY c_e.course.course_id, c_e.capacity
                    HAVING COUNT(c_e.student_id) < (c_e.capacity + -10)"""
            ).type_check(SymbolTable()),
            ("c_e", Schema({
                "course_id": BaseType.INT,
                "count_student_id": BaseType.INT
            }))
        )

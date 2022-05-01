import unittest

from src.parsing.statements import stmt_sequence
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema, TypeMismatchError
from test.e2e.tables import (student_create_table_statement,
                             enrolled_create_table_statement,
                             course_create_table_statement)


class TestQueryTable(unittest.TestCase):
    def test_query_table(self):
        st = SymbolTable()
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student"""
            ).type_check(st),
            ("student", Schema({
                "student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT
            }))
        )

        st = SymbolTable()
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    course AS c"""
            ).type_check(st),
            ("c", Schema({
                "course_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "capacity": BaseType.INT,
                "instructor": BaseType.VARCHAR
            }))
        )


class TestQuerySelect(unittest.TestCase):
    def test_query_select(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, CONCAT(s.name, "!"), s.year + 4 AS start_year, not s.graduate as undergraduate
                    FROM student AS s"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR,
                "start_year": BaseType.INT,
                "undergraduate": BaseType.BOOL
            }))
        )

        with self.assertRaises(KeyError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        SELECT s.student_id, s.no_such_field
                        FROM student AS s"""
            ).type_check(SymbolTable())


class TestQuerySelectWhere(unittest.TestCase):
    def test_query_select_where(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        SELECT s.student_id, CONCAT(s.name, "!"), s.year + 4 AS start_year, not s.graduate as undergraduate
                        FROM student AS s
                        WHERE s.alumni = True"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR,
                "start_year": BaseType.INT,
                "undergraduate": BaseType.BOOL
            }))
        )

        with self.assertRaises(KeyError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        SELECT s.student_id, s.no_such_field
                        FROM student AS s
                        WHERE s.alumni = True"""
            ).type_check(SymbolTable())

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        SELECT s.student_id, CONCAT(s.name, "!"), s.year + 4 AS start_year, not s.graduate as undergraduate
                        FROM student AS s
                        WHERE s.gpa"""
            ).type_check(SymbolTable())


class TestJoin2(unittest.TestCase):
    def test_join_2(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        student JOIN enrolled ON student.student_id = enrolled.student_id AS s_e"""
            ).type_check(SymbolTable()),
            ("s_e", Schema({
                "student.student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "enrolled.student_id": BaseType.INT,
                "course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )

        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        student AS s JOIN enrolled AS e ON e.grade < s.gpa AS s_e"""
            ).type_check(SymbolTable()),
            ("s_e", Schema({
                "s.student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "e.student_id": BaseType.INT,
                "course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                            {enrolled_create_table_statement}
                            {course_create_table_statement}
                            student AS s JOIN enrolled AS e ON s.gpa AS s_e"""
            ).type_check(SymbolTable())


class TestJoin3(unittest.TestCase):
    def test_join_3(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        student JOIN enrolled ON student.student_id = enrolled.student_id AS s_e
                            JOIN course ON s_e.course_id = course.course_id as s_e_c"""
            ).type_check(SymbolTable()),
            ("s_e_c", Schema({
                "student.student_id": BaseType.INT,
                "s_e.name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "enrolled.student_id": BaseType.INT,
                "s_e.course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL,
                "course.course_id": BaseType.INT,
                "course.name": BaseType.VARCHAR,
                "capacity": BaseType.INT,
                "instructor": BaseType.VARCHAR
            }))
        )

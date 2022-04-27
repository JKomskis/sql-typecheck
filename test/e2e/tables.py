student_create_table_statement = \
    """CREATE TABLE student (
    student_id INT,
    name VARCHAR,
    year INT,
    graduate BOOL,
    alumni BOOL,
    gpa INT
);"""

enrolled_create_table_statement = \
    """CREATE TABLE enrolled (
    student_id INT,
    course_id INT,
    semester VARCHAR,
    grade INT,
    dropped BOOL
);"""

course_create_table_statement = \
    """CREATE TABLE course (
    course_id INT,
    name VARCHAR,
    capacity INT,
    instructor VARCHAR
);"""

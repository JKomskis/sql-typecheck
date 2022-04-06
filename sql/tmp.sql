CREATE TABLE students (ssn INT, gpa INT, year INT, graduate BOOL);
SELECT students.ssn FROM students WHERE students.gpa < 3
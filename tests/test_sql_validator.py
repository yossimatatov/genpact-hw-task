from tools.validator import validate_sql_against_database, validate_sql_safety


def test_validate_sql_safety_accepts_select():
    is_valid, error = validate_sql_safety("SELECT * FROM students")

    assert is_valid is True
    assert error == ""


def test_validate_sql_safety_accepts_cte():
    is_valid, error = validate_sql_safety(
        """
        WITH student_count AS (
            SELECT COUNT(*) AS count
            FROM students
        )
        SELECT count FROM student_count
        """
    )

    assert is_valid is True
    assert error == ""


def test_validate_sql_safety_rejects_mutation():
    is_valid, error = validate_sql_safety("DELETE FROM students")

    assert is_valid is False
    assert "Only SELECT or WITH" in error


def test_validate_sql_safety_rejects_multiple_statements():
    is_valid, error = validate_sql_safety("SELECT * FROM students; DROP TABLE students")

    assert is_valid is False
    assert "Multiple SQL statements" in error


def test_validate_sql_against_database_accepts_valid_join(seeded_db):
    query = """
        SELECT s.first_name, c.course_name
        FROM students s
        JOIN enrollments e ON e.student_id = s.student_id
        JOIN course_offerings co ON co.offering_id = e.offering_id
        JOIN courses c ON c.course_id = co.course_id
    """

    is_valid, error = validate_sql_against_database(query)

    assert is_valid is True
    assert error == ""


def test_validate_sql_against_database_rejects_unknown_column(seeded_db):
    is_valid, error = validate_sql_against_database("SELECT missing_column FROM students")

    assert is_valid is False
    assert "SQL does not match" in error

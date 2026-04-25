import pytest

from tools.schema import expand_tables_with_relationships
from tools.sql import execute_read_query


def test_seeded_database_has_expected_counts(seeded_db):
    expected_counts = {
        "students": 20,
        "teachers": 8,
        "courses": 12,
        "course_offerings": 16,
        "enrollments": 68,
        "grades": 68,
    }

    for table_name, expected_count in expected_counts.items():
        rows = execute_read_query(f"SELECT COUNT(*) AS count FROM {table_name}")

        assert rows[0]["count"] == expected_count


def test_average_grade_for_database_systems(seeded_db):
    rows = execute_read_query(
        """
        SELECT AVG(g.points) AS average_grade
        FROM grades g
        JOIN enrollments e ON e.enrollment_id = g.enrollment_id
        JOIN course_offerings co ON co.offering_id = e.offering_id
        JOIN courses c ON c.course_id = co.course_id
        WHERE c.course_name = 'Database Systems'
        """
    )

    assert rows[0]["average_grade"] == pytest.approx(80.0)


def test_teacher_course_join_for_rachel_cohen(seeded_db):
    rows = execute_read_query(
        """
        SELECT DISTINCT c.course_name
        FROM teachers t
        JOIN course_offerings co ON co.teacher_id = t.teacher_id
        JOIN courses c ON c.course_id = co.course_id
        WHERE t.first_name = 'Rachel'
          AND t.last_name = 'Cohen'
        """
    )

    assert {row["course_name"] for row in rows} == {
        "Introduction to Programming",
        "Database Systems",
    }


def test_schema_expands_bridge_tables_for_join_path(seeded_db):
    expanded_tables = expand_tables_with_relationships(["students", "courses"])

    assert "students" in expanded_tables
    assert "courses" in expanded_tables
    assert "enrollments" in expanded_tables
    assert "course_offerings" in expanded_tables

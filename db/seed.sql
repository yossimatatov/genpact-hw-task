PRAGMA foreign_keys = ON;

INSERT INTO student_groups (group_id, group_name) VALUES
    (1, 'CS-101'),
    (2, 'DS-201'),
    (3, 'BA-301');

INSERT INTO students (student_id, first_name, last_name, sex, group_id) VALUES
    (1, 'Anna', 'Petrova', 'F', 1),
    (2, 'Ivan', 'Sokolov', 'M', 1),
    (3, 'Maria', 'Levin', 'F', 2),
    (4, 'David', 'Cohen', 'M', 2),
    (5, 'Olga', 'Morozova', 'F', 3);

INSERT INTO teachers (teacher_id, first_name, last_name, sex) VALUES
    (1, 'Elena', 'Smirnova', 'F'),
    (2, 'Michael', 'Brown', 'M'),
    (3, 'Nina', 'Katz', 'F');

INSERT INTO courses (course_id, course_code, course_name, is_elective) VALUES
    (1, 'CS101', 'Introduction to Programming', 0),
    (2, 'DB201', 'Database Systems', 0),
    (3, 'ML301', 'Machine Learning', 1),
    (4, 'STAT210', 'Statistics', 0);

INSERT INTO course_offerings (offering_id, course_id, teacher_id, semester, academic_year) VALUES
    (1, 1, 1, 'Fall', 2025),
    (2, 2, 2, 'Fall', 2025),
    (3, 3, 3, 'Spring', 2026),
    (4, 4, 2, 'Spring', 2026),
    (5, 2, 1, 'Spring', 2026);

INSERT INTO enrollments (enrollment_id, student_id, offering_id, passed) VALUES
    (1, 1, 1, 1),
    (2, 2, 1, 1),
    (3, 3, 2, 1),
    (4, 4, 2, 0),
    (5, 1, 3, 1),
    (6, 3, 3, 1),
    (7, 5, 4, 1),
    (8, 2, 5, 1),
    (9, 4, 5, 1);

INSERT INTO grades (grade_id, enrollment_id, points) VALUES
    (1, 1, 92.0),
    (2, 2, 81.5),
    (3, 3, 88.0),
    (4, 4, 58.0),
    (5, 5, 95.0),
    (6, 6, 90.0),
    (7, 7, 84.0),
    (8, 8, 76.0),
    (9, 9, 82.0);

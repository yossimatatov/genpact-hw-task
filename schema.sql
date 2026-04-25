PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS course_offerings;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS student_groups;

CREATE TABLE student_groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL UNIQUE
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('F', 'M')),
    group_id INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES student_groups(group_id)
);

CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('F', 'M'))
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY,
    course_code TEXT NOT NULL UNIQUE,
    course_name TEXT NOT NULL,
    is_elective INTEGER NOT NULL CHECK (is_elective IN (0, 1))
);

CREATE TABLE course_offerings (
    offering_id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    semester TEXT NOT NULL CHECK (semester IN ('Spring', 'Summer', 'Fall', 'Winter')),
    academic_year INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    UNIQUE (course_id, teacher_id, semester, academic_year)
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    offering_id INTEGER NOT NULL,
    passed INTEGER NOT NULL DEFAULT 0 CHECK (passed IN (0, 1)),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
    UNIQUE (student_id, offering_id)
);

CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL UNIQUE,
    points NUMERIC NOT NULL CHECK (points >= 0 AND points <= 100),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
);

CREATE INDEX idx_students_group_id ON students(group_id);
CREATE INDEX idx_course_offerings_course_id ON course_offerings(course_id);
CREATE INDEX idx_course_offerings_teacher_id ON course_offerings(teacher_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_offering_id ON enrollments(offering_id);

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

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
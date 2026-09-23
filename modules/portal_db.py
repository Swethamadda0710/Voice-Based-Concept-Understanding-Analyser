import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime


DB_PATH = os.environ.get("CONCEPTLENS_DB_PATH", os.path.join("data", "users.db"))


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password, stored):
    if stored.startswith("pbkdf2_sha256$"):
        _, salt, expected = stored.split("$", 2)
        actual = _hash_password(password, salt).split("$", 2)[2]
        return hmac.compare_digest(actual, expected)
    return hmac.compare_digest(hashlib.sha256(password.encode("utf-8")).hexdigest(), stored)


def connect():
    os.makedirs("data", exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    initialize(connection)
    return connection


def initialize(connection=None):
    owned = connection is None
    connection = connection or connect.__wrapped__() if hasattr(connect, "__wrapped__") else connection
    if connection is None:
        os.makedirs("data", exist_ok=True)
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
    legacy_users = []
    existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(users)").fetchall()}
    if existing_columns and "id" not in existing_columns:
        legacy_users = connection.execute("SELECT username, password FROM users").fetchall()
        connection.execute("ALTER TABLE users RENAME TO users_legacy")
    elif connection.execute("SELECT 1 FROM sqlite_master WHERE sql LIKE '%users_legacy%'").fetchone():
        legacy_users = connection.execute("SELECT username, password FROM users_legacy").fetchall()
        _repair_interrupted_migration(connection)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '', email TEXT DEFAULT '', role TEXT NOT NULL DEFAULT 'student',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE,
            teacher_id TEXT NOT NULL UNIQUE, department TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE,
            student_id TEXT NOT NULL UNIQUE, class_name TEXT DEFAULT '', section TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS teacher_students (
            teacher_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            PRIMARY KEY(teacher_id, student_id),
            FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, question_text TEXT NOT NULL,
            concept TEXT NOT NULL, subject TEXT DEFAULT '', difficulty TEXT DEFAULT '', reference_answer TEXT DEFAULT '',
            reference_answer_source TEXT DEFAULT 'Teacher Written', reference_answer_status TEXT DEFAULT 'Draft',
            generated_at TEXT, approved_at TEXT, approved_by INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(approved_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER NOT NULL, teacher_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL, assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY(question_id) REFERENCES questions(id), FOREIGN KEY(teacher_id) REFERENCES teachers(id),
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, assignment_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            audio_file TEXT, transcription TEXT, similarity_score REAL, final_score REAL, understanding_level TEXT,
            feedback TEXT, submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, attempt_number INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(assignment_id) REFERENCES assignments(id), FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """
    )
    for legacy_user in legacy_users:
        connection.execute("INSERT OR IGNORE INTO users (username, password, name, role) VALUES (?, ?, ?, 'student')", (legacy_user[0], legacy_user[1], legacy_user[0]))
    if legacy_users:
        connection.execute("DROP TABLE users_legacy")
        connection.commit()
    for user in connection.execute("SELECT id, role, name, email FROM users").fetchall():
        _ensure_profile(connection, user["id"], user["role"], user["name"], user["email"])
    connection.commit()
    if owned:
        connection.commit()
        connection.close()


def _repair_interrupted_migration(connection):
    """Rebuild tables whose FKs were rewritten when users was renamed."""
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    for table in ("teacher_students", "submissions", "assignments", "questions", "students", "teachers"):
        connection.execute(f"DROP TABLE IF EXISTS {table}")
    connection.executescript(
        """
        CREATE TABLE teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE,
            teacher_id TEXT NOT NULL UNIQUE, department TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE,
            student_id TEXT NOT NULL UNIQUE, class_name TEXT DEFAULT '', section TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE teacher_students (
            teacher_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            PRIMARY KEY(teacher_id, student_id),
            FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, question_text TEXT NOT NULL,
            concept TEXT NOT NULL, subject TEXT DEFAULT '', difficulty TEXT DEFAULT '', reference_answer TEXT DEFAULT '',
            reference_answer_source TEXT DEFAULT 'Teacher Written', reference_answer_status TEXT DEFAULT 'Draft',
            generated_at TEXT, approved_at TEXT, approved_by INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(approved_by) REFERENCES users(id)
        );
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER NOT NULL, teacher_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL, assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Pending', FOREIGN KEY(question_id) REFERENCES questions(id),
            FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(student_id) REFERENCES students(id)
        );
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, assignment_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            audio_file TEXT, transcription TEXT, similarity_score REAL, final_score REAL, understanding_level TEXT,
            feedback TEXT, submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, attempt_number INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(assignment_id) REFERENCES assignments(id), FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """
    )
    connection.commit()
    connection.execute("PRAGMA foreign_keys = ON")


def _ensure_profile(connection, user_id, role, name, email):
    if role == "teacher":
        connection.execute("INSERT OR IGNORE INTO teachers (user_id, teacher_id) VALUES (?, ?)", (user_id, f"T-{user_id:03d}"))
        connection.execute("UPDATE teachers SET department = COALESCE(NULLIF(department, ''), 'CSE') WHERE user_id = ?", (user_id,))
    else:
        connection.execute("INSERT OR IGNORE INTO students (user_id, student_id) VALUES (?, ?)", (user_id, f"S-{user_id:03d}"))
        student = connection.execute("SELECT student_id, section FROM students WHERE user_id = ?", (user_id,)).fetchone()
        section = student["section"] or chr(ord("A") + (user_id - 1) % 4)
        connection.execute("UPDATE students SET class_name = COALESCE(NULLIF(class_name, ''), 'CSE'), section = ? WHERE user_id = ?", (section, user_id))
        teachers = connection.execute("SELECT id FROM teachers").fetchall()
        student_row = connection.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
        for teacher in teachers:
            connection.execute("INSERT OR IGNORE INTO teacher_students (teacher_id, student_id) VALUES (?, ?)", (teacher["id"], student_row["id"]))
    default_email = f"{name.strip() or 'user'}.{user_id}@conceptlens.local".lower().replace(" ", ".")
    connection.execute("UPDATE users SET name = COALESCE(NULLIF(?, ''), name), email = COALESCE(NULLIF(email, ''), ?) WHERE id = ?", (name, email or default_email, user_id))


def seed_demo_users():
    connection = connect()
    demos = [("teacher", "teacher", "teacher123", "Demo Teacher", "teacher@example.com"), ("student", "student", "student123", "Student A", "student@example.com")]
    for role, username, password, name, email in demos:
        row = connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            cursor = connection.execute("INSERT INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)", (username, _hash_password(password), name, email, role))
            user_id = cursor.lastrowid
        else:
            user_id = row["id"]
        _ensure_profile(connection, user_id, role, name, email)
    teacher = connection.execute("SELECT teachers.id FROM teachers JOIN users ON users.id = teachers.user_id WHERE users.username = 'teacher'").fetchone()
    student = connection.execute("SELECT students.id FROM students JOIN users ON users.id = students.user_id WHERE users.username = 'student'").fetchone()
    if teacher and student:
        connection.execute("INSERT OR IGNORE INTO teacher_students (teacher_id, student_id) VALUES (?, ?)", (teacher["id"], student["id"]))
    connection.commit()
    connection.close()


def get_user(username, password, role=None):
    connection = connect()
    row = connection.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    if row is None or (role and row["role"] != role) or not verify_password(password, row["password"]):
        connection.close()
        return None
    _ensure_profile(connection, row["id"], row["role"], row["name"], row["email"])
    connection.commit()
    connection.close()
    return dict(row)


def create_user(username, password, role="student", name="", email="", class_name="CSE", section=""):
    username, role = username.strip(), role.lower()
    if not username or not password:
        return False, "Enter a username and password."
    if role not in {"student", "teacher"}:
        return False, "Choose a valid account role."
    connection = connect()
    try:
        cursor = connection.execute("INSERT INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)", (username, _hash_password(password), name.strip() or username, email.strip(), role))
        _ensure_profile(connection, cursor.lastrowid, role, name.strip() or username, email.strip())
        if role == "student":
            connection.execute("UPDATE students SET class_name = ?, section = ? WHERE user_id = ?", (class_name.strip() or "CSE", section.strip().upper() or "A", cursor.lastrowid))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        return False, "That username is already in use."
    connection.close()
    return True, "Account created. You can sign in now."


def profile_for_user(user_id, role):
    connection = connect()
    table = "teachers" if role == "teacher" else "students"
    row = connection.execute(f"SELECT users.*, {table}.* FROM users JOIN {table} ON {table}.user_id = users.id WHERE users.id = ?", (user_id,)).fetchone()
    connection.close()
    return dict(row) if row else None


def teacher_id_for_user(user_id):
    connection = connect(); row = connection.execute("SELECT id FROM teachers WHERE user_id = ?", (user_id,)).fetchone(); connection.close()
    return row["id"] if row else None


def student_id_for_user(user_id):
    connection = connect(); row = connection.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone(); connection.close()
    return row["id"] if row else None


def create_question(user_id, question_text, concept, subject, difficulty, reference_answer, source="Teacher Written", status="Draft"):
    teacher_id = teacher_id_for_user(user_id)
    if not teacher_id or not question_text.strip() or not concept.strip():
        return None
    connection = connect()
    cursor = connection.execute("INSERT INTO questions (teacher_id, question_text, concept, subject, difficulty, reference_answer, reference_answer_source, reference_answer_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (teacher_id, question_text.strip(), concept.strip(), subject, difficulty, reference_answer.strip(), source, status))
    connection.commit(); question_id = cursor.lastrowid; connection.close()
    return question_id


def approve_question(question_id, user_id, answer, source):
    teacher_id = teacher_id_for_user(user_id)
    connection = connect()
    connection.execute("UPDATE questions SET reference_answer = ?, reference_answer_source = ?, reference_answer_status = 'Approved', approved_at = ?, approved_by = ? WHERE id = ? AND teacher_id = ?", (answer.strip(), source, datetime.now().isoformat(timespec="seconds"), user_id, question_id, teacher_id))
    connection.commit(); connection.close()


def teacher_questions(user_id):
    teacher_id = teacher_id_for_user(user_id); connection = connect()
    rows = connection.execute("SELECT q.*, COUNT(a.id) AS assigned_count FROM questions q LEFT JOIN assignments a ON a.question_id = q.id WHERE q.teacher_id = ? GROUP BY q.id ORDER BY q.created_at DESC", (teacher_id,)).fetchall(); connection.close()
    return [dict(row) for row in rows]


def students_for_teacher(user_id):
    teacher_id = teacher_id_for_user(user_id); connection = connect()
    rows = connection.execute("SELECT s.*, u.name, u.email, COUNT(DISTINCT a.id) AS assigned_count, COUNT(DISTINCT sub.id) AS completed_count, COALESCE(AVG(sub.final_score), 0) AS average_score FROM teacher_students ts JOIN students s ON s.id = ts.student_id JOIN users u ON u.id = s.user_id LEFT JOIN assignments a ON a.student_id = s.id AND a.teacher_id = ts.teacher_id LEFT JOIN submissions sub ON sub.student_id = s.id AND sub.assignment_id = a.id WHERE ts.teacher_id = ? GROUP BY s.id ORDER BY u.name", (teacher_id,)).fetchall(); connection.close()
    return [dict(row) for row in rows]


def assign_question(user_id, question_id, student_id, due_date):
    teacher_id = teacher_id_for_user(user_id); connection = connect()
    valid = connection.execute("SELECT 1 FROM questions WHERE id = ? AND teacher_id = ?", (question_id, teacher_id)).fetchone()
    authorized_student = connection.execute("SELECT 1 FROM teacher_students WHERE teacher_id = ? AND student_id = ?", (teacher_id, student_id)).fetchone()
    if not valid or not authorized_student:
        connection.close(); return False
    connection.execute("INSERT INTO assignments (question_id, teacher_id, student_id, due_date) VALUES (?, ?, ?, ?)", (question_id, teacher_id, student_id, due_date or None)); connection.commit(); connection.close(); return True


def assign_question_to_students(user_id, question_id, student_ids, due_date):
    """Assign a teacher-owned question to authorized students without duplicates."""
    teacher_id = teacher_id_for_user(user_id)
    connection = connect()
    valid_question = connection.execute("SELECT 1 FROM questions WHERE id = ? AND teacher_id = ?", (question_id, teacher_id)).fetchone()
    if not valid_question:
        connection.close()
        return 0
    created = 0
    for student_id in set(student_ids):
        authorized = connection.execute("SELECT 1 FROM teacher_students WHERE teacher_id = ? AND student_id = ?", (teacher_id, student_id)).fetchone()
        existing = connection.execute("SELECT 1 FROM assignments WHERE question_id = ? AND teacher_id = ? AND student_id = ?", (question_id, teacher_id, student_id)).fetchone()
        if authorized and not existing:
            connection.execute("INSERT INTO assignments (question_id, teacher_id, student_id, due_date) VALUES (?, ?, ?, ?)", (question_id, teacher_id, student_id, due_date or None))
            created += 1
    connection.commit()
    connection.close()
    return created


def assignments_for_student(user_id):
    student_id = student_id_for_user(user_id); connection = connect()
    rows = connection.execute("SELECT a.*, q.question_text, q.concept, q.subject, q.reference_answer, q.reference_answer_status, u.name AS teacher_name, s.student_id FROM assignments a JOIN questions q ON q.id = a.question_id JOIN teachers t ON t.id = a.teacher_id JOIN users u ON u.id = t.user_id JOIN students s ON s.id = a.student_id WHERE a.student_id = ? AND q.reference_answer_status = 'Approved' ORDER BY a.assigned_at DESC", (student_id,)).fetchall(); connection.close()
    return [dict(row) for row in rows]


def submissions_for_student(user_id):
    student_id = student_id_for_user(user_id); connection = connect()
    rows = connection.execute("SELECT sub.*, q.question_text, q.concept FROM submissions sub JOIN assignments a ON a.id = sub.assignment_id JOIN questions q ON q.id = a.question_id WHERE sub.student_id = ? ORDER BY sub.submitted_at DESC", (student_id,)).fetchall(); connection.close(); return [dict(row) for row in rows]


def submissions_for_teacher(user_id):
    teacher_id = teacher_id_for_user(user_id); connection = connect()
    rows = connection.execute("SELECT sub.*, q.question_text, q.concept, u.name AS student_name, s.student_id FROM submissions sub JOIN assignments a ON a.id = sub.assignment_id JOIN questions q ON q.id = a.question_id JOIN students s ON s.id = sub.student_id JOIN users u ON u.id = s.user_id WHERE a.teacher_id = ? ORDER BY sub.submitted_at DESC", (teacher_id,)).fetchall(); connection.close(); return [dict(row) for row in rows]


def save_submission(user_id, assignment_id, audio_file, transcription, similarity, final_score, level, feedback):
    student_id = student_id_for_user(user_id); connection = connect()
    valid = connection.execute("SELECT 1 FROM assignments WHERE id = ? AND student_id = ?", (assignment_id, student_id)).fetchone()
    if not valid:
        connection.close(); return None
    attempt = connection.execute("SELECT COALESCE(MAX(attempt_number), 0) + 1 AS next_attempt FROM submissions WHERE assignment_id = ?", (assignment_id,)).fetchone()["next_attempt"]
    cursor = connection.execute("INSERT INTO submissions (assignment_id, student_id, audio_file, transcription, similarity_score, final_score, understanding_level, feedback, attempt_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (assignment_id, student_id, audio_file, transcription, similarity, final_score, level, feedback, attempt))
    connection.execute("UPDATE assignments SET status = 'Completed' WHERE id = ? AND student_id = ?", (assignment_id, student_id)); connection.commit(); submission_id = cursor.lastrowid; connection.close(); return submission_id


seed_demo_users()
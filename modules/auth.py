import hashlib
import os
import sqlite3


DB_PATH = os.path.join("data", "users.db")


def _connect():
    os.makedirs("data", exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL)")
    return connection


def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Enter a username and password."
    connection = _connect()
    try:
        connection.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, _hash_password(password)))
        connection.commit()
    except sqlite3.IntegrityError:
        return False, "That username is already in use."
    finally:
        connection.close()
    return True, "Account created. You can sign in now."


def authenticate(username, password):
    connection = _connect()
    row = connection.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username.strip(), _hash_password(password))).fetchone()
    connection.close()
    return row is not None


def change_password(username, current_password, new_password):
    if not authenticate(username, current_password):
        return False
    connection = _connect()
    connection.execute("UPDATE users SET password = ? WHERE username = ?", (_hash_password(new_password), username.strip()))
    connection.commit()
    connection.close()
    return True


def seed_demo_user():
    connection = _connect()
    connection.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", _hash_password("admin123")))
    connection.commit()
    connection.close()


seed_demo_user()
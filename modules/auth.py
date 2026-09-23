from modules import portal_db


def create_user(username, password, role="student", name="", email="", class_name="CSE", section="A"):
    return portal_db.create_user(username, password, role, name, email, class_name, section)


def authenticate(username, password):
    return portal_db.get_user(username, password) is not None


def authenticate_user(username, password, role):
    return portal_db.get_user(username, password, role)


def change_password(username, current_password, new_password):
    user = portal_db.get_user(username, current_password)
    if not user:
        return False
    connection = portal_db.connect()
    connection.execute("UPDATE users SET password = ? WHERE id = ?", (portal_db._hash_password(new_password), user["id"]))
    connection.commit()
    connection.close()
    return True

import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

class User:
    def __init__(self, user_id=None, email=None, role='user', status='active'):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.status = status

    @staticmethod
    def register(email, password):
        if not email or not password:
            return False, "Email and password are required."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (email, password, role, status) VALUES (?, ?, 'user', 'active')",
                (email, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, User(user_id, email, 'user', 'active')
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Email is already registered."

    @staticmethod
    def login(email, password):
        if not email or not password:
            return False, "Email and password are required."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password, role, status FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return False, "Invalid email or password."
        
        user_id, db_email, db_password, role, status = row
        if status == 'banned':
            return False, "Your account has been banned for violating our Terms of Service (ToS)."
            
        if check_password_hash(db_password, password):
            return True, User(user_id, db_email, role, status)
        return False, "Invalid email or password."

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, role, status FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            if row[3] == 'banned':
                return None
            return User(row[0], row[1], row[2], row[3])
        return None

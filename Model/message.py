import sqlite3

class Message:
    def __init__(self, message_id=None, sender_id=None, receiver_id=None, text=None, timestamp=None):
        self.id = message_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.text = text
        self.timestamp = timestamp

    @staticmethod
    def send_message(sender_id, receiver_id, text):
        if not text or not text.strip():
            return False, "Message text cannot be empty."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, text) VALUES (?, ?, ?)",
                (sender_id, receiver_id, text.strip())
            )
            conn.commit()
            msg_id = cursor.lastrowid
            conn.close()
            return True, msg_id
        except Exception as e:
            conn.close()
            return False, str(e)

    @staticmethod
    def get_chat_history(user1_id, user2_id):
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT messages.id, messages.sender_id, messages.receiver_id, messages.text, messages.timestamp,
                   sender.email as sender_email, receiver.email as receiver_email
            FROM messages
            JOIN users sender ON messages.sender_id = sender.id
            JOIN users receiver ON messages.receiver_id = receiver.id
            WHERE (messages.sender_id = ? AND messages.receiver_id = ?)
               OR (messages.sender_id = ? AND messages.receiver_id = ?)
            ORDER BY messages.timestamp ASC
        ''', (user1_id, user2_id, user2_id, user1_id))
        rows = cursor.fetchall()
        history = [dict(r) for r in rows]
        conn.close()
        return history

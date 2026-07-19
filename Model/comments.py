import sqlite3

class Comments:
    def __init__(self, comment_id=None, text=None, timestamp=None):
        self.id = comment_id
        self.text = text
        self.timestamp = timestamp

    @staticmethod
    def post_comment(crop_id, user_id, text):
        """Post a comment for a crop after checking ToS."""
        if not text or not text.strip():
            return False, "Comment cannot be empty."
            
        comment_checker = Comments(text=text)
        if not comment_checker.Check_ToS():
            return False, "Comment violates our Terms of Service (ToS). Inappropriate keywords detected."
            
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO comments (crop_id, user_id, text) VALUES (?, ?, ?)",
                (crop_id, user_id, text.strip())
            )
            conn.commit()
            comment_id = cursor.lastrowid
            conn.close()
            return True, comment_id
        except Exception as e:
            conn.close()
            return False, str(e)

    def Check_ToS(self):
        """Verify if comment breaks ToS."""
        if not self.text:
            return True
        # Standard content moderation check
        banned_words = ['scam', 'spam', 'hack', 'buy online', 'fuck', 'shit', 'idiot', 'advertising', 'promo', 'viagra', 'earn money']
        text_lower = self.text.lower()
        for word in banned_words:
            if word in text_lower:
                return False
        return True

    @staticmethod
    def delete_comment(comment_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

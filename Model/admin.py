import sqlite3
from Model.user import User

class Admin(User):
    def __init__(self, user_id=None, email=None, status='active'):
        super().__init__(user_id, email, 'admin', status)

    def uploadimage(self, crop_id, url, img_type):
        """Admin should be able to post and remove images."""
        if not url or img_type not in ['healthy', 'infected']:
            return False, "Invalid image details."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO crop_images (crop_id, url, type) VALUES (?, ?, ?)",
                (crop_id, url, img_type)
            )
            conn.commit()
            img_id = cursor.lastrowid
            conn.close()
            return True, img_id
        except Exception as e:
            conn.close()
            return False, str(e)

    def addcropsinfo(self, scientific_name, common_name, medicinal_benefit):
        """Admin should be able to add crop info."""
        if not scientific_name or not common_name:
            return False, "Scientific name and common name are required."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO crops (scientific_name, common_name, medicinal_benefit) VALUES (?, ?, ?)",
                (scientific_name, common_name, medicinal_benefit)
            )
            conn.commit()
            crop_id = cursor.lastrowid
            conn.close()
            return True, crop_id
        except Exception as e:
            conn.close()
            return False, str(e)

    def manage_category(self, crop_id, disease_name, description, treatment, is_treatable):
        """Admin can add or modify disease info (categorized details)."""
        if not disease_name or not description or not treatment:
            return False, "Disease name, description, and treatment plan are required."
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM diseases WHERE crop_id = ? AND disease_name = ?", (crop_id, disease_name))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE diseases SET description = ?, treatment = ?, is_treatable = ? WHERE id = ?",
                    (description, treatment, 1 if is_treatable else 0, row[0])
                )
                msg = "Disease updated successfully."
                disease_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO diseases (crop_id, disease_name, description, treatment, is_treatable) VALUES (?, ?, ?, ?, ?)",
                    (crop_id, disease_name, description, treatment, 1 if is_treatable else 0)
                )
                msg = "Disease added successfully."
                disease_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True, {"message": msg, "id": disease_id}
        except Exception as e:
            conn.close()
            return False, str(e)

    def ban(self, user_id):
        """Admin can ban users who spread misinformation or break ToS."""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET status = 'banned' WHERE id = ? AND role != 'admin'", (user_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            if success:
                return True, "User successfully banned."
            return False, "User not found or user is admin."
        except Exception as e:
            conn.close()
            return False, str(e)
            
    def unban(self, user_id):
        """Admin can unban users."""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            if success:
                return True, "User successfully unbanned."
            return False, "User not found."
        except Exception as e:
            conn.close()
            return False, str(e)

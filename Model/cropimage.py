import sqlite3

class Cropimage:
    def __init__(self, image_id=None, url=None, img_type=None):
        self.id = image_id
        self.url = url
        self.type = img_type

    @staticmethod
    def addimage(crop_id, url, img_type):
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

    @staticmethod
    def removeimage(image_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crop_images WHERE id = ?", (image_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

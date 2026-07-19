import sqlite3

class Crops:
    def __init__(self, crop_id=None, scientname=None, common_name=None, medical_benifit=None):
        self.id = crop_id
        self.scientname = scientname
        self.common_name = common_name
        self.medical_benifit = medical_benifit

    def getinfo(self):
        """Fetch all details including images, diseases, and comments for this crop."""
        if not self.id:
            return None
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get crop details
        cursor.execute("SELECT * FROM crops WHERE id = ?", (self.id,))
        crop_row = cursor.fetchone()
        if not crop_row:
            conn.close()
            return None
            
        crop_data = {
            "id": crop_row["id"],
            "scientific_name": crop_row["scientific_name"],
            "common_name": crop_row["common_name"],
            "medicinal_benefit": crop_row["medicinal_benefit"]
        }
        
        # Get images
        cursor.execute("SELECT id, url, type FROM crop_images WHERE crop_id = ?", (self.id,))
        crop_data['images'] = [dict(r) for r in cursor.fetchall()]
        
        # Get diseases
        cursor.execute("SELECT id, disease_name, description, treatment, is_treatable FROM diseases WHERE crop_id = ?", (self.id,))
        crop_data['diseases'] = [dict(r) for r in cursor.fetchall()]
        
        # Get comments
        cursor.execute('''
            SELECT comments.id, comments.text, comments.timestamp, users.email, users.id as user_id
            FROM comments 
            JOIN users ON comments.user_id = users.id 
            WHERE comments.crop_id = ?
            ORDER BY comments.timestamp DESC
        ''', (self.id,))
        crop_data['comments'] = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return crop_data

    @staticmethod
    def get_all():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, scientific_name, common_name, medicinal_benefit FROM crops")
        rows = cursor.fetchall()
        
        crops_list = []
        for r in rows:
            crop_dict = {
                "id": r["id"],
                "scientific_name": r["scientific_name"],
                "common_name": r["common_name"],
                "medicinal_benefit": r["medicinal_benefit"]
            }
            # Fetch primary image
            cursor.execute("SELECT url FROM crop_images WHERE crop_id = ? AND type = 'healthy' LIMIT 1", (r['id'],))
            img_row = cursor.fetchone()
            crop_dict['primary_image'] = img_row['url'] if img_row else '/static/images/default.jpg'
            crops_list.append(crop_dict)
            
        conn.close()
        return crops_list

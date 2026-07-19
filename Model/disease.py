import sqlite3

class Disease:
    def __init__(self, disease_id=None, diseasename=None, descriptions=None, treatment=None, is_treatable=None):
        self.id = disease_id
        self.diseasename = diseasename
        self.descriptions = descriptions
        self.treatment = treatment
        self.is_treatable = is_treatable

    def gettreatmentplan(self):
        """Retrieve treatment plan and details for this disease."""
        if not self.id:
            return None
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, crop_id, disease_name, description, treatment, is_treatable FROM diseases WHERE id = ?", (self.id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row["id"],
                "crop_id": row["crop_id"],
                "disease_name": row["disease_name"],
                "description": row["description"],
                "treatment": row["treatment"],
                "is_treatable": bool(row["is_treatable"])
            }
        return None

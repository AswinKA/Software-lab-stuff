class Category:
    def __init__(self, category_id=None, name=None, description=None):
        self.id = category_id
        self.name = name
        self.description = description

    def extend(self):
        # This represents expansion behavior modeled on the frontend
        return True

    def collapse(self):
        # This represents collapse behavior modeled on the frontend
        return True

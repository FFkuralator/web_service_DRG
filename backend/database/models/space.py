from flask import current_app
from backend.database.db import Database


class Space:
    def __init__(self, db_path=None):
        self.db = Database(db_path or current_app.config['DATABASE'])

    def get_all_spaces(self):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.image_src, s.image_alt,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
        """)

        result = []
        for space in spaces:
            result.append({
                'id': space[0],
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'image_src': space[6],
                'image_alt': space[7],
                'category_name': space[8],
                'features': self.get_space_features(space[0])
            })
        return result

    def get_by_category(self, category_id):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location,
                   s.description, s.image_src, s.image_alt,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            WHERE s.category_id = ?
        """, (category_id,))

        result = []
        for space in spaces:
            result.append({
                'id': space[0],
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'image_src': space[6],
                'image_alt': space[7],
                'category_name': space[8],
                'features': self.get_space_features(space[0])
            })
        return result

    def get_space_features(self, space_id):
        features = self.db.execute(
            "SELECT feature FROM space_features WHERE space_id = ?",
            (space_id,)
        )
        return [f[0] for f in features]

    def get_favorites(self, user_id):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location,
                   s.description, s.image_src, s.image_alt,
                   c.name AS category_name
            FROM spaces s
            JOIN user_favorites uf ON s.id = uf.space_id
            JOIN categories c ON s.category_id = c.id
            WHERE uf.user_id = ?
        """, (user_id,))

        result = []
        for space in spaces:
            result.append({
                'id': space[0],
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'image_src': space[6],
                'image_alt': space[7],
                'category_name': space[8],
                'features': self.get_space_features(space[0])
            })
        return result

    def get_filtered_spaces(self, category_id=None, building=None, features=None):
        query = """
            SELECT s.id, s.name, s.building, s.level, s.location,
                   s.description, s.image_src, s.image_alt,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            WHERE 1=1
        """
        params = []

        if category_id:
            query += " AND s.category_id = ?"
            params.append(category_id)

        if building:
            query += " AND s.building = ?"
            params.append(building)

        if features:
            query += """
                AND EXISTS (
                    SELECT 1 FROM space_features sf 
                    WHERE sf.space_id = s.id AND sf.feature IN ({})
                )
            """.format(','.join(['?'] * len(features)))
            params.extend(features)

        spaces = self.db.execute(query, tuple(params))

        result = []
        for space in spaces:
            result.append({
                'id': space[0],
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'image_src': space[6],
                'image_alt': space[7],
                'category_name': space[8],
                'features': self.get_space_features(space[0])
            })
        return result
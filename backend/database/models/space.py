from flask import current_app
from backend.database.db import Database


class Space:
    def __init__(self, db_path=None):
        self.db = Database(db_path or current_app.config['DATABASE'])

    def get_all_spaces(self):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.location_description, s.likes, s.map_url,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            ORDER BY s.name
        """)

        result = []
        for space in spaces:
            space_id = space[0]
            result.append({
                'id': space_id,
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'location_description': space[6],
                'likes': space[7],
                'map_url': space[8],
                'category_name': space[9],
                'primary_image': self.get_primary_image(space_id),
                'images': self.get_space_images(space_id),
                'features': self.get_space_features(space_id)
            })
        return result

    def get_by_id(self, space_id):
        space = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.location_description, s.likes, s.map_url,
                   c.name AS category_name, c.id AS category_id
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            WHERE s.id = ?
        """, (space_id,), fetch_one=True)

        if not space:
            return None

        return {
            'id': space[0],
            'name': space[1],
            'building': space[2],
            'level': space[3],
            'location': space[4],
            'description': space[5],
            'location_description': space[6],
            'likes': space[7],
            'map_url': space[8],
            'category_name': space[9],
            'category_id': space[10],
            'images': self.get_space_images(space_id),
            'features': self.get_space_features(space_id)
        }

    def get_by_category(self, category_id):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.location_description, s.likes, s.map_url,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            WHERE s.category_id = ?
            ORDER BY s.name
        """, (category_id,))

        result = []
        for space in spaces:
            space_id = space[0]
            result.append({
                'id': space_id,
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'location_description': space[6],
                'likes': space[7],
                'map_url': space[8],
                'category_name': space[9],
                'primary_image': self.get_primary_image(space_id),
                'images': self.get_space_images(space_id),
                'features': self.get_space_features(space_id)
            })
        return result

    def get_space_features(self, space_id):
        features = self.db.execute(
            "SELECT feature FROM space_features WHERE space_id = ?",
            (space_id,)
        )
        return [f[0] for f in features]

    def get_space_images(self, space_id):
        images = self.db.execute(
            "SELECT id, image_url, alt_text, is_primary FROM space_images WHERE space_id = ? ORDER BY is_primary DESC, id",
            (space_id,)
        )
        return [{
            'id': img[0],
            'url': img[1],
            'alt': img[2],
            'is_primary': bool(img[3])
        } for img in images]

    def get_primary_image(self, space_id):
        image = self.db.execute(
            "SELECT image_url, alt_text FROM space_images WHERE space_id = ? AND is_primary = 1 LIMIT 1",
            (space_id,),
            fetch_one=True
        )
        return {'url': image[0], 'alt': image[1]} if image else None

    def get_favorites(self, user_id):
        spaces = self.db.execute("""
            SELECT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.location_description, s.likes, s.map_url,
                   c.name AS category_name
            FROM spaces s
            JOIN user_favorites uf ON s.id = uf.space_id
            JOIN categories c ON s.category_id = c.id
            WHERE uf.user_id = ?
            ORDER BY s.name
        """, (user_id,))

        result = []
        for space in spaces:
            space_id = space[0]
            result.append({
                'id': space_id,
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'location_description': space[6],
                'likes': space[7],
                'map_url': space[8],
                'category_name': space[9],
                'primary_image': self.get_primary_image(space_id),
                'images': self.get_space_images(space_id),
                'features': self.get_space_features(space_id)
            })
        return result

    def get_filtered_spaces(self, category_id=None, building=None, features=None):
        query = """
            SELECT DISTINCT s.id, s.name, s.building, s.level, s.location, 
                   s.description, s.location_description, s.likes, s.map_url,
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
            placeholders = ','.join(['?'] * len(features))
            query += f"""
                AND s.id IN (
                    SELECT sf.space_id 
                    FROM space_features sf 
                    WHERE sf.feature IN ({placeholders})
                    GROUP BY sf.space_id
                    HAVING COUNT(DISTINCT sf.feature) = ?
                )
            """
            params.extend(features)
            params.append(len(features))

        query += " ORDER BY s.name"
        spaces = self.db.execute(query, tuple(params))

        result = []
        for space in spaces:
            space_id = space[0]
            result.append({
                'id': space_id,
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'location': space[4],
                'description': space[5],
                'location_description': space[6],
                'likes': space[7],
                'map_url': space[8],
                'category_name': space[9],
                'primary_image': self.get_primary_image(space_id),
                'features': self.get_space_features(space_id)
            })
        return result

    def add_to_favorites(self, user_id, space_id):
        try:
            self.db.execute(
                "INSERT OR IGNORE INTO user_favorites (user_id, space_id) VALUES (?, ?)",
                (user_id, space_id)
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error adding to favorites: {e}")
            return False

    def remove_from_favorites(self, user_id, space_id):
        try:
            self.db.execute(
                "DELETE FROM user_favorites WHERE user_id = ? AND space_id = ?",
                (user_id, space_id)
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error removing from favorites: {e}")
            return False

    def is_favorite(self, user_id, space_id):
        result = self.db.execute(
            "SELECT 1 FROM user_favorites WHERE user_id = ? AND space_id = ?",
            (user_id, space_id),
            fetch_one=True
        )
        return bool(result)

    def add_image(self, space_id, image_url, alt_text="", is_primary=False):
        try:
            if is_primary:
                self.db.execute(
                    "UPDATE space_images SET is_primary = 0 WHERE space_id = ?",
                    (space_id,)
                )

            self.db.execute(
                """INSERT INTO space_images 
                (space_id, image_url, alt_text, is_primary) 
                VALUES (?, ?, ?, ?)""",
                (space_id, image_url, alt_text, int(is_primary)))
            return True
        except Exception as e:
            current_app.logger.error(f"Error adding space image: {e}")
            return False

    def delete_image(self, image_id):
        try:
            self.db.execute(
                "DELETE FROM space_images WHERE id = ?",
                (image_id,)
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting space image: {e}")
            return False

    def set_primary_image(self, space_id, image_id):
        try:
            self.db.execute(
                "UPDATE space_images SET is_primary = 0 WHERE space_id = ?",
                (space_id,)
            )

            self.db.execute(
                "UPDATE space_images SET is_primary = 1 WHERE id = ? AND space_id = ?",
                (image_id, space_id)
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error setting primary image: {e}")
            return False

    def increment_likes(self, space_id):
        try:
            self.db.execute(
                "UPDATE spaces SET likes = likes + 1 WHERE id = ?",
                (space_id,)
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error incrementing likes: {e}")
            return False

    def get_popular_spaces(self, limit=5):
        spaces = self.db.execute(f"""
            SELECT s.id, s.name, s.building, s.level, s.likes,
                   c.name AS category_name
            FROM spaces s
            JOIN categories c ON s.category_id = c.id
            ORDER BY s.likes DESC
            LIMIT ?
        """, (limit,))

        result = []
        for space in spaces:
            space_id = space[0]
            result.append({
                'id': space_id,
                'name': space[1],
                'building': space[2],
                'level': space[3],
                'likes': space[4],
                'category_name': space[5],
                'primary_image': self.get_primary_image(space_id)
            })
        return result
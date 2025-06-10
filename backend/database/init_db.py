import sqlite3
from contextlib import closing
from backend.database.db import Database


def init_sample_data():
    db = Database('/Users/ffkura/PycharmProjects/web_service_DRG2/instance/app.db')

    with closing(db._get_connection()) as conn:
        conn.executescript("""
            DELETE FROM space_features;
            DELETE FROM user_favorites;
            DELETE FROM spaces;
            DELETE FROM categories;
        """)
        conn.commit()

    categories = [
        (1, "Танцы"),
        (2, "Не танцы"),
        (3, "Мероприятия")
    ]

    spaces = [
        (1, "Танцевальная студия", "A", "6", "A666", "Просторное помещение для танцев с зеркалами", "assets/dance1.jpg", "", 1),
        (2, "Малый танцзал", "A", "6", "A667", "Компактное пространство для репетиций", "assets/dance2.jpg", "", 3),
        (3, "Учебный класс", "B", "3", "B305", "Помещение для занятий с проектором", "assets/study1.jpg", "", 2),
        (4, "Танцевальная студия", "A", "6", "A666", "Просторное помещение для танцев с зеркалами", "assets/dance1.jpg",
         "", 1),
        (5, "Малый танцзал", "A", "6", "A667", "Компактное пространство для репетиций", "assets/dance2.jpg", "", 1),
        (6, "Учебный класс", "B", "3", "B305", "Помещение для занятий с проектором", "assets/study1.jpg", "", 2),
        (7, "Танцевальная студия", "A", "6", "A666", "Просторное помещение для танцев с зеркалами", "assets/dance1.jpg",
         "", 1),
        (8, "Малый танцзал", "A", "6", "A667", "Компактное пространство для репетиций", "assets/dance2.jpg", "", 3),
        (9, "Учебный класс", "B", "3", "B305", "Помещение для занятий с проектором", "assets/study1.jpg", "", 2)

    ]

    features = [
        (1, "projector"),
        (1, "mirror_wall"),
        (1, "sound_system"),
        (2, "mirror_wall"),
        (3, "projector"),
        (3, "whiteboard")
    ]

    with closing(db._get_connection()) as conn:
        try:
            conn.executemany(
                "INSERT INTO categories (id, name) VALUES (?, ?)",
                categories
            )

            conn.executemany(
                """INSERT INTO spaces 
                (id, name, building, level, location, description, image_src, image_alt, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                spaces
            )

            conn.executemany(
                "INSERT OR IGNORE INTO space_features (space_id, feature) VALUES (?, ?)",
                features
            )

            conn.commit()
            print("✅ Данные успешно загружены в БД:")
            print(f"- {len(categories)} категорий")
            print(f"- {len(spaces)} пространств")
            print(f"- {len(features)} характеристик")

        except sqlite3.Error as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    init_sample_data()
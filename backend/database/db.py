import os
import sqlite3
from contextlib import closing
from typing import Optional, List, Union


class Database:
    def __init__(self, db_path: str = 'instance/app.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = os.path.abspath(db_path)
        self._init_db()

    def _init_db(self):
        with closing(self._get_connection()) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    number_phone TEXT UNIQUE NOT NULL,
                    image_src TEXT,
                    image_alt TEXT,
                    is_admin BOOLEAN DEFAULT TRUE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS space_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    space_id INTEGER NOT NULL,
                    image_url TEXT NOT NULL,
                    alt_text TEXT,
                    is_primary BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (space_id) REFERENCES spaces(id)  
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS spaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    building TEXT NOT NULL,
                    level TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    location_description TEXT,
                    likes INTEGER,
                    map_url TEXT,
                    category_id INTEGER NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS space_features (
                    space_id INTEGER NOT NULL,
                    feature TEXT NOT NULL,
                    PRIMARY KEY (space_id, feature),
                    FOREIGN KEY (space_id) REFERENCES spaces(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_favorites (
                    user_id INTEGER NOT NULL,
                    space_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, space_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (space_id) REFERENCES spaces(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    space_id INTEGER NOT NULL,
                    booking_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (space_id) REFERENCES spaces(id)
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_space_category ON spaces(category_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_space_features ON space_features(space_id)")

            conn.commit()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute(self, query: str, params: tuple = (), fetch_one: bool = False) -> Union[List, Optional[tuple]]:
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

import sqlite3
from contextlib import closing
from typing import Optional, List, Union


class Database:
    def __init__(self, db_path: str = 'app.db'):
        self.db_path = db_path
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
                    image_alt,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    building TEXT NOT NULL,
                    level TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    image_src TEXT, 
                    image_alt TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                    
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

            conn.commit()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute(self, query: str, params: tuple = (), fetch_one: bool = False) -> Union[List, Optional[tuple]]:
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchone() if fetch_one else cursor.fetchall()
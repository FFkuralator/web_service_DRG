import sqlite3
import os


class Database:
    def __init__(self, db_path: str = 'app.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.db_path):
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()

    def insert(self, table: str, data: dict) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        result = self.execute(query, tuple(data.values()))
        return result.lastrowid  # Возвращает ID новой записи

    def select_one(self, table: str, where: dict) -> Optional[dict]:
        conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"SELECT * FROM {table} WHERE {conditions}"
        return self.execute(query, tuple(where.values()), fetch_one=True)


    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute(self, query, params=(), fetch_one=False):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
            return result
            
        except sqlite3.Error as e:
            conn.rollback()
            raise e
            
        finally:
            conn.close()

import sqlite3

from flask import current_app
from backend.database.db import Database
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes="bcrypt",
    deprecated="auto",
    bcrypt__ident="2b",
    sha256_crypt__default_rounds=10000
)


class User:
    def __init__(self, db_path=None):
        self.db = Database(db_path or current_app.config['DATABASE'])


    def create(self, email: str, password: str, full_name: str):
        hashed_password = pwd_context.hash(password)

        try:
            self.db.execute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
                (email, hashed_password, full_name)
            )
            return True

        except sqlite3.IntegrityError:
            raise ValueError('Пользователь с таким email уже существует')

    def authenticate(self, email: str, password: str):
        user = self.db.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
            fetch_one=True
        )

        if user and pwd_context.verify(password, user[2]):
            return user[0]
        return None

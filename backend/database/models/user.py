import sqlite3, re
from flask import current_app
from backend.database.db import Database
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"
)


class User:
    def __init__(self, db_path=None):
        self.db = Database(db_path or current_app.config['DATABASE'])

    @staticmethod
    def normalize_phone(number: str):
        if not number:
            return None

        cleaned = re.sub(r'[^\d+]', '', number)

        if cleaned.startswith('8'):
            return '+7' + cleaned[1:]
        elif cleaned.startswith('7'):
            return '+' + cleaned
        return cleaned


    def create(self, email: str, password: str, full_name: str, number_phone: str):

        if len(password) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')

        if not number_phone:
            raise ValueError('Номер телефона обязателен')

        hashed_password = pwd_context.hash(password)
        normalized_phone = self.normalize_phone(number_phone) if number_phone else None

        try:
            self.db.execute(
                """INSERT INTO users 
                (email, password_hash, full_name, number_phone) 
                VALUES (?, ?, ?, ?)""",
                (email, hashed_password, full_name, normalized_phone)
            )
            return True
        except sqlite3.IntegrityError as e:

            if 'email' in str(e):
                raise ValueError('Пользователь с таким email уже существует')
            elif 'number_phone' in str(e):
                raise ValueError('Пользователь с таким номером телефона уже существует')
            raise ValueError('Ошибка при создании пользователя')

    def authenticate(self, email: str, password: str):
        user = self.db.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
            fetch_one=True
        )

        if user and pwd_context.verify(password, user[2]):
            return user[0]
        return None

    def get_user_data(self, user_id: int):
        return self.db.execute(
            """SELECT email, full_name, number_phone, image_src 
               FROM users WHERE id = ?""",
                (user_id,),
            fetch_one=True
        )

    def email_exists(self, email: str):
        result = self.db.execute(
            "SELECT 1 FROM users WHERE email = ? LIMIT 1",
            (email,),
            fetch_one=True
        )
        return result is not None

    def phone_exists(self, phone: str):
        result = self.db.execute(
            "SELECT 1 FROM users WHERE number_phone = ? LIMIT 1",
            (phone,),
            fetch_one=True
        )
        return result is not None


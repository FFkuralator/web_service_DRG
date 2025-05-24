from db import Database
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(self):
        self.db = Database()

    def create(self, emeil: str, password: str, full_name: str):
        hashed_password = pwd_context.hash(password)
        
        try:
            self.db.exevute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
                (email, password_hash, full_name)
            )
            return True
            
        except sqlite3.IntegrityError:
            raise ValueError('Пользователь с таким email уже существует')
    
    def authenticate(self, email: str, password: str):
        user = self.db.execute(
            "SELECT id, email, password_hash FROM users WHERE emeil = ?",
            (email),
            fetch_one=True
        )
        
        if user and pwd_context.verify(password, user[2]):
            return user[0]
        return None

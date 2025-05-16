import re

from flask import Blueprint, request, jsonify
import bcrypt
from api.extensions import db
from api.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False

    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)

    return has_digit and has_upper and has_lower



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if not is_valid_password(data['password']):
        return jsonify({
            'error': 'Пароль должен содержать минимум 8 символов, '
                     '1 цифру, 1 заглавную букву, 1 строчную букву и 1 спецсимвол'
        }), 400


    if not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'error': 'Необходимо указать username, password и email'}), 400

    if not is_valid_email(data['email']):
        return jsonify({'error': 'Некорректный email'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Ник уже занят'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email уже занят'}), 400

    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        username=data['username'],
        password=password_hash,
        email=data['email']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201
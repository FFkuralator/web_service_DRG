import re
from functools import wraps

from flask import Blueprint, request, redirect, session, url_for, flash, render_template

from backend.database.models.user import *


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        password_check = request.form.get('password_check', '')
        full_name = request.form.get('full_name', '').strip()
        number_phone = request.form.get('number_phone', '').strip()

        if not all([email, password, full_name, number_phone]):
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('auth/auth.html',
                                   email = email,
                                   full_name = full_name,
                                   number_phone = number_phone)

        if not number_phone:
            flash('Номер телефона обязателен', 'danger')
            return render_template('auth/auth.html',
                                   email=email,
                                   number_phone=number_phone,
                                   full_name=full_name)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Некорректный email', 'danger')
            return render_template('auth/auth.html',
                                   email = email, full_name = full_name)

        if len(password) < 8:
            flash('Пароль должен содержать минимум 8 символов', 'danger')
            return render_template('auth/auth.html',
                                   email = email, full_name = full_name)

        if password != password_check:
            flash('Пароли не совпадают', 'danger')
            return render_template('auth/auth.html',
                                email=email,
                                full_name=full_name,
                                number_phone=number_phone,
                                password_check=password_check)

        user = User()
        if user.email_exists(email):
            flash('Этот email уже зарегистрирован', 'danger')
            return render_template('auth/auth.html',
                                email='',
                                full_name=full_name,
                                number_phone=number_phone)

        if user.phone_exists(number_phone):
            flash('Этот номер телефона уже зарегистрирован', 'danger')
            return render_template('auth/auth.html',
                                email=email,
                                full_name=full_name,
                                number_phone='')

        try:
            if user.create(email, password, full_name, number_phone):
                flash('Регистрация успешна! Теперь войдите.', 'success')
                return redirect(url_for('auth_bp.login'))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')

    return render_template('auth/auth.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для доступа к этой странице необходимо войти в систему', 'warning')
            return redirect(url_for('auth_bp.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not all([email, password]):
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('auth/auth.html', login_form=True)

        try:
            user = User()
            user_id = user.authenticate(email, password)

            if user_id:
                session['user_id'] = user_id
                flash('Вход выполнен успешно!', 'success')

                next_page = request.args.get('next')
                return redirect(next_page or url_for('profile'))
            else:
                flash('Неверный email или пароль', 'danger')
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash('Ошибка сервера при входе', 'danger')

    return render_template('auth/auth.html', login_form=True)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth_bp.login'))

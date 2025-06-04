import re
from flask import Blueprint, request, redirect, session, url_for, flash, render_template

from backend.database.models.user import *


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        number_phone = request.form.get('number_phone', '').strip()

        if not all([email, password, full_name, number_phone]):
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('auth/register.html',
                                   email = email, full_name = full_name, number_phone = number_phone)

        if not number_phone:
            flash('Номер телефона обязателен', 'danger')
            return render_template('auth/auth.html',
                                   email=email,
                                   number_phone=number_phone,
                                   full_name=full_name)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Некорректный email', 'danger')
            return render_template('auth/register.html',
                                   email = email, full_name = full_name)

        if len(password) < 8:
            flash('Пароль должен содержать минимум 8 символов', 'danger')
            return render_template('auth/register.html',
                                   email = email, full_name = full_name)

        try:
            user = User()
            if user.create(email, password, full_name, number_phone):
                flash('Регистрация успешна! Теперь войдите.', 'success')
                return redirect(url_for('auth_bp.login'))  # Исправлен url_for

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Произошла ошибка: {str(    e)}', 'danger')

    return render_template('signup.html')  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')

        if not all([email, password]):
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('auth.register'))

        user = User()
        user_id = user.authenticate(email, password)

        if user_id:
            session['user_id'] = user_id
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('auth/profile.html')  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

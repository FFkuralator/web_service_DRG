from flask import Blueprint, request, redirect, session, url_for, flash, render_template
from models.user import User 
import sqlite3

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not all([email, password, full_name]):
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            user = User()
            if user.create(email, password, full_name):
                flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
                return redirect(url_for('auth.login'))
                
        except ValueError as e:
            flash(str(e), 'danger')
        except sqlite3.IntegrityError:
            flash('Пользователь с таким email уже существует', 'danger')
        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')
    
    return render_template('') #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
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
        
    return render_template('') #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

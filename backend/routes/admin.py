import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from backend.database.models.user import User
from backend.database.db import Database
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or not g.user.get('is_admin'):
            flash(  'Доступ запрещен: требуются права администратора', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.before_request
@admin_required
def before_request():
    #Проверка прав администратора для всех роутов /admin
    pass


@admin_bp.route('/')
def dashboard():
    db = Database()

    users_count = db.execute("SELECT COUNT(*) FROM users", fetch_one=True)[0]
    spaces_count = db.execute("SELECT COUNT(*) FROM spaces", fetch_one=True)[0]
    bookings_count = db.execute("SELECT COUNT(*) FROM bookings", fetch_one=True)[0]

    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           spaces_count=spaces_count,
                           bookings_count=bookings_count)


@admin_bp.route('/users')
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    user_model = User()
    total_users = user_model.db.execute("SELECT COUNT(*) FROM users", fetch_one=True)[0]
    users = user_model.db.execute(
        """SELECT id, email, full_name, number_phone, is_admin, is_banned,
           strftime('%d.%m.%Y %H:%M', created_at) 
           FROM users 
           ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (per_page, (page - 1) * per_page)
    )

    return render_template('admin/users.html',
                           users=users,
                           page=page,
                           per_page=per_page,
                           total_users=total_users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    user_model = User()
    current_status = user_model.is_admin(user_id)

    if current_status:
        user_model.revoke_admin(user_id)
        flash('Права администратора отозваны', 'success')
    else:
        user_model.make_admin(user_id)
        flash('Пользователь назначен администратором', 'success')

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/spaces')
def manage_spaces():
    db = Database()
    spaces = db.execute(
        """SELECT s.id, s.name, c.name, s.building, s.level, s.likes,
           (SELECT COUNT(*) FROM user_favorites WHERE space_id = s.id) as favorites
           FROM spaces s
           JOIN categories c ON s.category_id = c.id
           ORDER BY s.id DESC"""
    )
    return render_template('admin/spaces.html', spaces=spaces)

@admin_bp.route('/bookings')
def manage_bookings():
    db = Database()
    bookings = db.execute(
        """SELECT b.id, u.email, s.name, 
           strftime('%d.%m.%Y', b.booking_date) as date,
           strftime('%H:%M', b.start_time) || '-' || strftime('%H:%M', b.end_time) as time,
           strftime('%d.%m.%Y %H:%M', b.created_at) as created
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           JOIN spaces s ON b.space_id = s.id
           ORDER BY b.booking_date DESC, b.start_time DESC"""
    )
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/bookings/<int:booking_id>/delete', methods=['POST'])
def delete_booking(booking_id):
    db = Database()
    db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    flash('Бронирование успешно удалено', 'success')
    return redirect(url_for('admin.manage_bookings'))

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
def ban_user(user_id):
    db = Database()
    db.execute("UPDATE users SET is_banned = TRUE WHERE id = ?", (user_id,))
    flash('Пользователь заблокирован', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
def unban_user(user_id):
    db = Database()
    db.execute("UPDATE users SET is_banned = FALSE WHERE id = ?", (user_id,))
    flash('Пользователь разблокирован', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/space/<int:space_id>/update', methods=['POST'])
def update_space(space_id):
    data = request.form
    db = Database()
    db.execute(
        """UPDATE spaces SET 
           name = ?, building = ?, level = ?, location = ?,
           description = ?, location_description = ?, map_url = ?
           WHERE id = ?""",
        (data['name'], data['building'], data['level'], data['location'],
         data['description'], data['location_description'], data['map_url'], space_id)
    )
    flash('Пространство обновлено', 'success')
    return redirect(url_for('admin.manage_spaces'))

@admin_bp.route('/user/<int:user_id>/bookings')
@admin_required
def get_user_bookings(user_id):
    user_model = User()
    bookings = user_model.get_user_with_bookings(user_id)
    return jsonify([{
        'id': b[0],
        'space_name': b[1],
        'date': b[2],
        'time': b[3],
        'comment': b[4]
    } for b in bookings])


@admin_bp.route('/users/filter')
@admin_required
def filter_users():
    status = request.args.get('status')
    activity = request.args.get('activity')

    query = "SELECT id, email, full_name, is_admin, is_banned FROM users WHERE 1=1"
    params = []

    if status:
        if 'admin' in status:
            query += " AND is_admin = 1"
        if 'banned' in status:
            query += " AND is_banned = 1"

    users = Database().execute(query, params)
    return render_template('admin/users_partial.html', users=users)


@admin_bp.route('/spaces/create', methods=['GET', 'POST'])
def create_space():
    if request.method == 'POST':
        data = request.form
        db = Database()
        try:
            db.execute(
                """INSERT INTO spaces 
                (name, building, level, location, description, category_id) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (data['name'], data['building'], data['level'],
                 data['location'], data['description'], data['category_id'])
            )
            flash('Пространство успешно создано', 'success')
            return redirect(url_for('admin.manage_spaces'))
        except Exception as e:
            flash(f'Ошибка при создании пространства: {str(e)}', 'error')

    categories = Database().execute("SELECT id, name FROM categories")
    return render_template('admin/create_space.html', categories=categories)


@admin_bp.route('/spaces/<int:space_id>/delete', methods=['POST'])
def delete_space(space_id):
    try:
        db = Database()
        db.execute("DELETE FROM spaces WHERE id = ?", (space_id,))
        flash('Пространство успешно удалено', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении пространства: {str(e)}', 'error')
    return redirect(url_for('admin.manage_spaces'))


@admin_bp.route('/categories')
def manage_categories():
    categories = Database().execute("SELECT id, name FROM categories")
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/create', methods=['POST'])
def create_category():
    name = request.form.get('name')
    if not name:
        flash('Название категории обязательно', 'error')
        return redirect(url_for('admin.manage_categories'))

    try:
        Database().execute("INSERT INTO categories (name) VALUES (?)", (name,))
        flash('Категория успешно создана', 'success')
    except sqlite3.IntegrityError:
        flash('Категория с таким названием уже существует', 'error')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/users/search')
def search_users():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('admin.manage_users'))

    users = Database().execute(
        """SELECT id, email, full_name, number_phone, is_admin, is_banned
           FROM users 
           WHERE email LIKE ? OR full_name LIKE ? OR number_phone LIKE ?
           ORDER BY full_name""",
        (f'%{query}%', f'%{query}%', f'%{query}%')
    )
    return render_template('admin/users.html', users=users, search_query=query)
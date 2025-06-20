from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from backend.database.models.user import User
from backend.database.db import Database
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or not g.user.get('is_admin'):
            flash('Доступ запрещен: требуются права администратора', 'error')
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

    # Получаем статистику
    users_count = db.execute("SELECT COUNT(*) FROM users", fetch_one=True)[0]
    spaces_count = db.execute("SELECT COUNT(*) FROM spaces", fetch_one=True)[0]
    bookings_count = db.execute("SELECT COUNT(*) FROM bookings", fetch_one=True)[0]

    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           spaces_count=spaces_count,
                           bookings_count=bookings_count)

@admin_bp.route('/users')
def manage_users():
    user_model = User()
    users = user_model.db.execute(
        """SELECT id, email, full_name, number_phone, is_admin, 
           strftime('%d.%m.%Y %H:%M', created_at) 
           FROM users ORDER BY created_at DESC"""
    )
    return render_template('admin/users.html', users=users)


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

import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from backend.database.models.user import User
from backend.database.db import Database
from functools import wraps

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/master')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_model = User()
        if not g.user or not user_model.is_admin(g.user['id']):
            flash('Доступ запрещен: требуются права администратора', 'error')
            return redirect(url_for('index'))
        user_model.update_activity(g.user['id'])
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.before_request
@admin_required
def before_request():
    pass


def get_activity_filter_query(activity):
    today = datetime.now().date()
    queries = {
        'week': (today - timedelta(days=7)),
        'month': (today - timedelta(days=30)),
        'half_year': (today - timedelta(days=180)),
        'year': (today - timedelta(days=365)),
    }

    if activity == 'active_week':
        return "AND last_activity >= ?", [queries['week']]
    elif activity == 'active_month':
        return "AND last_activity >= ?", [queries['month']]
    elif activity == 'active_half_year':
        return "AND last_activity >= ?", [queries['half_year']]
    elif activity == 'active_year':
        return "AND last_activity >= ?", [queries['year']]
    elif activity == 'inactive_year':
        return "AND last_activity < ?", [queries['year']]
    return "", []


@admin_bp.route('/')
def dashboard():
    db = Database()

    stats = {
        'users': {
            'total': db.execute("SELECT COUNT(*) FROM users", fetch_one=True)[0],
            'active':
                db.execute("SELECT COUNT(*) FROM users WHERE last_activity >= date('now', '-30 day')", fetch_one=True)[
                    0],
            'new': db.execute("SELECT COUNT(*) FROM users WHERE created_at >= date('now', '-7 day')", fetch_one=True)[
                0],
        },
        'spaces': {
            'total': db.execute("SELECT COUNT(*) FROM spaces", fetch_one=True)[0],
            'popular': db.execute("""
                SELECT s.name, COUNT(b.id) as bookings 
                FROM spaces s
                LEFT JOIN bookings b ON s.id = b.space_id 
                WHERE b.booking_date >= date('now', '-30 day')
                GROUP BY s.id 
                ORDER BY bookings DESC 
                LIMIT 5
            """)
        },
        'bookings': {
            'total': db.execute("SELECT COUNT(*) FROM bookings", fetch_one=True)[0],
            'upcoming': db.execute("SELECT COUNT(*) FROM bookings WHERE booking_date >= date('now')", fetch_one=True)[
                0],
            'categories': db.execute("""
                SELECT c.name, COUNT(b.id) 
                FROM categories c
                JOIN spaces s ON c.id = s.category_id
                JOIN bookings b ON s.id = b.space_id
                WHERE b.booking_date >= date('now', '-30 day')
                GROUP BY c.id
            """)
        }
    }

    return render_template('master/master.html', stats=stats)


@admin_bp.route('/users')
def manage_users():
    user_model = User()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    status = request.args.getlist('status')
    activity = request.args.get('activity')
    search = request.args.get('search', '').strip()

    base_query = """
        SELECT u.id, u.email, u.full_name, u.number_phone, u.is_admin, u.is_banned,
               strftime('%d.%m.%Y %H:%M', u.created_at) as created_at,
               (SELECT COUNT(*) FROM bookings b WHERE b.user_id = u.id) as bookings_count,
               MAX(b.booking_date) as last_booking
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
    """

    conditions = []
    params = []

    if search:
        conditions.append("(u.email LIKE ? OR u.full_name LIKE ? OR u.number_phone LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    if status:
        status_conditions = []
        if 'admin' in status:
            status_conditions.append("u.is_admin = 1")
        if 'user' in status:
            status_conditions.append("u.is_admin = 0")
        if 'banned' in status:
            status_conditions.append("u.is_banned = 1")
        if status_conditions:
            conditions.append(f"({' OR '.join(status_conditions)})")

    if activity:
        activity_query, activity_params = get_activity_filter_query(activity)
        if activity_query:
            conditions.append(activity_query)
            params.extend(activity_params)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    group_by = "GROUP BY u.id"
    order_by = "ORDER BY u.created_at DESC"
    limit = f"LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    query = f"{base_query} {where_clause} {group_by} {order_by} {limit}"

    users = user_model.db.execute(query, tuple(params))
    total_users = \
    user_model.db.execute(f"SELECT COUNT(*) FROM users {where_clause}", tuple(params[:-2]), fetch_one=True)[0]

    return render_template('master/users.html',
                           users=users,
                           page=page,
                           per_page=per_page,
                           total_users=total_users,
                           current_filters={
                               'status': status,
                               'activity': activity,
                               'search': search
                           })


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    user_model = User()
    try:
        current_status = user_model.is_admin(user_id)
        user_model.make_admin(user_id) if not current_status else user_model.revoke_admin(user_id)
        return jsonify({'success': True, 'is_admin': not current_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/users/<int:user_id>/toggle-ban', methods=['POST'])
def toggle_ban(user_id):
    user_model = User()
    try:
        current_status = user_model.get_banned_status(user_id)
        user_model.db.execute(
            "UPDATE users SET is_banned = ? WHERE id = ?",
            (not current_status, user_id)
        )
        return jsonify({'success': True, 'is_banned': not current_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/users/<int:user_id>/bookings')
def get_user_bookings(user_id):
    user_model = User()
    bookings = user_model.db.execute(
        """SELECT b.id, s.name, s.id as space_id,
           strftime('%d.%m.%Y', b.booking_date) as date,
           strftime('%H:%M', b.start_time) || '-' || strftime('%H:%M', b.end_time) as time,
           b.comment, b.booking_date >= date('now') as is_upcoming
           FROM bookings b
           JOIN spaces s ON b.space_id = s.id
           WHERE b.user_id = ?
           ORDER BY b.booking_date DESC""",
        (user_id,)
    )
    return jsonify([{
        'id': b[0],
        'space_name': b[1],
        'space_id': b[2],
        'date': b[3],
        'time': b[4],
        'comment': b[5],
        'is_upcoming': bool(b[6]),
        'can_cancel': b[6]
    } for b in bookings])


@admin_bp.route('/spaces')
def manage_spaces():
    db = Database()

    category = request.args.get('category')
    building = request.args.get('building')
    features = request.args.getlist('feature')

    query = """
        SELECT s.id, s.name, c.name as category, s.building, s.level,
               (SELECT COUNT(*) FROM bookings WHERE space_id = s.id AND booking_date >= date('now', '-30 day')) as recent_bookings,
               (SELECT COUNT(*) FROM user_favorites WHERE space_id = s.id) as favorites,
               GROUP_CONCAT(sf.feature) as features
        FROM spaces s
        JOIN categories c ON s.category_id = c.id
        LEFT JOIN space_features sf ON s.id = sf.space_id
    """

    conditions = []
    params = []

    if category:
        conditions.append("c.name = ?")
        params.append(category)

    if building:
        conditions.append("s.building = ?")
        params.append(building)

    if features:
        feature_conditions = []
        for feature in features:
            feature_conditions.append("EXISTS (SELECT 1 FROM space_features WHERE space_id = s.id AND feature = ?)")
            params.append(feature)
        conditions.append(f"({' AND '.join(feature_conditions)})")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY s.id ORDER BY recent_bookings DESC"

    spaces = db.execute(query, tuple(params))
    categories = db.execute("SELECT name FROM categories")

    return render_template('master/spaces.html',
                           spaces=spaces,
                           categories=categories,
                           current_filters={
                               'category': category,
                               'building': building,
                               'features': features
                           })


@admin_bp.route('/space/<int:space_id>')
def space_detail(space_id):
    db = Database()

    space = db.execute(
        """SELECT s.*, c.name as category_name,
           (SELECT GROUP_CONCAT(feature) FROM space_features WHERE space_id = s.id) as features,
           (SELECT image_url FROM space_images WHERE space_id = s.id AND is_primary = 1 LIMIT 1) as primary_image
           FROM spaces s
           JOIN categories c ON s.category_id = c.id
           WHERE s.id = ?""",
        (space_id,),
        fetch_one=True
    )

    if not space:
        flash('Пространство не найдено', 'error')
        return redirect(url_for('admin_bp.manage_spaces'))

    images = db.execute(
        "SELECT id, image_url, alt_text, is_primary FROM space_images WHERE space_id = ? ORDER BY is_primary DESC",
        (space_id,)
    )

    bookings = db.execute(
        """SELECT b.id, u.email, u.full_name, 
           strftime('%d.%m.%Y', b.booking_date) as date,
           strftime('%H:%M', b.start_time) || '-' || strftime('%H:%M', b.end_time) as time
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           WHERE b.space_id = ? AND b.booking_date >= date('now')
           ORDER BY b.booking_date, b.start_time""",
        (space_id,)
    )

    return render_template('master/space.html',
                           space=space,
                           images=images,
                           bookings=bookings)


@admin_bp.route('/space/<int:space_id>/update', methods=['POST'])
def update_space(space_id):
    try:
        data = request.form
        db = Database()
        db.execute(
            """UPDATE spaces SET 
               name = ?, building = ?, level = ?, location = ?,
               description = ?, location_description = ?, map_url = ?,
               category_id = (SELECT id FROM categories WHERE name = ?)
               WHERE id = ?""",
            (data['name'], data['building'], data['level'], data['location'],
             data['description'], data['location_description'], data['map_url'],
             data['category'], space_id)
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/space/<int:space_id>/delete', methods=['POST'])
def delete_space(space_id):
    try:
        db = Database()
        db.execute("DELETE FROM spaces WHERE id = ?", (space_id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/categories')
def manage_categories():
    categories = Database().execute("SELECT id, name FROM categories")
    return render_template('categories.html', categories=categories)


@admin_bp.route('/categories/create', methods=['POST'])
def create_category():
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'success': False, 'error': 'Название категории обязательно'}), 400

        Database().execute("INSERT INTO categories (name) VALUES (?)", (name,))
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Категория с таким названием уже существует'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
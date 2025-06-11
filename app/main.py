from flask import Flask, render_template, g, session, jsonify, request

from backend.database.db import Database
import os

from backend.database.models.booking import Booking
from backend.database.models.space import Space
from backend.database.models.user import User
from backend.routes.register import auth_bp, login_required


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_fallback_key')
app.config['DATABASE'] = os.path.join('instance', 'app.db')

os.makedirs('instance', exist_ok=True)
app.register_blueprint(auth_bp, url_prefix='/auth')

with app.app_context():
    db = Database(app.config['DATABASE'])
    db._init_db()

@app.before_request
def get_global_vars():
    g.user = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/space/<int:id>')
def space(id):
    space_model = Space()
    space_data = db.execute(
        """SELECT s.*, c.name AS category_name 
           FROM spaces s JOIN categories c ON s.category_id = c.id 
           WHERE s.id = ?""",
        (id,),
        fetch_one=True
    )

    if not space_data:
        return "Space not found", 404

    columns = ['id', 'name', 'building', 'level', 'location', 'description',
               'image1', 'image2', 'image3', 'location_description', 'likes', 'map_url', 'category_name']
    space_dict = dict(zip(columns, space_data))
    space_dict['features'] = space_model.get_space_features(id)

    if 'user_id' in session:
        space_dict['is_favorite'] = space_model.is_favorite(session['user_id'], id)
    else:
        space_dict['is_favorite'] = False

    return render_template('spaces/space_card.html', space=space_dict)


@app.route('/catalog')
def catalog():
    space_model = Space()
    categories = db.execute("SELECT * FROM categories")

    space_categories = []
    for cat in categories:
        spaces = space_model.get_by_category(cat[0])
        enriched_spaces = []
        for space in spaces:
            is_fav = False
            if 'user_id' in session:
                is_fav = space_model.is_favorite(session['user_id'], space['id'])
            enriched_spaces.append({**space, 'is_favorite': is_fav})

        space_categories.append({
            "id": cat[0],
            "name": cat[1],
            "spaces": enriched_spaces
        })

    return render_template('spaces/catalog.html', space_categories=space_categories)


@app.route('/catalog/filter')
def filtered_catalog():
    activity = request.args.get('activity', '')
    building = request.args.get('building', '')
    features = request.args.get('features', '').split(',') if request.args.get('features') else []

    space_model = Space()

    if not activity and not building and not features:
        categories = db.execute("SELECT * FROM categories")
        space_categories = []
        for cat in categories:
            spaces = space_model.get_by_category(cat[0])
            space_categories.append({
                "id": cat[0],
                "name": cat[1],
                "spaces": spaces
            })
        return jsonify(space_categories)

    category_id = None
    if activity == 'dancing':
        category_id = 1
    elif activity == 'studying':
        category_id = 2
    elif activity == 'event':
        category_id = 3

    spaces = space_model.get_filtered_spaces(
        category_id=category_id,
        building=building if building else None,
        features=features if features else None
    )

    return jsonify(spaces)


@app.route('/favorites')
@login_required
def favorites():
    space_model = Space()
    spaces = space_model.get_favorites(session['user_id'])

    return render_template('spaces/favorites.html', favorites={
        "spaces": spaces
    })


@app.route('/api/favorites', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        space_id = data.get('space_id')
        user_id = session.get('user_id')

        if not space_id or not user_id:
            return jsonify({'error': 'Missing parameters'}), 400

        space_model = Space()

        if space_model.is_favorite(user_id, space_id):
            space_model.remove_from_favorites(user_id, space_id)
            return jsonify({'status': 'removed'})
        else:
            space_model.add_to_favorites(user_id, space_id)
            return jsonify({'status': 'added'})

    except Exception as e:
        print(f"Error in toggle_favorite: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/favorites/check/<int:space_id>')
@login_required
def check_favorite(space_id):
    user_id = session['user_id']
    space_model = Space()
    is_fav = space_model.is_favorite(user_id, space_id)
    return jsonify({'is_favorite': is_fav})

@app.route('/auth')
def auth():
    return render_template('auth/auth.html')

@app.before_request
def get_global_vars():
    user_id = session.get('user_id')
    if user_id is not None:
        user = User()
        user_data = user.get_user_data(user_id)
        if user_data:
            g.user = {
                'id': user_id,
                'email': user_data[0],
                'full_name': user_data[1],
                'number_phone': user_data[2],
                'image_src': user_data[3] if len(user_data) > 3 else None
            }
    else:
        g.user = None


@app.route('/book', methods=['POST'])
@login_required
def book_space():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400

        required_fields = ['space_id', 'booking_date', 'start_time', 'end_time']
        if any(field not in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return jsonify({'error': f'Отсутствуют обязательные поля: {", ".join(missing)}'}), 400

        try:
            space_id = int(data['space_id'])
        except:
            return jsonify({'error': 'Неверный ID пространства'}), 400

        booking_model = Booking()
        success, message = booking_model.create_booking(
            session['user_id'],
            space_id,
            data['booking_date'],
            data['start_time'],
            data['end_time'],
            data.get('comment')
        )

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': message})

    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


@app.route('/api/availability/<int:space_id>')
def get_availability(space_id):
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    booking_model = Booking()
    bookings = booking_model.get_space_availability(space_id, date)

    booked_slots = [{'start': booking[0], 'end': booking[1]} for booking in bookings]
    return jsonify({'booked_slots': booked_slots})


@app.route('/my-bookings')
@login_required
def my_bookings():
    booking_model = Booking()
    bookings = booking_model.get_user_bookings(session['user_id'])
    return render_template('bookings/my_bookings.html', bookings=bookings)


@app.route('/profile')
@login_required
def profile():
    user = User()
    booking_model = Booking()

    user_data = user.db.execute(
        "SELECT email, full_name, number_phone FROM users WHERE id = ?",
        (session['user_id'],),
        fetch_one=True
    )

    bookings = booking_model.get_user_bookings(session['user_id'])

    return render_template('auth/profile.html',
                           user={
                               'email': user_data[0],
                               'full_name': user_data[1],
                               'number': user_data[2]
                           },
                           bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
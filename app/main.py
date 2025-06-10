from flask import Flask, render_template, g, session, jsonify, request
from backend.database.db import Database
import os

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

    space_data['features'] = space_model.get_space_features(id)
    return render_template('spaces/space_card.html', space=space_data)


@app.route('/catalog')
def catalog():
    space_model = Space()
    categories = db.execute("SELECT * FROM categories")

    space_categories = []
    for cat in categories:
        spaces = space_model.get_by_category(cat[0])
        space_categories.append({
            "id": cat[0],
            "name": cat[1],
            "spaces": spaces
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

@app.route('/profile')
@login_required
def profile():
    user = User()
    user_data = user.db.execute(
        "SELECT email, full_name, number_phone FROM users WHERE id = ?",
        (session['user_id'],),
        fetch_one=True
    )

    return render_template('auth/profile.html',
                           user={
                               'email': user_data[0],
                               'full_name': user_data[1],
                               'number': user_data[2]
                           })

if __name__ == '__main__':
    app.run(debug=True)
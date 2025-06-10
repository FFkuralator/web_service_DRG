from flask import Flask, render_template, g, session
from backend.database.db import Database
import os

from backend.database.models.user import User
from backend.routes.register import auth_bp, login_required

# delete later
all_spaces = [
    {
        "id": 1,
        "name": "Танцы",
        "spaces": [
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },

        ]
    },
    {
        "id": 1,
        "name": "Не танцы",
        "spaces": [
            {
                "id": 3,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            },
            {
                "id": 4,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/portrait.png",
                "image_alt": "",
            }

        ]
    },
]

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
    return render_template('spaces/space_card.html', space=all_spaces[0]["spaces"][0])

@app.route('/catalog')
def catalog():
    return render_template('spaces/catalog.html', space_categories=all_spaces, category=all_spaces[0])

@app.route('/favorites')
def favorites():
    return render_template('spaces/favorites.html', favorites=all_spaces[0])

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
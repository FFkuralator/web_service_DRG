from flask import Flask, render_template, g
from backend.database.db import Database
import os

from backend.routes.register import auth_bp

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
                "image_src": "assets/image.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/image.png",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/image.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/image.png",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/image.png",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/image.png",
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
                "image_src": "assets/ne_diana.jpg",
                "image_alt": "",
            },
            {
                "id": 4,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/ne_diana.jpg",
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

@app.route('/profile')
def profile():
    return render_template('auth/profile.html', user={
        "username": "loh",
        "email": "asdkkl@aksld",
        "number": 19283289,
        "avatar_src": "assets/image.png"},
        booking_history=[
            {
                "name": "hui",
                "date": "20.03.2006 10:50-12:30",
                "vote": "up"
            }
        ]
        )

if __name__ == '__main__':
    app.run(debug=True)
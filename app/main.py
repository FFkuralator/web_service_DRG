from flask import Flask, render_template
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
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "",
                "image_alt": "",
            },
            {
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "",
                "image_alt": "",
            }

        ]
    },
    {
        "id": 1,
        "name": "Не танцы",
        "spaces": [
            {
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "",
                "image_alt": "",
            },
            {
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "",
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/space')
def space():
    return render_template('spaces/space_card.html')

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
        "avatar_src": "12"},
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
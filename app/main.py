from flask import Flask, render_template
import os

from backend.routes.register import auth_bp

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

app.register_blueprint(auth_bp)

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
    return render_template('auth/profile.html')

if __name__ == '__main__':
    app.run(debug=True)
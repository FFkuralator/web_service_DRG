from flask import Flask, render_template, session
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
                "image_src": "assets/diana1.jpeg",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/diana2.jpeg",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/diana3.jpeg",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/diana4.jpeg",
                "image_alt": "",
            },
            {
                "id": 1,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/dmitry.jpeg",
                "image_alt": "",
            },
            {
                "id": 2,
                "name": "Пространство",
                "building": "A",
                "level": 6,
                "location": "A666",
                "description": "Lorem ipsum dolores sit ame",
                "image_src": "assets/ivan.jpeg",
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

db = Database(app.config['DATABASE'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/space/<int:space_id>')
def space(space_id: int):
    space_data = db.execute(
        "SELECT * FROM spaces WHERE id = ?",
        (space_id,),
        fetch_one=True
    )
    if not space_data:
        return render_template('errors/404.html'), 404
    return render_template('spaces/space_card.html', space=space_data)

@app.route('/catalog')
def catalog():
    categories = db.execute(
        """SELECT c.id, c.name, 
           (SELECT COUNT(*) FROM spaces WHERE category_id = c.id) 
           FROM categories c"""
    )
    return render_template('spaces/catalog.html', categories=categories)

@app.route('/favorites')
@login_required
def favorites():
    favorites = db.execute(
        """SELECT s.* FROM spaces s
           JOIN user_favorites uf ON s.id = uf.space_id
           WHERE uf.user_id = ?""",
        (session['user_id'],)
    )
    return render_template('spaces/favorites.html', favorites=favorites)

@app.route('/auth')
def auth():
    return render_template('auth/auth.html')


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
    db = Database('instance/app.db')
    db.add_test_data()  # Тесттт
    app.run(debug=True)
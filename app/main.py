import logging
from flask import Flask, render_template, g, session
import os
from backend.database.db import Database
from backend.database.models.user import User
from backend.routes import spaces_bp, bookings_bp, favorites_bp, images_bp, profile_bp, admin_bp
from backend.routes.register import auth_bp

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_fallback_key')
app.config['DATABASE'] = os.path.join('instance', 'app.db')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/assets'
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
os.makedirs('instance', exist_ok=True)

app.register_blueprint(spaces_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(favorites_bp)
app.register_blueprint(images_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)

with app.app_context():
    db = Database(app.config['DATABASE'])
    db._init_db()
    app.extensions['db'] = db

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template
import os

from backend.routes.register import auth_bp


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_fallback_key')
app.config['DATABASE'] = os.path.join('instance', 'app.db')

os.makedirs('instance', exist_ok=True)

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
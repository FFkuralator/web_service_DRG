from api import create_app
from api.extensions import db

app = create_app()

@app.route('/')
def register():
    return '<h1>io</h1>'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
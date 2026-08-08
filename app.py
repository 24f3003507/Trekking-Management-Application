# Starting of the app
from flask import Flask
from backend.models import db
from backend.controllers import auth_bp

app = None

def setup_app():
    global app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite3"
    app.config["SECRET_KEY"] = "your-secret-key"
    db.init_app(app)
    app.register_blueprint(auth_bp)
    with app.app_context():
        db.create_all()
    app.debug = True
    print("Trekking app is started...")

setup_app()

if __name__ == "__main__":
    app.run(port=5003)
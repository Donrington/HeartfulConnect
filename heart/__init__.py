from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

from heart.models import db

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_pyfile("config.py", silent=True)
    db.init_app(app)
    migrate = Migrate(app,db)
    socketio = SocketIO(app)
    csrf.init_app(app)
    return app, socketio
app, socketio = create_app()

from heart.routes import user_bp,therapist_bp

app.register_blueprint(user_bp, url_prefix='/user')

# Register the therapist Blueprint with the app
app.register_blueprint(therapist_bp, url_prefix='/therapist')



from heart import admin_routes, user_routes, thera_routes













from heart import admin_routes, user_routes
from heart.forms import *
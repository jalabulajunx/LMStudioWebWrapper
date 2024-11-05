# server/__init__.py

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import get_config

socketio = SocketIO()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize extensions
    from .database import init_db, User  # Import User model
    init_db(app)
    socketio.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .auth import auth_bp
    from .chat import chat_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    # Add root route
    from flask import redirect, url_for
    from flask_login import current_user

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('chat.index'))
        return redirect(url_for('auth.login'))

    return app

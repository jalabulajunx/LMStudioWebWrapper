# server/app.py

from flask import Flask, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO
from .database import init_db
from .auth import auth_bp
from .chat import chat_bp

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object or dictionary
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        app.config.from_object('config.settings')
    
    # Initialize extensions
    socketio = SocketIO(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app, socketio

# run.py
if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

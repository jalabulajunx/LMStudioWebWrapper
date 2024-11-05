# server/database.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    """User model for authentication and session management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    chats = db.relationship('Chat', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chat(db.Model):
    """Chat model for storing conversation history"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)
    chat_type = db.Column(db.String(20), default='general')  # 'general' or 'music'
    
    def rename(self, new_title):
        self.title = new_title
        db.session.commit()

class Message(db.Model):
    """Message model for storing individual messages in a chat"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_user = db.Column(db.Boolean, default=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

class MusicDatabase(db.Model):
    """Music database model for storing music information"""
    id = db.Column(db.Integer, primary_key=True)
    album = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    composer = db.Column(db.String(200))
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))

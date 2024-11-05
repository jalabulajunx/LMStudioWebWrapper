# server/auth.py

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .database import db, User

auth_bp = Blueprint('auth', __name__)

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class AuthManager:
    """Handles user authentication operations"""
    
    @staticmethod
    def create_user(username, password):
        """
        Create a new user.
        
        Args:
            username (str): The username for the new user
            password (str): The password for the new user
            
        Returns:
            User: The created user object
            
        Raises:
            AuthenticationError: If username already exists
        """
        if User.query.filter_by(username=username).first():
            raise AuthenticationError('Username already exists')
            
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate a user.
        
        Args:
            username (str): The username to authenticate
            password (str): The password to verify
            
        Returns:
            User: The authenticated user object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise AuthenticationError('Invalid username or password')
        return user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = AuthManager.authenticate_user(username, password)
            login_user(user)
            return redirect(url_for('chat.index'))
        except AuthenticationError as e:
            flash(str(e), 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
            
        try:
            user = AuthManager.create_user(username, password)
            login_user(user)
            return redirect(url_for('chat.index'))
        except AuthenticationError as e:
            flash(str(e), 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('auth.login'))

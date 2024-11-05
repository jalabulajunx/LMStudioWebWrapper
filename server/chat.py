# server/chat.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from .database import db, Chat, Message
from .llm import LMStudioClient
from .music import MusicQueryProcessor

chat_bp = Blueprint('chat', __name__)
lm_client = LMStudioClient()
music_processor = MusicQueryProcessor()

class ChatManager:
    """Manages chat operations and message handling"""
    
    @staticmethod
    def create_chat(user_id, title=None, chat_type='general'):
        """
        Create a new chat session.
        
        Args:
            user_id (int): ID of the user creating the chat
            title (str, optional): Title of the chat
            chat_type (str): Type of chat ('general' or 'music')
            
        Returns:
            Chat: Created chat instance
        """
        if not title:
            title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
        chat = Chat(
            title=title,
            user_id=user_id,
            chat_type=chat_type
        )
        db.session.add(chat)
        db.session.commit()
        return chat
    
    @staticmethod
    def get_user_chats(user_id):
        """Get all chats for a user"""
        return Chat.query.filter_by(user_id=user_id).order_by(Chat.created_at.desc()).all()
    
    @staticmethod
    def get_chat(chat_id, user_id):
        """Get a specific chat if it belongs to the user"""
        return Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    @staticmethod
    def rename_chat(chat_id, user_id, new_title):
        """Rename a chat"""
        chat = ChatManager.get_chat(chat_id, user_id)
        if chat:
            chat.title = new_title
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_chat(chat_id, user_id):
        """Delete a chat and its messages"""
        chat = ChatManager.get_chat(chat_id, user_id)
        if chat:
            db.session.delete(chat)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def add_message(chat_id, content, is_user=True):
        """Add a message to a chat"""
        message = Message(
            chat_id=chat_id,
            content=content,
            is_user=is_user
        )
        db.session.add(message)
        db.session.commit()
        return message

@chat_bp.route('/chat')
@login_required
def index():
    """Render the main chat interface"""
    chats = ChatManager.get_user_chats(current_user.id)
    return render_template('chat/index.html', chats=chats)

@chat_bp.route('/api/chats', methods=['POST'])
@login_required
def create_chat():
    """API endpoint to create a new chat"""
    data = request.get_json()
    chat_type = data.get('type', 'general')
    chat = ChatManager.create_chat(current_user.id, chat_type=chat_type)
    return jsonify({
        'id': chat.id,
        'title': chat.title,
        'created_at': chat.created_at.isoformat()
    })

@chat_bp.route('/api/chats/<int:chat_id>/rename', methods=['POST'])
@login_required
def rename_chat(chat_id):
    """API endpoint to rename a chat"""
    data = request.get_json()
    new_title = data.get('title')
    if not new_title:
        return jsonify({'error': 'Title is required'}), 400
        
    success = ChatManager.rename_chat(chat_id, current_user.id, new_title)
    if success:
        return jsonify({'message': 'Chat renamed successfully'})
    return jsonify({'error': 'Chat not found'}), 404

@chat_bp.route('/api/chats/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """API endpoint to delete a chat"""
    success = ChatManager.delete_chat(chat_id, current_user.id)
    if success:
        return jsonify({'message': 'Chat deleted successfully'})
    return jsonify({'error': 'Chat not found'}), 404

@chat_bp.route('/api/chats/<int:chat_id>/messages')
@login_required
def get_messages(chat_id):
    """API endpoint to get chat messages"""
    chat = ChatManager.get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
        
    messages = [
        {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_user': msg.is_user
        }
        for msg in chat.messages
    ]
    return jsonify(messages)

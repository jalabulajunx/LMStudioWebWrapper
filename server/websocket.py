# server/websocket.py

from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
import asyncio
import threading
from .chat import ChatManager
from .llm import LMStudioClient
from .music import MusicQueryProcessor

class WebSocketHandler:
    """Handles WebSocket connections and message processing"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.lm_client = LMStudioClient()
        self.music_processor = MusicQueryProcessor()
        self.active_generations = set()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            if not current_user.is_authenticated:
                return False
            join_room(str(current_user.id))
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            if current_user.is_authenticated:
                leave_room(str(current_user.id))
        
        @self.socketio.on('join_chat')
        def handle_join_chat(data):
            """Handle user joining a specific chat room"""
            chat_id = data['chat_id']
            chat = ChatManager.get_chat(chat_id, current_user.id)
            if chat:
                join_room(f"chat_{chat_id}")
        
        @self.socketio.on('leave_chat')
        def handle_leave_chat(data):
            """Handle user leaving a specific chat room"""
            chat_id = data['chat_id']
            leave_room(f"chat_{chat_id}")
        
        @self.socketio.on('send_message')
        def handle_message(data):
            """Handle incoming chat messages"""
            chat_id = data['chat_id']
            content = data['content']
            chat_type = data['type']
            
            # Store user message
            message = ChatManager.add_message(chat_id, content, is_user=True)
            
            # Broadcast user message
            self._broadcast_message(chat_id, message)
            
            # Generate response
            threading.Thread(
                target=self._generate_response,
                args=(chat_id, content, chat_type)
            ).start()
        
        @self.socketio.on('stop_generation')
        def handle_stop_generation(data):
            """Handle request to stop response generation"""
            chat_id = data['chat_id']
            self.active_generations.discard(chat_id)
    
    def _broadcast_message(self, chat_id, message):
        """Broadcast message to chat room"""
        emit('new_message', {
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_user': message.is_user
        }, room=f"chat_{chat_id}")
    
    def _generate_response(self, chat_id, user_message, chat_type):
        """Generate and stream AI response"""
        self.active_generations.add(chat_id)
        
        try:
            if chat_type == 'music':
                # Handle music-related query
                sql_query = self.music_processor.generate_sql(user_message)
                results = self.music_processor.execute_query(sql_query)
                prompt = self.music_processor.format_results(results)
                response_stream = self.lm_client.generate_stream(prompt)
            else:
                # Handle general query
                response_stream = self.lm_client.generate_stream(user_message)
            
            # Initialize response message
            response_message = ChatManager.add_message(chat_id, "", is_user=False)
            accumulated_text = ""
            
            # Stream response
            for chunk in response_stream:
                if chat_id not in self.active_generations:
                    break
                    
                accumulated_text += chunk
                response_message.content = accumulated_text
                db.session.commit()
                
                emit('response_chunk', {
                    'chat_id': chat_id,
                    'message_id': response_message.id,
                    'chunk': chunk
                }, room=f"chat_{chat_id}")
            
            # Final update
            if chat_id in self.active_generations:
                response_message.content = accumulated_text
                db.session.commit()
                
                emit('response_complete', {
                    'chat_id': chat_id,
                    'message_id': response_message.id
                }, room=f"chat_{chat_id}")
        
        except Exception as e:
            emit('error', {
                'chat_id': chat_id,
                'error': str(e)
            }, room=f"chat_{chat_id}")
        
        finally:
            self.active_generations.discard(chat_id)

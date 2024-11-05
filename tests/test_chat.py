# tests/test_chat.py
import pytest
from server.chat import ChatManager

def test_create_chat(db, authenticated_user):
    """Test chat creation"""
    chat = ChatManager.create_chat(authenticated_user.id)
    assert chat.user_id == authenticated_user.id
    assert chat.chat_type == 'general'

def test_rename_chat(db, authenticated_user):
    """Test chat renaming"""
    chat = ChatManager.create_chat(authenticated_user.id)
    assert ChatManager.rename_chat(chat.id, authenticated_user.id, "New Title")
    assert chat.title == "New Title"

def test_delete_chat(db, authenticated_user):
    """Test chat deletion"""
    chat = ChatManager.create_chat(authenticated_user.id)
    assert ChatManager.delete_chat(chat.id, authenticated_user.id)
    assert ChatManager.get_chat(chat.id, authenticated_user.id) is None

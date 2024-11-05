// static/js/chat.js

class ChatApp {
    constructor() {
        this.socket = io();
        this.currentChatId = null;
        this.isGenerating = false;
        
        // Cache DOM elements
        this.elements = {
            messageForm: document.getElementById('message-form'),
            messageInput: document.getElementById('message-input'),
            messagesContainer: document.getElementById('messages'),
            newChatButton: document.getElementById('new-chat'),
            chatTypeSelect: document.getElementById('chat-type'),
            stopButton: document.getElementById('stop-generation'),
            chatList: document.querySelector('.chat-list'),
            renameModal: document.getElementById('rename-modal'),
            newChatTitleInput: document.getElementById('new-chat-title'),
            confirmRenameButton: document.getElementById('confirm-rename'),
            cancelRenameButton: document.getElementById('cancel-rename'),
            logoutButton: document.getElementById('logout')
        };
        
        this.setupEventListeners();
        this.setupSocketHandlers();
        
        // Load last active chat if exists
        const lastChatId = localStorage.getItem('lastChatId');
        if (lastChatId) {
            this.loadChat(lastChatId);
        }
    }
    
    setupEventListeners() {
        // Message form submission
        this.elements.messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // New chat creation
        this.elements.newChatButton.addEventListener('click', () => {
            this.createNewChat();
        });
        
        // Stop generation
        this.elements.stopButton.addEventListener('click', () => {
            this.stopGeneration();
        });
        
        // Chat item click handlers
        this.elements.chatList.addEventListener('click', (e) => {
            const chatItem = e.target.closest('.chat-item');
            if (!chatItem) return;
            
            if (e.target.closest('.rename-chat')) {
                this.showRenameModal(chatItem);
            } else if (e.target.closest('.delete-chat')) {
                this.deleteChat(chatItem.dataset.chatId);
            } else {
                this.loadChat(chatItem.dataset.chatId);
            }
        });
        
        // Rename modal handlers
        this.elements.confirmRenameButton.addEventListener('click', () => {
            this.renameChat();
        });
        
        this.elements.cancelRenameButton.addEventListener('click', () => {
            this.hideRenameModal();
        });
        
        // Logout handler
        this.elements.logoutButton.addEventListener('click', () => {
            window.location.href = '/logout';
        });
        
        // Auto-resize message input
        this.elements.messageInput.addEventListener('input', () => {
            this.elements.messageInput.style.height = 'auto';
            this.elements.messageInput.style.height = this.elements.messageInput.scrollHeight + 'px';
        });
    }
    
    setupSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        this.socket.on('new_message', (message) => {
            this.appendMessage(message);
        });
        
        this.socket.on('response_chunk', (data) => {
            if (data.chat_id === this.currentChatId) {
                this.updateStreamingMessage(data);
            }
        });
        
        this.socket.on('response_complete', (data) => {
            if (data.chat_id === this.currentChatId) {
                this.completeStreamingMessage(data);
            }
        });
        
        this.socket.on('error', (data) => {
            if (data.chat_id === this.currentChatId) {
                this.handleError(data.error);
            }
        });
    }
    
    async createNewChat() {
        try {
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: this.elements.chatTypeSelect.value
                })
            });
            
            const chat = await response.json();
            this.addChatToList(chat);
            this.loadChat(chat.id);
        } catch (error) {
            console.error('Error creating chat:', error);
        }
    }
    
    async loadChat(chatId) {
        try {
            const response = await fetch(`/api/chats/${chatId}/messages`);
            const messages = await response.json();
            
            this.currentChatId = chatId;
            localStorage.setItem('lastChatId', chatId);
            
            // Update UI
            this.updateActiveChatItem(chatId);
            this.elements.messagesContainer.innerHTML = '';
            messages.forEach(message => this.appendMessage(message));
            this.scrollToBottom();
            
            // Join chat room
            this.socket.emit('join_chat', { chat_id: chatId });
        } catch (error) {
            console.error('Error loading chat:', error);
        }
    }
    
    async renameChat() {
        const chatId = this.elements.renameModal.dataset.chatId;
        const newTitle = this.elements.newChatTitleInput.value.trim();
        
        if (!newTitle) return;
        
        try {
            const response = await fetch(`/api/chats/${chatId}/rename`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: newTitle })
            });
            
            if (response.ok) {
                const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
                chatItem.querySelector('.chat-item-title').textContent = newTitle;
                this.hideRenameModal();
            }
        } catch (error) {
            console.error('Error renaming chat:', error);
        }
    }
    
    async deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;
        
        try {
            const response = await fetch(`/api/chats/${chatId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
                chatItem.remove();
                
                if (this.currentChatId === chatId) {
                    this.currentChatId = null;
                    this.elements.messagesContainer.innerHTML = '';
                    localStorage.removeItem('lastChatId');
                }
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
        }
    }
    
    sendMessage() {
        const content = this.elements.messageInput.value.trim();
        if (!content || !this.currentChatId) return;
        
        this.socket.emit('send_message', {
            chat_id: this.currentChatId,
            content: content,
            type: this.elements.chatTypeSelect.value
        });
        
        this.elements.messageInput.value = '';
        this.elements.messageInput.style.height = 'auto';
        this.isGenerating = true;
        this.updateGeneratingUI(true);
    }
    
    stopGeneration() {
        if (this.isGenerating) {
            this.socket.emit('stop_generation', {
                chat_id: this.currentChatId
            });
            this.isGenerating = false;
            this.updateGeneratingUI(false);
        }
    }
    
    appendMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.is_user ? 'user' : 'assistant'}`;
        messageElement.dataset.messageId = message.id;
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = message.content;
        
        const timestampElement = document.createElement('div');
        timestampElement.className = 'message-timestamp';
        timestampElement.textContent = new Date(message.timestamp).toLocaleTimeString();
        
        messageElement.appendChild(contentElement);
        messageElement.appendChild(timestampElement);
        
        this.elements.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    updateStreamingMessage(data) {
        const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
        if (messageElement) {
            const contentElement = messageElement.querySelector('.message-content');
            contentElement.textContent += data.chunk;
            this.scrollToBottom();
        }
    }
    
    completeStreamingMessage(data) {
        this.isGenerating = false;
        this.updateGeneratingUI(false);
    }
    
    updateGeneratingUI(isGenerating) {
        this.elements.stopButton.style.display = isGenerating ? 'block' : 'none';
        this.elements.messageInput.disabled = isGenerating;
    }
    
    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    }
    
    showRenameModal(chatItem) {
        this.elements.renameModal.dataset.chatId = chatItem.dataset.chatId;
        this.elements.newChatTitleInput.value = chatItem.querySelector('.chat-item-title').textContent;
        this.elements.renameModal.style.display = 'block';
    }
    
    hideRenameModal() {
        this.elements.renameModal.style.display = 'none';
        this.elements.newChatTitleInput.value = '';
        delete this.elements.renameModal.dataset.chatId;
    }
    
    updateActiveChatItem(chatId) {
        const chatItems = document.querySelectorAll('.chat-item');
        chatItems.forEach(item => {
            item.classList.toggle('active', item.dataset.chatId === chatId);
        });
    }
    
handleError(error) {
        console.error('Server error:', error);
        this.isGenerating = false;
        this.updateGeneratingUI(false);

        // Add error message to chat
        const errorMessage = {
            id: Date.now(),
            content: `Error: ${error}`,
            timestamp: new Date().toISOString(),
            is_user: false
        };
        this.appendMessage(errorMessage);
    }

    addChatToList(chat) {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.chatId = chat.id;

        chatItem.innerHTML = `
            <div class="chat-item-title">${chat.title}</div>
            <div class="chat-item-actions">
                <button class="rename-chat" title="Rename">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="delete-chat" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        this.elements.chatList.insertBefore(chatItem, this.elements.chatList.firstChild);
    }
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

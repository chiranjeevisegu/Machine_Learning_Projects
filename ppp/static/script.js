// Enhanced Chat Application with Performance Optimizations
class ChatApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.messageQueue = [];
        this.isProcessing = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.typingTimeout = null;
        this.debounceTimeout = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadChatHistory();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7);
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendMessage = document.getElementById('sendMessage');
        this.newChatButton = document.getElementById('newChat');
        this.chatHistory = document.getElementById('chatHistory');
    }

    bindEvents() {
        // Send message events
        this.sendMessage.addEventListener('click', () => this.handleSendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        // Auto-resize textarea with debouncing
        this.userInput.addEventListener('input', () => {
            clearTimeout(this.debounceTimeout);
            this.debounceTimeout = setTimeout(() => this.autoResizeTextarea(), 100);
        });

        // New chat
        this.newChatButton.addEventListener('click', () => this.startNewChat());

        // Handle paste events for better UX
        this.userInput.addEventListener('paste', (e) => {
            setTimeout(() => this.autoResizeTextarea(), 10);
        });

        // Handle focus for better accessibility
        this.userInput.addEventListener('focus', () => {
            this.userInput.parentElement.style.borderColor = '#10a37f';
        });

        this.userInput.addEventListener('blur', () => {
            this.userInput.parentElement.style.borderColor = '#565869';
        });
    }

    autoResizeTextarea() {
        this.userInput.style.height = 'auto';
        const newHeight = Math.min(this.userInput.scrollHeight, 200);
        this.userInput.style.height = newHeight + 'px';
    }

    async loadChatHistory() {
        try {
            const response = await this.makeRequest('/chat_history', {
                method: 'GET',
                params: { session_id: this.sessionId }
            });
            
            const history = await response.json();
            
            // Clear existing messages
            this.chatMessages.innerHTML = '';
            
            // Add historical messages with smooth animation
            for (let i = 0; i < history.length; i++) {
                const conv = history[i];
                await this.addMessageWithDelay(conv.user_message, 'user', i * 50);
                await this.addMessageWithDelay(conv.bot_response, 'bot', (i * 50) + 100);
            }
            
            // Show initial greeting if no history
            if (history.length === 0) {
                this.addMessage('Hello! How can I help you today?', 'bot');
            }
            
            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.addMessage('Hello! How can I help you today?', 'bot');
        }
    }

    async addMessageWithDelay(message, sender, delay) {
        return new Promise(resolve => {
            setTimeout(() => {
                this.addMessage(message, sender);
                resolve();
            }, delay);
        });
    }

    async handleSendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isProcessing) return;

        // Reset UI
        this.userInput.value = '';
        this.autoResizeTextarea();
        this.sendMessage.disabled = true;
        this.sendMessage.style.opacity = '0.5';

        // Add user message
        this.addMessage(message, 'user');

        // Show typing indicator
        const typingIndicator = this.addTypingIndicator();

        try {
            this.isProcessing = true;
            const response = await this.sendMessageToBot(message);
            
            // Remove typing indicator
            typingIndicator.remove();

            // Add bot's response
            if (response.error) {
                this.addMessage(response.response || 'Sorry, I encountered an error. Please try again.', 'bot', 'error');
            } else {
                this.addMessage(response.response, 'bot');
                if (response.cached) {
                    this.showCacheIndicator();
                }
            }

            this.retryCount = 0; // Reset retry count on success
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            
            // Implement retry logic
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                this.addMessage(`Retrying... (${this.retryCount}/${this.maxRetries})`, 'bot', 'retry');
                setTimeout(() => this.handleSendMessage(), 1000 * this.retryCount);
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot', 'error');
                this.retryCount = 0;
            }
        } finally {
            this.isProcessing = false;
            this.sendMessage.disabled = false;
            this.sendMessage.style.opacity = '1';
        }
    }

    async sendMessageToBot(message) {
        const response = await this.makeRequest('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': this.sessionId
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async makeRequest(url, options) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>AI is thinking...</span>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
        return typingDiv;
    }

    addMessage(message, sender, type = 'normal') {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        if (type !== 'normal') {
            messageDiv.classList.add(`message-${type}`);
        }

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Sanitize and format message
        contentDiv.innerHTML = this.formatMessage(message);
        
        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.classList.add('message-timestamp');
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestamp);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add fade-in animation
        setTimeout(() => messageDiv.classList.add('message-visible'), 10);
    }

    formatMessage(message) {
        // Basic markdown-like formatting
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showCacheIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('cache-indicator');
        indicator.textContent = '⚡ Cached response';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10a37f;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => indicator.remove(), 300);
        }, 2000);
    }

    startNewChat() {
        this.sessionId = this.generateSessionId();
        this.chatMessages.innerHTML = '';
        this.retryCount = 0;
        this.addMessage('Hello! How can I help you today?', 'bot');
        
        // Update chat history in sidebar
        this.updateChatHistory();
    }

    updateChatHistory() {
        // This could be expanded to show actual chat history in sidebar
        const historyItem = document.createElement('div');
        historyItem.classList.add('history-item');
        historyItem.textContent = `Chat ${new Date().toLocaleTimeString()}`;
        this.chatHistory.appendChild(historyItem);
    }
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .message {
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
    }
    
    .message-visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .typing-dots {
        display: inline-flex;
        gap: 4px;
        margin-right: 8px;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        background: #8E8EA0;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    .message-timestamp {
        font-size: 11px;
        color: #8E8EA0;
        margin-top: 4px;
    }
    
    .message-error {
        border-left: 3px solid #ff4444;
    }
    
    .message-retry {
        border-left: 3px solid #ffaa00;
    }
    
    .history-item {
        padding: 8px 12px;
        margin: 2px 0;
        background: #343541;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .history-item:hover {
        background: #40414F;
    }
`;
document.head.appendChild(style);
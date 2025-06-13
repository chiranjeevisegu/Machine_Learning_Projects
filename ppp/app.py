from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import os
import logging
from functools import wraps
import time
import threading
from collections import defaultdict
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCbWtjx2aaFYixR5QMG_93Bxf_pRlW74xk')
    MAX_HISTORY_FILES = int(os.getenv('MAX_HISTORY_FILES', 100))
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 4000))
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))

# Configure the API key
genai.configure(api_key=Config.GEMINI_API_KEY)

# Enhanced model configuration
genai_model_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 40,
    "max_output_tokens": 2048,
    "candidate_count": 1,
}

# Initialize the model with error handling
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    model = genai.GenerativeModel(model_name, generation_config=genai_model_config)
    logger.info(f"Using model: {model_name}")
except Exception as e:
    logger.error(f"Failed to initialize model: {e}")
    model = None

# Enhanced session management with cleanup
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timestamps = {}
        self.lock = threading.Lock()
        
    def get_session(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                # Check if session has expired
                if time.time() - self.session_timestamps[session_id] > Config.SESSION_TIMEOUT:
                    self.cleanup_session(session_id)
                    return None
                return self.sessions[session_id]
            return None
    
    def create_session(self, session_id, history=None):
        with self.lock:
            if model is None:
                raise Exception("Model not initialized")
            
            chat_session = model.start_chat(history=history or [])
            self.sessions[session_id] = chat_session
            self.session_timestamps[session_id] = time.time()
            return chat_session
    
    def cleanup_session(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_timestamps:
                del self.session_timestamps[session_id]
    
    def cleanup_expired_sessions(self):
        with self.lock:
            current_time = time.time()
            expired_sessions = [
                sid for sid, timestamp in self.session_timestamps.items()
                if current_time - timestamp > Config.SESSION_TIMEOUT
            ]
            for sid in expired_sessions:
                self.cleanup_session(sid)
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

session_manager = SessionManager()

# Cache for responses
response_cache = {}
cache_lock = threading.Lock()

def get_cache_key(session_id, message):
    """Generate cache key for message"""
    return hashlib.md5(f"{session_id}:{message}".encode()).hexdigest()

def get_cached_response(cache_key):
    """Get cached response if available and not expired"""
    with cache_lock:
        if cache_key in response_cache:
            timestamp, response = response_cache[cache_key]
            if time.time() - timestamp < Config.CACHE_TIMEOUT:
                return response
            else:
                del response_cache[cache_key]
    return None

def cache_response(cache_key, response):
    """Cache response with timestamp"""
    with cache_lock:
        response_cache[cache_key] = (time.time(), response)

# Path for storing chat history
HISTORY_DIR = 'chat_history'
os.makedirs(HISTORY_DIR, exist_ok=True)

def cleanup_old_history_files(session_id):
    """Clean up old history files for a session"""
    try:
        session_files = [f for f in os.listdir(HISTORY_DIR) if f.startswith(f'chat_{session_id}_')]
        if len(session_files) > Config.MAX_HISTORY_FILES:
            # Sort by modification time and remove oldest
            session_files.sort(key=lambda x: os.path.getmtime(os.path.join(HISTORY_DIR, x)))
            files_to_remove = session_files[:-Config.MAX_HISTORY_FILES]
            for file in files_to_remove:
                os.remove(os.path.join(HISTORY_DIR, file))
            logger.info(f"Cleaned up {len(files_to_remove)} old history files for session {session_id}")
    except Exception as e:
        logger.error(f"Error cleaning up history files: {e}")

def save_chat_history(session_id, messages):
    """Save chat history with cleanup"""
    try:
        filename = f"{HISTORY_DIR}/chat_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(messages, f, indent=2)
        cleanup_old_history_files(session_id)
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")

def load_chat_history(session_id):
    """Load chat history with error handling"""
    history = []
    try:
        if os.path.exists(HISTORY_DIR):
            session_files = [f for f in os.listdir(HISTORY_DIR) if f.startswith(f'chat_{session_id}_')]
            session_files.sort(key=lambda x: os.path.getmtime(os.path.join(HISTORY_DIR, x)))
            
            for file in session_files[-10:]:  # Load only last 10 files
                try:
                    with open(os.path.join(HISTORY_DIR, file), 'r') as f:
                        history.extend(json.load(f))
                except Exception as e:
                    logger.error(f"Error loading history file {file}: {e}")
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
    return history

def validate_message(message):
    """Validate user message"""
    if not message or not isinstance(message, str):
        return False, "Message must be a non-empty string"
    
    if len(message) > Config.MAX_MESSAGE_LENGTH:
        return False, f"Message too long. Maximum {Config.MAX_MESSAGE_LENGTH} characters allowed"
    
    # Basic content filtering
    if any(word in message.lower() for word in ['script', 'javascript:', 'data:']):
        return False, "Message contains potentially harmful content"
    
    return True, None

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided',
                'response': 'Please provide a message.'
            }), 400

        session_id = request.headers.get('X-Session-ID', 'default')
        user_message = data['message']

        # Validate message
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            return jsonify({
                'error': 'Invalid message',
                'response': error_msg
            }), 400

        # Check cache first
        cache_key = get_cache_key(session_id, user_message)
        cached_response = get_cached_response(cache_key)
        if cached_response:
            logger.info(f"Cache hit for session {session_id}")
            return jsonify({
                'response': cached_response,
                'status': 'success',
                'cached': True
            })

        # Get or create chat session
        chat = session_manager.get_session(session_id)
        if not chat:
            history = load_chat_history(session_id)
            chat = session_manager.create_session(session_id, history)

        # Enhanced context for better responses
        context = (
            "You are a helpful AI assistant. Provide detailed, accurate responses. "
            "If a request is unclear, ask for clarification. For complex tasks, "
            "explain your approach step by step. Be concise but thorough."
        )

        try:
            # Send message with context
            response = chat.send_message(f"{context}\n\nUser: {user_message}")
            
            # Cache the response
            cache_response(cache_key, response.text)
            
            # Save the conversation
            conversation = {
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'bot_response': response.text,
                'session_id': session_id
            }
            save_chat_history(session_id, [conversation])

            return jsonify({
                'response': response.text,
                'status': 'success',
                'cached': False
            })

        except Exception as chat_error:
            logger.error(f"Chat Error for session {session_id}: {str(chat_error)}")
            # Reset session on error
            session_manager.cleanup_session(session_id)
            chat = session_manager.create_session(session_id)
            response = chat.send_message(user_message)
            
            return jsonify({
                'response': response.text,
                'status': 'success',
                'info': 'Chat session was reset due to an error'
            })

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({
            'error': 'An error occurred',
            'response': 'I apologize, but I encountered an issue. Could you please rephrase your question?',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('session_id', 'default')
    history = load_chat_history(session_id)
    return jsonify(history)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_available': model is not None,
        'active_sessions': len(session_manager.sessions),
        'cache_size': len(response_cache),
        'config': {
            'max_history_files': Config.MAX_HISTORY_FILES,
            'session_timeout': Config.SESSION_TIMEOUT,
            'cache_timeout': Config.CACHE_TIMEOUT,
            'max_message_length': Config.MAX_MESSAGE_LENGTH
        }
    })

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear response cache"""
    with cache_lock:
        response_cache.clear()
    return jsonify({'status': 'Cache cleared'})

# Background task for session cleanup
def cleanup_sessions_periodically():
    """Periodically cleanup expired sessions"""
    while True:
        time.sleep(300)  # Run every 5 minutes
        session_manager.cleanup_expired_sessions()

# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_sessions_periodically, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(debug=debug, host=host, port=port)
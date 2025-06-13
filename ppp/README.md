# 🤖 Optimized AI Chatbot

A high-performance, feature-rich chatbot built with Flask and Google's Gemini AI, featuring advanced caching, session management, and modern UI.

![Chatbot Demo](https://img.shields.io/badge/Status-Running-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-red) ![Gemini AI](https://img.shields.io/badge/Gemini%20AI-1.5%20Flash-orange)

## ✨ Key Features

### 🚀 Performance Optimizations
- **Response Caching**: Intelligent caching system with TTL for faster responses
- **Session Management**: Thread-safe session handling with automatic cleanup
- **Memory Optimization**: Automatic cleanup of expired sessions and old history files
- **Error Recovery**: Robust error handling with automatic retry mechanisms
- **Input Validation**: Comprehensive message validation and sanitization

### 🎨 User Experience
- **Modern UI**: Clean, ChatGPT-like interface with dark theme
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Enhanced transitions with reduced motion support
- **Real-time Feedback**: Typing indicators and loading states
- **Accessibility**: WCAG 2.1 AA compliant with keyboard navigation

### 🔒 Security & Reliability
- **Input Sanitization**: Protection against XSS and injection attacks
- **Environment Variables**: Secure configuration management
- **Content Filtering**: Basic content validation and filtering
- **Graceful Degradation**: Handles API failures gracefully

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Performance Features](#-performance-features)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini AI API key
- Git (for cloning)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp config.env.example .env
   # Edit .env with your Gemini API key
   ```

4. **Start the application**
   ```bash
   python start.py
   ```

5. **Access the chatbot**
   ```
   http://localhost:5000
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `config.env.example`:

```env
# Gemini AI API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0

# Performance Settings
MAX_HISTORY_FILES=100
SESSION_TIMEOUT=3600
CACHE_TIMEOUT=300
MAX_MESSAGE_LENGTH=4000
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Your Google Gemini AI API key |
| `PORT` | 5000 | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `MAX_HISTORY_FILES` | 100 | Max history files per session |
| `SESSION_TIMEOUT` | 3600 | Session timeout in seconds |
| `CACHE_TIMEOUT` | 300 | Cache timeout in seconds |
| `MAX_MESSAGE_LENGTH` | 4000 | Maximum message length |

## 🚀 Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Start chatting with the AI assistant
3. Use the sidebar to start new conversations
4. Your chat history is automatically saved

### API Endpoints

#### Send Message
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: your-session-id" \
  -d '{"message": "Hello, how are you?"}'
```

#### Get Chat History
```bash
curl http://localhost:5000/chat_history?session_id=your-session-id
```

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Clear Cache
```bash
curl -X POST http://localhost:5000/clear_cache
```

## 📊 API Reference

### POST /chat
Send a message to the AI assistant.

**Request:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "response": "AI response text",
  "status": "success",
  "cached": false
}
```

### GET /chat_history
Retrieve chat history for a session.

**Parameters:**
- `session_id` (optional): Session identifier

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00",
    "user_message": "User message",
    "bot_response": "AI response",
    "session_id": "session-id"
  }
]
```

### GET /health
Check application health and status.

**Response:**
```json
{
  "status": "healthy",
  "model_available": true,
  "active_sessions": 5,
  "cache_size": 10,
  "config": {
    "max_history_files": 100,}
}

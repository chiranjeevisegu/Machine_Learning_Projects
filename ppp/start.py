#!/usr/bin/env python3
"""
Optimized Chatbot Startup Script
Handles environment loading and graceful startup
"""

import os
import sys
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print("⚠️  No .env file found, using default configuration")
        print("💡 Copy config.env.example to .env and configure your API key")

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = ['flask', 'google.generativeai']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("⚠️  Gemini API key not configured")
        print("💡 Set GEMINI_API_KEY in your .env file")
        return False
    
    print("✅ API key configured")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Optimized Chatbot...")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        print("⚠️  Continuing with hardcoded API key (not recommended for production)")
    
    # Import and run app
    try:
        from app import app
        
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        
        print(f"🌐 Starting server on {host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("=" * 50)
        print("💡 Press Ctrl+C to stop the server")
        
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
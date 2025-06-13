#!/usr/bin/env python3
"""
Chatbot Deployment Script
Handles production deployment with Gunicorn
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

class ChatbotDeployer:
    def __init__(self):
        self.process = None
        self.port = int(os.getenv('PORT', 5000))
        self.host = os.getenv('HOST', '0.0.0.0')
        self.workers = int(os.getenv('WORKERS', 4))
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        required = ['flask', 'gunicorn', 'google.generativeai']
        missing = []
        
        for dep in required:
            try:
                __import__(dep.replace('-', '_'))
            except ImportError:
                missing.append(dep)
        
        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            print("💡 Run: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def check_config(self):
        """Check configuration files"""
        if not os.path.exists('.env'):
            print("⚠️  No .env file found")
            print("💡 Copy config.env.example to .env and configure your settings")
            return False
        
        print("✅ Configuration files found")
        return True
    
    def start_gunicorn(self):
        """Start the application with Gunicorn"""
        cmd = [
            'gunicorn',
            '--bind', f'{self.host}:{self.port}',
            '--workers', str(self.workers),
            '--timeout', '120',
            '--keep-alive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            'app:app'
        ]
        
        print(f"🚀 Starting Gunicorn on {self.host}:{self.port}")
        print(f"👥 Workers: {self.workers}")
        print("=" * 50)
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            print(f"✅ Process started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Gunicorn: {e}")
            return False
    
    def stop_gunicorn(self):
        """Stop the Gunicorn process"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=10)
                print("✅ Process stopped gracefully")
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                print("⚠️  Process force killed")
            except Exception as e:
                print(f"❌ Error stopping process: {e}")
    
    def deploy(self):
        """Main deployment function"""
        print("🚀 Deploying Optimized Chatbot...")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Check configuration
        if not self.check_config():
            return False
        
        # Start the application
        if not self.start_gunicorn():
            return False
        
        print("🎉 Deployment successful!")
        print(f"🌐 Access your chatbot at: http://{self.host}:{self.port}")
        print("💡 Press Ctrl+C to stop the server")
        
        try:
            # Keep the process running
            while self.process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            self.stop_gunicorn()
        
        return True

def main():
    deployer = ChatbotDeployer()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stop':
        # Stop existing process
        deployer.stop_gunicorn()
    else:
        # Deploy
        success = deployer.deploy()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 
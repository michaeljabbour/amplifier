#!/usr/bin/env python3
"""
Simplified Amplifier Backend with Virtual Terminal Support
Working implementation without async complications
"""

import os
import sys
import json
import uuid
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

# Add Amplifier to Python path
sys.path.insert(0, '/home/ubuntu/amplifier')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'amplifier-ui-secret'
CORS(app, origins=["http://localhost:5174", "http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5174", "http://localhost:3000"])

# Configuration
AMPLIFIER_PATH = "/home/ubuntu/amplifier"
SESSIONS_DIR = "/tmp/amplifier-sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Set up environment
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("Warning: ANTHROPIC_API_KEY not set")

# Global state for sessions
active_sessions = {}

class SimpleAmplifierSession:
    """Simplified Amplifier session with basic terminal support"""
    
    def __init__(self, session_id, name, project_path=None):
        self.session_id = session_id
        self.name = name
        self.project_path = project_path or AMPLIFIER_PATH
        self.session_dir = os.path.join(SESSIONS_DIR, session_id)
        self.created_at = datetime.now()
        self.status = "initializing"
        self.cost = 0.0
        self.messages = []
        self.agents = []
        self.terminal_process = None
        self.terminal_active = False
        
        # Create session directory
        os.makedirs(self.session_dir, exist_ok=True)
        
    def start(self):
        """Start the session with basic terminal"""
        try:
            # Start a simple bash process for the terminal
            self.terminal_process = subprocess.Popen(
                ['/bin/bash'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.session_dir,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.terminal_active = True
            self.status = "active"
            
            # Start terminal monitoring thread
            monitor_thread = threading.Thread(target=self._monitor_terminal)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Add initial message
            self.messages.append({
                "role": "system",
                "content": f"Amplifier session '{self.name}' started with terminal support",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            
            # Initialize the terminal with Amplifier environment
            self._init_terminal()
            
            return True
            
        except Exception as e:
            self.status = "error"
            self.messages.append({
                "role": "system", 
                "content": f"Failed to start session: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            return False
    
    def _init_terminal(self):
        """Initialize the terminal with Amplifier environment"""
        try:
            if self.terminal_process and self.terminal_process.stdin:
                # Change to amplifier directory
                self.terminal_process.stdin.write(f"cd {AMPLIFIER_PATH}\n")
                self.terminal_process.stdin.flush()
                
                # Set environment variables
                if api_key:
                    self.terminal_process.stdin.write(f"export ANTHROPIC_API_KEY={api_key}\n")
                    self.terminal_process.stdin.flush()
                
                # Show welcome message
                self.terminal_process.stdin.write("echo 'Amplifier Terminal Ready'\n")
                self.terminal_process.stdin.write("echo 'Type \"claude\" to start Claude Code CLI'\n")
                self.terminal_process.stdin.write("echo 'Type \"make help\" to see Amplifier commands'\n")
                self.terminal_process.stdin.flush()
                
        except Exception as e:
            print(f"Failed to initialize terminal: {e}")
    
    def _monitor_terminal(self):
        """Monitor terminal output and emit to WebSocket"""
        if not self.terminal_process:
            return
            
        try:
            while self.terminal_active and self.terminal_process.poll() is None:
                output = self.terminal_process.stdout.readline()
                if output:
                    socketio.emit('terminal_output', {
                        'session_id': self.session_id,
                        'output': output
                    }, room=f'session_{self.session_id}')
                time.sleep(0.1)
        except Exception as e:
            print(f"Terminal monitoring error: {e}")
    
    def send_message(self, message):
        """Send a message to the session (mock Claude response)"""
        try:
            # Add user message
            self.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            
            # Generate mock response
            response = self._generate_response(message)
            
            # Add assistant response
            self.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            
            # Update cost (simulated)
            self.cost += 0.05
            
            return response
            
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            self.messages.append({
                "role": "system",
                "content": error_msg,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            })
            return error_msg
    
    def _generate_response(self, message):
        """Generate a mock Claude response"""
        responses = [
            f"I understand you want to work on: '{message}'. I can help you with code generation, debugging, and development tasks using the Amplifier toolkit.",
            f"Great question about '{message}'. Let me analyze this and provide you with a comprehensive solution using the terminal and Amplifier commands.",
            f"I can help you with '{message}'. Would you like me to run some commands in the terminal or generate code for you?",
            f"Regarding '{message}', I can assist with implementation, testing, and documentation. I'll use the Amplifier environment to help you."
        ]
        import random
        return random.choice(responses)
    
    def execute_terminal_command(self, command):
        """Execute a command in the terminal"""
        try:
            if self.terminal_process and self.terminal_process.stdin:
                self.terminal_process.stdin.write(command + '\n')
                self.terminal_process.stdin.flush()
                return True
        except Exception as e:
            print(f"Failed to execute command: {e}")
        return False
    
    def get_session_info(self):
        """Get session information"""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "cost": self.cost,
            "message_count": len(self.messages),
            "agents": self.agents,
            "terminal_active": self.terminal_active,
            "project_path": self.project_path,
            "session_dir": self.session_dir
        }
    
    def stop(self):
        """Stop the session and clean up resources"""
        self.terminal_active = False
        
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self.terminal_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.terminal_process.kill()
            except:
                pass
        
        self.status = "stopped"

# REST API Endpoints

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "amplifier_available": True,
        "api_key_configured": bool(api_key),
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all active sessions"""
    sessions = []
    for session_id, session in active_sessions.items():
        sessions.append(session.get_session_info())
    
    return jsonify({
        "sessions": sessions,
        "count": len(sessions)
    })

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new Amplifier session"""
    try:
        data = request.get_json() or {}
        session_name = data.get('name', f'Session {len(active_sessions) + 1}')
        project_path = data.get('project_path')
        
        session_id = str(uuid.uuid4())
        session = SimpleAmplifierSession(session_id, session_name, project_path)
        
        # Start the session
        if session.start():
            active_sessions[session_id] = session
            return jsonify({
                "success": True,
                "session": session.get_session_info()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to start session"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific session"""
    if session_id not in active_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = active_sessions[session_id]
    return jsonify({
        "session": session.get_session_info(),
        "messages": session.messages[-50:]  # Last 50 messages
    })

@app.route('/api/sessions/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message to a session"""
    if session_id not in active_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        session = active_sessions[session_id]
        response = session.send_message(message)
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/sessions/<session_id>/terminal', methods=['POST'])
def execute_terminal_command(session_id):
    """Execute a command in the session's terminal"""
    if session_id not in active_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({"error": "Command is required"}), 400
        
        session = active_sessions[session_id]
        success = session.execute_terminal_command(command)
        
        return jsonify({
            "success": success,
            "message": "Command executed" if success else "Failed to execute command"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    if session_id not in active_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    try:
        session = active_sessions[session_id]
        session.stop()
        del active_sessions[session_id]
        
        return jsonify({
            "success": True,
            "message": "Session deleted"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# WebSocket Events for Real-time Terminal

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Amplifier backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join a session room for terminal updates"""
    session_id = data.get('session_id')
    if session_id and session_id in active_sessions:
        join_room(f'session_{session_id}')
        emit('joined_session', {'session_id': session_id})

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave a session room"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(f'session_{session_id}')
        emit('left_session', {'session_id': session_id})

@socketio.on('terminal_input')
def handle_terminal_input(data):
    """Handle terminal input from client"""
    session_id = data.get('session_id')
    input_data = data.get('input', '')
    
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session.execute_terminal_command(input_data.rstrip('\n'))

if __name__ == '__main__':
    print("Starting Simplified Amplifier Backend...")
    print(f"API key configured: {bool(api_key)}")
    print(f"Sessions directory: {SESSIONS_DIR}")
    
    # Run with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5002, debug=False, allow_unsafe_werkzeug=True)

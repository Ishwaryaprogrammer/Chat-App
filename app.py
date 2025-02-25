from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit
import os
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = '0000'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*")

users = []

@app.route('/')
def index():
    return render_template('index.html')

# Handle new connection
@socketio.on('connect')
def handle_connect():
    print('A user connected')

# Handle disconnection
@socketio.on('disconnect')
def handle_disconnect():
    print('A user disconnected')

# Handle new message
@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = data['username']
    print(f"Message from {username}: {msg}")
    send({'msg': msg, 'username': username}, broadcast=True)

# Handle new user joining
@socketio.on('join')
def handle_join(username):
    if username not in users:
        users.append(username)
    emit('update_users', users, broadcast=True)
    send({'msg': f"{username} has joined the chat", 'username': 'System'}, broadcast=True)

# Handle file upload
@socketio.on('file_upload')
def handle_file_upload(data):
    filename = data['name']
    file_data = data['data'].split(',')[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(file_data))
    
    emit('file_uploaded', {'name': filename, 'username': data['username']}, broadcast=True)

# Handle message reactions
@socketio.on('reaction')
def handle_reaction(data):
    emit('reaction', {'message': data['message'], 'username': data['username'], 'reaction': data['reaction']}, broadcast=True)

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


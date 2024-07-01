from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'messages.db')
db = SQLAlchemy(app)

# Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    channel = db.Column(db.String(80), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.json
    new_message = Message(user=data['user'], content=data['content'], channel=data['channel'])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({"message": "Message posted successfully"}), 201

@app.route('/messages/<channel>', methods=['GET'])
def get_messages(channel):
    messages = Message.query.filter_by(channel=channel).order_by(Message.timestamp.desc()).limit(50).all()
    return jsonify([
        {
            "id": message.id,
            "user": message.user,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "channel": message.channel
        } for message in messages
    ])

if __name__ == '__main__':
    app.run(debug=True)
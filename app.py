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
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.json
    new_message = Message(
        user=data['user'],
        content=data['content'],
        channel=data['channel'],
        parent_id=data.get('parent_id')
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({"message": "Message posted successfully", "id": new_message.id}), 201

@app.route('/messages/<channel>', methods=['GET'])
def get_messages(channel):
    messages = Message.query.filter_by(channel=channel, parent_id=None).order_by(Message.timestamp.desc()).limit(50).all()
    return jsonify([message_to_dict(message) for message in messages])

@app.route('/messages/<int:message_id>/replies', methods=['GET'])
def get_replies(message_id):
    replies = Message.query.filter_by(parent_id=message_id).order_by(Message.timestamp).all()
    return jsonify([message_to_dict(reply) for reply in replies])

def message_to_dict(message):
    return {
        "id": message.id,
        "user": message.user,
        "content": message.content,
        "timestamp": message.timestamp.isoformat(),
        "channel": message.channel,
        "has_replies": bool(message.replies),
        "parent_id": message.parent_id
    }

if __name__ == '__main__':
    app.run(debug=True)

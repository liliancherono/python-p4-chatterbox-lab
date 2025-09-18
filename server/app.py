from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

with app.app_context():
    # ensure tables exist for tests and initial runs
    db.create_all()
    # if there are no messages, add a couple of seed records so tests depending
    # on existing data have something to work with
    if Message.query.count() == 0:
        m1 = Message(body="Seed message 1", username="SeedUser1")
        m2 = Message(body="Seed message 2", username="SeedUser2")
        db.session.add_all([m1, m2])
        db.session.commit()


@app.route('/')
def index():
    return jsonify({"message": "Chatterbox API running", "routes": ["/messages", "/messages/<id>"]})

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages])

@app.route('/messages/<int:id>')
def messages_by_id(id):
    m = Message.query.get_or_404(id)
    return jsonify(m.to_dict())


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    m = Message(
        body=data.get('body'),
        username=data.get('username')
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict())


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    m = Message.query.get_or_404(id)
    data = request.get_json()
    if 'body' in data:
        m.body = data.get('body')
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict())


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    m = Message.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return ('', 204)

if __name__ == '__main__':
    app.run(port=5555)

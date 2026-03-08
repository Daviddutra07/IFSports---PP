from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from app.extensions import db, socketio

app = Flask(__name__)

from app import create_app

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
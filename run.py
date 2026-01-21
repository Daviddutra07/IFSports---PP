from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from app.extensions import db

app = Flask(__name__)

from app import create_app

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
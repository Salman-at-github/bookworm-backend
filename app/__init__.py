from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config

from flask_jwt_extended import JWTManager

from dotenv import load_dotenv

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for only React frontend
CORS(app, origins=["http://localhost:3000"])

#for jwt
jwt = JWTManager(app)

#load the env
load_dotenv()

db = SQLAlchemy(app)

from app import routes

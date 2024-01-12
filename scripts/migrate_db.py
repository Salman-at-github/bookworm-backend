import os
import sys
import json
from dotenv import load_dotenv

# Append the path to the root of your project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# need to load env here again because scripts generally don't get access to env
load_dotenv()
from app import app, db

def make_migration():
    app.app_context().push()
    db.create_all()


if __name__ == "__main__":
    make_migration()
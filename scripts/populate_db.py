# This script is used to populate the db using the data.json file

import os
import sys
# Append the path to the root of your project to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from dotenv import load_dotenv
load_dotenv()
from app import app, db
from app.models import BookModel




def load_data(file_path='scripts/data.json'):
    """
        Read the data from the json file
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def populate_database(data):
    """
        iterate over the json data and populate the DB
    """
    for book_data in data:
        book = BookModel(
            title=book_data['title'],
            author=book_data['author'],
            description=book_data['description'],
            genre=book_data['genre']
        )
        db.session.add(book)

    db.session.commit()
    print("DB populated successfully")

if __name__ == "__main__":
    with app.app_context():
        data = load_data()
        populate_database(data)

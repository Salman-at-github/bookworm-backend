from flask import jsonify, request
from app import app, db
from app.models import BookModel, UserModel
import bcrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import os

@app.route('/api/books', methods=['GET'])
def get_books():
    books = BookModel.query.all()
    book_list = [{'title': book.title, 'author': book.author, 'genre': book.genre} for book in books]
    return jsonify(book_list)


@app.route('/api/user/signup', methods=['POST'])
def user_signup():
    try:
        data = request.get_json()

        if 'name' not in data or 'email' not in data or 'phone' not in data or 'password' not in data:
            return jsonify({'message': 'Missing required fields'}), 400

        name = data['name']
        email = data['email']
        phone = data['phone']
        password = data['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = UserModel(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password.decode('utf-8')
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User signed up successfully', 'user': {'name': name, 'email': email, 'phone': phone}}), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message': 'Email already in use'}), 400


@app.route('/api/user/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()

        if 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Missing email or password'}), 400

        email = data['email']
        password = data['password']

        user = UserModel.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'message': 'Invalid password'}), 401

        access_token = create_access_token(identity=email)
        return jsonify({'token': access_token, "message" : "Logged in successfully!"}), 200

    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred','error':e}), 500


@app.route('/api/fields', methods=['GET'])
def get_fields():
    try:
        genres = db.session.query(BookModel.genre).distinct().all()
        authors = db.session.query(BookModel.author).distinct().all()

        unique_genres = [genre[0] for genre in genres]
        unique_authors = [author[0] for author in authors]

        return jsonify({'genres': unique_genres, 'authors': unique_authors}), 200

    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred','error':e}), 500

@app.route('/api/user/getpreferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    try:
        current_user_email = get_jwt_identity()
        user = UserModel.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        user_preferences = {
            'preferredAuthors': [],
            'preferredGenres': [],
        }

        if user.preferred_authors:
            user_preferences['preferredAuthors'] = user.preferred_authors.split(',')

        if user.preferred_genres:
            user_preferences['preferredGenres'] = user.preferred_genres.split(',')

        return jsonify(user_preferences), 200

    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred', 'error': e}), 500

@app.route('/api/user/preferences', methods=['POST'])
@jwt_required()
def save_user_preferences():
    try:
        current_user_email = get_jwt_identity()
        user = UserModel.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        data = request.get_json()

        if 'preferred_authors' not in data or 'preferred_genres' not in data:
            return jsonify({'message': 'Missing preferred_authors or preferred_genres in request'}), 400

        user.preferred_authors = data['preferred_authors']
        user.preferred_genres = data['preferred_genres']

        db.session.commit()

        user_dict = {
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'preferred_authors': user.preferred_authors,
            'preferred_genres': user.preferred_genres
        }

        return jsonify({'message': 'User preferences saved successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred', 'error':e}), 500


@app.route('/api/books/preferences', methods=['GET'])
@jwt_required()
def get_books_for_user_preferences():
    try:
        current_user_email = get_jwt_identity()
        user = UserModel.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        preferred_authors = user.preferred_authors.split(',')
        preferred_genres = user.preferred_genres.split(',')

        books = BookModel.query.filter(
            (BookModel.author.in_(preferred_authors)) | (BookModel.genre.in_(preferred_genres))
        ).all()

        book_list = [{'title': book.title, 'author': book.author, 'genre': book.genre} for book in books]
        return jsonify(book_list), 200

    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred','error':e}), 500

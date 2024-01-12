from flask import jsonify, request
from app import app, db
from app.models import BookModel, UserModel
import bcrypt #for hashing the password
from sqlalchemy.exc import IntegrityError #for preventing duplicate users
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity #for jwt


@app.route('/api/books', methods=['GET'])
def get_books():
    books = BookModel.query.all()
    book_list = [{'title': book.title, 'author': book.author, 'genre': book.genre} for book in books]
    return jsonify(book_list)


@app.route('/api/user/signup', methods=['POST'])
def user_signup():
    # Retrieve data from the JSON request
    data = request.get_json()

    # Check if all required fields are present
    if 'name' not in data or 'email' not in data or 'phone' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract user information
    name = data['name']
    email = data['email']
    phone = data['phone']
    password = data['password']

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        # Create a new user instance
        new_user = UserModel(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password.decode('utf-8')  # Store the hashed password
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Return a success response
        return jsonify({'message': 'User signed up successfully', 'user': {'name': name, 'email': email, 'phone': phone}}), 201

    except IntegrityError as e:
        # Handle the case where the email already exists
        db.session.rollback()
        return jsonify({'error': 'Email already in use'}), 400


@app.route('/api/user/login', methods=['POST'])
def user_login():
    # Retrieve data from the JSON request
    data = request.get_json()

    # Check if all required fields are present
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400

    # Extract user information
    email = data['email']
    password = data['password']

    # Find the user by email in the database
    user = UserModel.query.filter_by(email=email).first()

    # Check if the user exists
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Verify the password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401

    # Generate JWT token
    access_token = create_access_token(identity=email)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/fields', methods=['GET'])
def get_fields():
    # Fetch unique genres and authors from the books in the database
    genres = db.session.query(BookModel.genre).distinct().all()
    authors = db.session.query(BookModel.author).distinct().all()
    
    # Convert the results to lists
    unique_genres = [genre[0] for genre in genres]
    unique_authors = [author[0] for author in authors]

    return jsonify({'genres': unique_genres, 'authors': unique_authors}), 200


@app.route('/api/user/preferences', methods=['POST'])
@jwt_required()
def save_user_preferences():
    current_user_email = get_jwt_identity()
    user = UserModel.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Check if 'preferred_authors' and 'preferred_genres' are present in the request
    if 'preferred_authors' not in data or 'preferred_genres' not in data:
        return jsonify({'error': 'Missing preferred_authors or preferred_genres in request'}), 400

    # Update user preferences
    user.preferred_authors = data['preferred_authors']
    user.preferred_genres = data['preferred_genres']

    db.session.commit()

    # Create a dictionary representation of the user for JSON serialization
    user_dict = {
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'preferred_authors': user.preferred_authors,
        'preferred_genres': user.preferred_genres
    }

    return jsonify({'message': 'User preferences saved successfully', 'user': user_dict}), 200


@app.route('/api/books/preferences', methods=['GET'])
@jwt_required()
def get_books_for_user_preferences():
    current_user_email = get_jwt_identity()

    # Find the user by email in the database
    user = UserModel.query.filter_by(email=current_user_email).first()

    # Check if the user exists
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Fetch books based on preferred authors and genres
    preferred_authors = user.preferred_authors.split(',')
    preferred_genres = user.preferred_genres.split(',')

    # Query books matching either preferred authors or genres
    books = BookModel.query.filter(
        (BookModel.author.in_(preferred_authors)) | (BookModel.genre.in_(preferred_genres))
    ).all()

    book_list = [{'title': book.title, 'author': book.author, 'genre': book.genre} for book in books]
    return jsonify(book_list), 200
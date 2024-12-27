import jwt
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ## means from __init__.py import db
from flask_login import login_required, logout_user, current_user
from .auth_utils import verify_token, SECRET_KEY

SECRET_KEY = 'SECRET_KEY'

auth = Blueprint('auth', __name__)


def create_token(user):
    expiration = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        'sub': str(user.id),
        'exp': expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    # Сохраняем токен в базу
    session = Session(
        user_id=user.id,
        session_token=token,
        created_at=datetime.utcnow(),
        expires_at=expiration
    )
    db.session.add(session)
    db.session.commit()
    
    return token

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        print(email)
        print(password)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')

                # Создание JWT токена
                token = create_token(user)

                # Отправка токена в заголовке ответа
                response = jsonify({'message': 'Logged in successfully!'})
                response.headers['Authorization'] = f'Bearer {token}'  # Добавляем токен в заголовок
                return response

            else:
                #flash('Incorrect password, try again.', category='error')
                return jsonify({'message': 'incorrect password!'})
        else:
            #flash('Email does not exist.', category='error')
            return jsonify({'message': 'email does not exist!'})

    return jsonify({'message': 'Logged in unsuccessfully!'})
    #return render_template("login.html", user=current_user)


@auth.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 401

    token = token.split(' ')[1] 
    
    session = Session.query.filter_by(session_token=token).first()
    if not session:
        return jsonify({'error': 'Token is not active or does not exist'}), 401

    db.session.delete(session)
    db.session.commit()
    return jsonify({'message': 'Successfully logged out'}), 200

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        print(email)

        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({'message': 'Email already exists!'}), 400
            flash('Email already exists.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(
                password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')

            token = create_token(new_user)

            response = jsonify({'message': 'Account created and logged in successfully!'})
            response.headers['Authorization'] = f'Bearer {token}'
            return response

    return render_template("sign_up.html", user=current_user)

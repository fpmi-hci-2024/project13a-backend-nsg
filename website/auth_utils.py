import jwt
from flask import request, jsonify
from . import db
from .models import Session
from datetime import datetime

SECRET_KEY = 'SECRET_KEY'

def verify_token():
    token = request.headers.get('Authorization')
    
    print(token)
    
    if token:
        token = token.split(' ')[1]     

        session = Session.query.filter_by(session_token=token).first()
        if not session:
            return jsonify({'error': 'Token is not active or does not exist'}), 401
        
        if session.expires_at < datetime.utcnow():
            db.session.delete(session) 
            db.session.commit()
            return jsonify({'error': 'Token has expired'}), 401

        return session.user_id 
    else:
        return jsonify({'error': 'Token is missing'}), 401
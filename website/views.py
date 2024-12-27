from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
import json
from .auth_utils import verify_token

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    
    user_id = verify_token()

    if isinstance(user_id, tuple):
        return user_id
    
    return jsonify({'message': f'Hello, user {user_id}!'})

    #return render_template("home.html", user=current_user)

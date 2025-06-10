import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

def check_token_valid (token):
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    data = jwt.decode(token, algorithms='HS256', subject='admin', key='JWT_SECRET')
    exp = data['exp']
    current_timestamp = datetime.now().timestamp()
    if exp is None or exp < current_timestamp:
        return jsonify({'error': 'Token is expired'}), 401
    return None

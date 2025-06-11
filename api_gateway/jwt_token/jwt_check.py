import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta

def check_token_valid(token):
    if not token:
        return False
    data = jwt.decode(token, algorithms='HS256', subject='admin', key='JWT_SECRET')
    exp = data['exp']
    current_timestamp = datetime.now().timestamp()
    if exp is None or exp < current_timestamp:
        False
    return True

import jwt
from datetime import datetime, timedelta

def is_token_valid (token: str) -> bool:
    data = jwt.decode(token, algorithms='HS256', subject='admin', key='JWT_SECRET')
    exp = data['exp']
    current_timestamp = datetime.now().timestamp()
    if exp is None or exp < current_timestamp:
        return False
    return True

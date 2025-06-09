from jwt import JWT, exceptions
import datetime

JWT_EXP_DELTA_SECONDS = 3600  # Время жизни токена в секундах (1 час)


def generate_jwt(username):
    jwt = JWT()
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload=payload)
    return token


def verify_jwt(token):
    jwt = JWT()
    try:
        payload = jwt.decode(token)
        return payload['username']
    except exceptions.JWTException:
        return None

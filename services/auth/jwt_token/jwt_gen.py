import jwt
from datetime import datetime, timedelta

JWT_EXP_DELTA_SECONDS = 3600  # Время жизни токена в секундах (1 час)


def generate_jwt(username):
    current_timestamp = datetime.now()
    data = dict(
        sub=username,
        iat=current_timestamp.__str__(),
        nbf=current_timestamp.__str__(),
        exp=(current_timestamp+timedelta(seconds=JWT_EXP_DELTA_SECONDS)).strftime("%Y-%m-%d %H:%M:%S.%f")
    )

    return jwt.encode(payload=data, key='JWT_SECRET', algorithm='HS256')


def verify_jwt(token):
    pass

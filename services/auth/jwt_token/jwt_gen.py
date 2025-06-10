from typing import Any

import jwt
from datetime import datetime, timedelta

JWT_EXP_DELTA_SECONDS = 3600  # Время жизни токена в секундах (1 час)


def generate_jwt(username: str, user_id: int) -> str:
    current_timestamp = datetime.now()
    data = dict(
        sub='admin',
        username=username,
        user_id=user_id,
        iat=current_timestamp.timestamp(),
        nbf=current_timestamp.timestamp(),
        exp=(current_timestamp+timedelta(seconds=JWT_EXP_DELTA_SECONDS)).timestamp()
    )

    return jwt.encode(payload=data, key='JWT_SECRET', algorithm='HS256')


def decode_jwt(token, ) -> dict[str: Any]:
    return jwt.decode(token, algorithms='HS256', subject='admin', key='JWT_SECRET' )


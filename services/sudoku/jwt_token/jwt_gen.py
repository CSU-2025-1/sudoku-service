from typing import Any

import jwt


def decode_jwt(token) -> dict[str: Any]:
    return jwt.decode(token, algorithms='HS256', subject='admin', key='JWT_SECRET')


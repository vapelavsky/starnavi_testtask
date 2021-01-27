import jwt

from starnavi_testtask import settings


def get_user_id_from_jwt(t):
    token = str.replace(str(t), 'Bearer ', '')
    payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
    return payload['user_id']

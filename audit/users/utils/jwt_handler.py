import jwt
from django.conf import settings
from datetime import datetime, timedelta

def generate_token(user):
    payload = {
        'user_id': user.id,
        'eth_address': user.eth_address,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
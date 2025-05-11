from .models import User
from .utils.jwt_handler import decode_token

def jwt_user(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return {'user': None}

    payload = decode_token(token)
    if not payload:
        return {'user': None}

    try:
        user = User.objects.get(id=payload['user_id'])
        return {'user': user}
    except User.DoesNotExist:
        return {'user': None}

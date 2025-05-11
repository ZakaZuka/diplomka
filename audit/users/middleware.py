import jwt
from django.conf import settings
from users.models import User
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            request.user = None
            return

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            request.user = None

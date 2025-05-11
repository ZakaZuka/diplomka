from django.http import JsonResponse
from django.shortcuts import render
from .models import User
from .utils.web3_auth import verify_signature
from .utils.jwt_handler import generate_token,  decode_token
from django.http import HttpResponseForbidden
import random, string, json
from django.views.decorators.csrf import csrf_exempt

def get_nonce(request):
    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': 'No address'}, status=400)
    user, _ = User.objects.get_or_create(eth_address=address.lower())
    user.nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    user.save()
    return JsonResponse({'nonce': user.nonce})

@csrf_exempt
def verify_login(request):
    data = json.loads(request.body)
    address = data.get('address')
    signature = data.get('signature')

    try:
        user = User.objects.get(eth_address=address.lower())
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)

    if verify_signature(address, signature, user.nonce):
        token = generate_token(user)
        response = JsonResponse({'success': True})
        response.set_cookie(
            key='jwt',
            value=token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60 * 60 * 24
        )
        return response

    return JsonResponse({'error': 'Invalid signature'}, status=400)

def profile_view(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return HttpResponseForbidden("Not authenticated")

    payload = decode_token(token)
    if not payload:
        return HttpResponseForbidden("Invalid token")

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return HttpResponseForbidden("User not found")

    return render(request, '/users/profile.html', {'user': user})

def index(request):
    return render(request, 'index.html')

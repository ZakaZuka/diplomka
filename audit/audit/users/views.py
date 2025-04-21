import json
import secrets
import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .utils import generate_nonce, verify_signature
from .models import User

logger = logging.getLogger(__name__)

@csrf_exempt  # Временно отключаем CSRF для тестов
def get_nonce(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    
    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': 'Address required'}, status=400)
    
    try:
        # 1. Ищем или создаём пользователя
        user, created = User.objects.get_or_create(
            eth_address=address.lower(),
            defaults={
                'username': address,
                'nonce': secrets.token_hex(16)  # Генерация случайного nonce
            }
        )
        
        # 2. Обновляем nonce для существующих пользователей
        if not created:
            user.nonce = secrets.token_hex(16)
            user.save()
        
        logger.info(f"Generated nonce for {address}: {user.nonce}")
        return JsonResponse({'nonce': user.nonce})
    
    except Exception as e:
        logger.error(f"Error in get_nonce: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
@require_POST
def metamask_login_view(request):
    try:
        data = json.loads(request.body)
        address = data.get('address')
        signature = data.get('signature')

        user = User.objects.get(eth_address=address)
        if verify_signature(address, signature, user.nonce):
            user.nonce = generate_nonce()
            user.save()
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return HttpResponseForbidden('Invalid signature')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'logged out'})

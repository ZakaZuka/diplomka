import os
import tempfile
from django.conf import settings
from django.shortcuts import render
from .forms import ContractUploadForm
from .logic.analyzer import ERC20AuditTool
def upload_contract(request):
    result = None
    if request.method == "POST":
        form = ContractUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('contract_file')
            code = form.cleaned_data.get('contract_code')
            if file:
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)
                with open(file_path, 'wb+') as dest:
                    for chunk in file.chunks():
                        dest.write(chunk)
            elif code:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".sol", dir=settings.MEDIA_ROOT, mode='w', encoding='utf-8') as tmp:
                    tmp.write(code)
                    file_path = tmp.name
            else:
                form.add_error(None, "Вы должны загрузить файл или вставить код")
                return render(request, 'contracts/upload.html', {'form': form})
            auditor = ERC20AuditTool(file_path, openai_api_key='AIzaSyA1Y8Ii4Hsfl71q4bfQq5IshxTYHjkxiZA')
            result = auditor.analyze()
    else:
        form = ContractUploadForm()
    return render(request, 'contracts/upload.html', {
        'form': form,
        'analysis_results': result
        #'log': result.get('log')  # <-- добавь это
    })


def extract_warnings(self, ai_text):
    """Извлекает предупреждения из AI анализа"""
    warnings = []
    if "Recommendation:" in ai_text:
        warnings = ai_text.split("Recommendation:")[1].strip().split('\n')
    return warnings
def index(request):
    return render(request, 'index.html')


# import tempfile
# import os
# from django.shortcuts import render
# from .forms import ContractForm
# from .utils import analyze_contract  # Подключи свою функцию анализа
# from pathlib import Path

# def contract_analysis_view(request):
#     analysis_results = {}

#     if request.method == 'POST':
#         form = ContractForm(request.POST, request.FILES)
#         if form.is_valid():
#             contract_file = form.cleaned_data.get('contract_file')
#             contract_code = form.cleaned_data.get('contract_code')

#             # Сохраняем во временный .sol-файл
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".sol", mode='w+', encoding='utf-8') as tmp:
#                 if contract_file:
#                     tmp.write(contract_file.read().decode('utf-8'))
#                 else:
#                     tmp.write(contract_code)
#                 tmp_path = tmp.name

#             try:
#                 issues, _ = analyze_contract(tmp_path)
#                 analysis_results['issues'] = issues
#             except Exception as e:
#                 analysis_results['errors'] = str(e)
#             finally:
#                 os.remove(tmp_path)
#     else:
#         form = ContractForm()

#     return render(request, 'contracts/analysis.html', {
#         'form': form,
#         'analysis_results': analysis_results
#     })

# def index(request):
#     return render(request, 'contracts/index.html')

# from django.shortcuts import render
# from django.http import JsonResponse
# from .forms import ContractForm
# from .utils import ContractAnalyzer
# import tempfile
# import os
# import logging

# logger = logging.getLogger(__name__)

# def contract_analysis_view(request):
#     """Обработчик для анализа контракта"""
#     analyzer = ContractAnalyzer()
#     results = {'success': False}
    
#     if request.method == 'POST':
#         form = ContractForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             try:
#                 # Создаем временный файл для анализа
#                 with tempfile.NamedTemporaryFile(mode='w+', suffix='.sol', delete=False) as tmp_file:
#                     if form.cleaned_data.get('contract_file'):
#                         # Обрабатываем загруженный файл
#                         for chunk in form.cleaned_data['contract_file'].chunks():
#                             tmp_file.write(chunk.decode('utf-8'))
#                     else:
#                         # Обрабатываем введенный код
#                         tmp_file.write(form.cleaned_data['contract_code'])
                    
#                     tmp_file_path = tmp_file.name
                
#                 # Анализируем контракт
#                 issues, _ = analyzer.analyze(
#                     source=tmp_file_path,
#                     is_file=True
#                 )
                
#                 results.update({
#                     'success': True,
#                     'issues': issues
#                 })
                
#             except Exception as e:
#                 logger.error(f"Ошибка анализа: {str(e)}")
#                 results['error'] = str(e)
#             finally:
#                 # Удаляем временный файл
#                 if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
#                     try:
#                         os.remove(tmp_file_path)
#                     except Exception as e:
#                         logger.error(f"Не удалось удалить временный файл: {str(e)}")
            
#             return JsonResponse(results)
    
#     # GET запрос или невалидная форма
#     return render(request, 'contracts/analysis.html', {'form': ContractForm()})

# def index(request):
#     return render(request, 'contracts/index.html')

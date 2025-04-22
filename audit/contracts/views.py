# import os
# import tempfile
# from django.conf import settings
# from django.shortcuts import render
# from .forms import ContractUploadForm
# from .logic.analyzer import ERC20AuditTool

# def upload_contract(request):
#     result = None
#     if request.method == "POST":
#         form = ContractUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES.get('contract_file')
#             code = form.cleaned_data.get('contract_code')

#             if file:
#                 file_path = os.path.join(settings.MEDIA_ROOT, file.name)
#                 with open(file_path, 'wb+') as dest:
#                     for chunk in file.chunks():
#                         dest.write(chunk)
#             elif code:
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".sol", dir=settings.MEDIA_ROOT, mode='w', encoding='utf-8') as tmp:
#                     tmp.write(code)
#                     file_path = tmp.name
#             else:
#                 form.add_error(None, "Вы должны загрузить файл или вставить код")
#                 return render(request, 'contracts/upload.html', {'form': form})

#             auditor = ERC20AuditTool(file_path, openai_api_key='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')
#             result = auditor.analyze()

#     else:
#         form = ContractUploadForm()

#     return render(request, 'contracts/upload.html', {'form': form, 'result': result})

# def extract_warnings(self, ai_text):
#     """Извлекает предупреждения из AI анализа"""
#     warnings = []
#     if "Recommendation:" in ai_text:
#         warnings = ai_text.split("Recommendation:")[1].strip().split('\n')
#     return warnings

# def index(request):
#     return render(request, 'index.html')


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


import tempfile
import os
import logging
from django.shortcuts import render
from django.conf import settings
from .forms import ContractForm
from .utils import analyze_contract
from pathlib import Path

logger = logging.getLogger(__name__)

def contract_analysis_view(request):
    analysis_results = {}
    form = ContractForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        contract_file = form.cleaned_data.get('contract_file')
        contract_code = form.cleaned_data.get('contract_code')

        # Создаем временную директорию, если не существует
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_contracts')
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Создаем временный файл с уникальным именем
            with tempfile.NamedTemporaryFile(
                mode='w+',
                suffix='.sol',
                encoding='utf-8',
                dir=temp_dir,
                delete=False  # Удалим вручную после анализа
            ) as tmp:
                tmp_path = tmp.name
                
                if contract_file:
                    # Обрабатываем загруженный файл
                    try:
                        content = contract_file.read().decode('utf-8')
                        tmp.write(content)
                    except UnicodeDecodeError:
                        # Пробуем другие кодировки, если utf-8 не работает
                        contract_file.seek(0)
                        content = contract_file.read().decode('latin-1')
                        tmp.write(content)
                else:
                    # Используем код из текстового поля
                    tmp.write(contract_code)

            try:
                # Анализируем контракт
                issues, report_path = analyze_contract(tmp_path)
                analysis_results['issues'] = issues
                
                # Сохраняем отчет, если нужно
                if report_path and os.path.exists(report_path):
                    analysis_results['report_path'] = report_path
                    
            except Exception as e:
                logger.error(f"Ошибка анализа контракта: {str(e)}", exc_info=True)
                analysis_results['error'] = f"Ошибка анализа: {str(e)}"
                
        except IOError as e:
            logger.error(f"Ошибка работы с файлом: {str(e)}", exc_info=True)
            analysis_results['error'] = "Ошибка обработки файла контракта"
            
        finally:
            # Удаляем временный файл контракта
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Не удалось удалить временный файл {tmp_path}: {str(e)}")

    return render(request, 'contracts/analysis.html', {
        'form': form,
        'analysis_results': analysis_results
    })

def index(request):
    return render(request, 'contracts/index.html')
import os
import tempfile
from django.conf import settings
from django.shortcuts import render
from .forms import ContractUploadForm
from .logic.analyzer import ERC20AuditTool
from decouple import config

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
            api_key = config("GENAI_API_KEY")
            auditor = ERC20AuditTool(file_path, openai_api_key=api_key)
            result = auditor.analyze()
    else:
        form = ContractUploadForm()
    return render(request, 'contracts/upload.html', {
        'form': form,
        'analysis_results': result
    })


def extract_warnings(self, ai_text):
    """Извлекает предупреждения из AI анализа"""
    warnings = []
    if "Recommendation:" in ai_text:
        warnings = ai_text.split("Recommendation:")[1].strip().split('\n')
    return warnings
def index(request):
    return render(request, 'index.html')

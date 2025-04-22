# contracts/utils.py
import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import openai
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ContractAnalyzer:
    def __init__(self):
        self._init_openai()
        self._check_dependencies()

    def _init_openai(self):
        """Инициализация OpenAI"""
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if not openai.api_key:
            logger.warning("OpenAI API ключ не настроен, переводы будут на английском")

    def _check_dependencies(self):
        """Проверка зависимостей"""
        try:
            subprocess.run(["slither", "--version"], check=True, capture_output=True)
            subprocess.run(["solc", "--version"], capture_output=True)
        except Exception as e:
            logger.error(f"Ошибка проверки зависимостей: {e}")
            raise RuntimeError("Не установлены необходимые инструменты (slither/solc)")

    def _translate_text(self, text: str, context: str = "") -> str:
        """Перевод текста через OpenAI с кэшированием"""
        if not text.strip() or not openai.api_key:
            return text

        cache_key = f"trans_{hash(text)}"
        if cached := cache.get(cache_key):
            return cached

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "system",
                    "content": "Ты переводчик технических текстов. Переводи точно, сохраняя термины."
                }, {
                    "role": "user", 
                    "content": f"Контекст: {context}\nПереведи на русский:\n{text[:2000]}"
                }],
                temperature=0.1
            )
            translated = response.choices[0].message.content.strip()
            cache.set(cache_key, translated, 86400)  # Кэш на 1 день
            return translated
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            return text

    def analyze(self, source: str, is_file: bool = True) -> Tuple[List[Dict], Optional[str]]:
        """
        Анализирует контракт из файла или текста
        
        Args:
            source: Путь к файлу или текст контракта
            is_file: Флаг, указывающий тип source
            
        Returns:
            Кортеж (результаты анализа, путь к отчету)
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.sol', delete=False) as tmp:
                if is_file:
                    with open(source, 'r') as f:
                        tmp.write(f.read())
                else:
                    tmp.write(source)
                tmp_path = tmp.name

            # Запуск Slither
            report_path = f"{tmp_path}.json"
            cmd = [
                "slither", tmp_path,
                "--json", report_path,
                "--disable-color",
                "--fail-none"
            ]
            
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
                shell=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"Slither error: {error_msg}")
                raise RuntimeError(self._translate_text(error_msg, "ошибка анализа"))

            # Обработка результатов
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            issues = []
            for det in data.get('detectors', []):
                check = det.get('check', '')
                desc = det.get('description', '')
                
                issues.append({
                    'check': self._translate_text(check, "тип уязвимости"),
                    'impact': self._translate_text(det.get('impact', ''), "уровень опасности"),
                    'description': self._translate_text(desc, check),
                    'elements': [self._translate_text(el.get('name', '')) 
                                for el in det.get('elements', [])],
                    'confidence': det.get('confidence', ''),
                    'original': desc  # Оригинал для отладки
                })

            return issues, report_path

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
        finally:
            # Очистка временных файлов
            for path in [tmp_path, report_path]:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

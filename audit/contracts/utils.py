# contracts/utils.py
import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def analyze_contract(contract_path: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Анализирует смарт-контракт с помощью Slither
    
    Args:
        contract_path: Путь к файлу контракта (.sol)
    
    Returns:
        Tuple: (список уязвимостей, путь к отчету или None)
    """
    try:
        # Нормализация пути для Windows
        contract_path = str(Path(contract_path).absolute().resolve())
        
        # Создаем временный файл для отчета
        report_dir = tempfile.mkdtemp()
        report_path = os.path.join(report_dir, "slither_report.json")
        
        # Запуск Slither
        cmd = [
            "slither",
            contract_path,
            "--json", report_path,
            "--disable-color",
            "--fail-none"
        ]
        
        logger.info(f"Запуск Slither: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            shell=True  # Важно для Windows
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            logger.error(f"Ошибка Slither: {error_msg}")
            raise RuntimeError(f"Ошибка анализа: {error_msg}")
        
        # Чтение отчета
        if not os.path.exists(report_path):
            logger.warning("Отчет Slither не создан")
            return [], None
            
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Форматирование результатов
        issues = []
        for detector in report.get('detectors', []):
            issues.append({
                'check': detector.get('check', ''),
                'impact': detector.get('impact', ''),
                'description': detector.get('description', ''),
                'elements': [e.get('name', '') for e in detector.get('elements', [])],
                'location': detector.get('source_mapping', '')
            })
            
        return issues, report_path
        
    except Exception as e:
        logger.error(f"Ошибка при анализе контракта: {str(e)}")
        raise
    finally:
        # Очистка временных файлов
        try:
            if 'report_dir' in locals() and os.path.exists(report_dir):
                for f in os.listdir(report_dir):
                    os.remove(os.path.join(report_dir, f))
                os.rmdir(report_dir)
        except Exception as e:
            logger
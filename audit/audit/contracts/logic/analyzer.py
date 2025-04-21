import subprocess
import json
from pathlib import Path
import openai
from slither import Slither
import shutil

CHECK_TRANSLATIONS = {
    'reentrancy-eth': 'Уязвимость повторного входа (ETH‑перевод)',
    'reentrancy-no-eth': 'Уязвимость повторного входа (без ETH‑перевода)',
    'unchecked-transfer': 'Непроверенный перевод',
    'incorrect-equality': 'Опасное строгое сравнение',
    'weak-prng': 'Слабый генератор случайных чисел',
    'timestamp': 'Зависимость от времени',
    'suicidal': 'Саморазрушение контракта',
    'delegatecall-loop': 'Опасный delegatecall',
    'uninitialized-state': 'Неинициализированное состояние',
}

IMPACT_TRANSLATIONS = {
    'high': 'критический',
    'medium': 'средний',
    'low': 'низкий',
    'informational': 'информационный'
}

class ERC20AuditTool:
    def __init__(self, contract_path, openai_api_key):
        self.contract_path = Path(contract_path)
        #self.slither = Slither(str(self.contract_path))
        openai.api_key = openai_api_key

    def translate_with_gpt(self, text):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Переводи технический текст с английского на русский, как профессиональный переводчик."},
                    {"role": "user", "content": f"Переведи на русский:\n\n{text}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Ошибка перевода через GPT: {e}")
            return text

    def analyze_with_ai(self, code_snippet):
        prompt = f"""
        Проанализируй следующий код смарт-контракта Solidity и найди потенциальные уязвимости или проблемы:

        {code_snippet}

        Если найдешь уязвимости, объясни их и предложи исправления.
        """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — эксперт по безопасности смарт-контрактов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()

    def run_slither_json(self):
        json_path = self.contract_path.with_suffix('.slither.json')

        # Удаляем старый файл, если есть
        if json_path.exists():
            json_path.unlink()

        # Проверим, что slither доступен
        if not shutil.which("slither"):
            print("❌ Slither не установлен или не найден в PATH")
            return None

        # Выполним анализ через subprocess
        proc = subprocess.run(
            ['slither', str(self.contract_path), '--json', str(json_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if proc.returncode != 0:
            print("⚠️ Slither завершился с ошибкой")
            error_output = proc.stderr.strip() or proc.stdout.strip()
            print(self.translate_with_gpt(error_output))
            return None

        # Проверим, что JSON действительно создан
        if not json_path.exists():
            print("❌ Slither не сгенерировал JSON. Пропускаем парсинг уязвимостей.")
            return None

        return json_path

    def parse_slither_issues(self, json_path):
        try:
            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Не найден отчёт: {json_path}")
            return []

        issues = []
        for det in data.get('detectors', []):
            issues.append({
                'check': CHECK_TRANSLATIONS.get(det.get('check', '').lower(), det.get('check')),
                'impact': IMPACT_TRANSLATIONS.get(det.get('impact', '').lower(), det.get('impact')),
                'description': det.get('description', '').strip(),
                'elements': [e.get('name') for e in det.get('elements', [])],
                'location': det.get('source_mapping', '').strip(),
            })

        
    
        return issues

    def save_simple_report(self, issues, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)
        print(f"💾 Отчёт сохранён: {path}")

    def analyze(self):
        print(f"🔍 Анализируем: {self.contract_path.name}")

        # AI-анализ
        code = self.contract_path.read_text(encoding='utf-8')
        ai_analysis = self.analyze_with_ai(code)

        json_path = self.run_slither_json()
        issues = []
        if json_path:
            issues = self.parse_slither_issues(json_path)
            self.save_simple_report(issues, self.contract_path.with_name('simple_report.json'))
        else:
            print("❌ Slither не сгенерировал JSON. Пропускаем парсинг уязвимостей.")

        if not issues:
            print("✅ Уязвимостей не найдено Slither'ом.")
            return {
                'ai_analysis': ai_analysis,
                'slither_issues': [],
                'json_path': str(json_path) if json_path else "—"
            }

        return {
            'ai_analysis': ai_analysis,
            'slither_issues': issues,
            'json_path': str(json_path)
        }
    
if __name__ == "__main__":
    tool = ERC20AuditTool("contracts/MyERC20.sol", openai_api_key="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")
    result = tool.analyze()

    print("\n=== 📋 AI-анализ ===")
    print(result['ai_analysis'])

    print("\n=== 🛡️ Найденные уязвимости ===")
    for issue in result['slither_issues']:
        print(f"⚠️ {issue['check']} ({issue['impact']}) — {issue['description']}")
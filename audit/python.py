import subprocess
import json
import sys
from pathlib import Path
from deep_translator import GoogleTranslator
import openai

# Настройка OpenAI
openai.api_key = "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"  # Замени на свой ключ

# Словари перевода
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

def translate_with_gpt(text):
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

def analyze_contract(contract_path):
    contract = Path(contract_path)
    if not contract.exists():
        print(f"❌ Файл не найден: {contract_path}")
        sys.exit(1)

    report_json = contract.with_suffix('.slither.json')

    proc = subprocess.run(
        ['slither', str(contract), '--json', str(report_json)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode != 0:
        print("⚠️ Slither завершился с кодом", proc.returncode)
        output = proc.stderr.strip() or proc.stdout.strip()
        translated_output = translate_with_gpt(output)
        print(translated_output)
        print("ℹ️ Продолжаю разбор JSON‑отчёта…")

    try:
        with open(report_json, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Не найден отчёт {report_json}")
        sys.exit(1)

    if 'detectors' not in data:
        print("❌ Ключ 'detectors' не найден в JSON.")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(1)

    issues = []
    for det in data.get('detectors', []):
        issues.append({
            'check': det.get('check', '').strip(),
            'impact': det.get('impact', '').strip(),
            'description': det.get('description', '').strip(),
            'elements': [e.get('name') for e in det.get('elements', [])],
            'location': det.get('source_mapping', '').strip(),
        })
    return issues, report_json

def print_report(issues, report_json):
    print(f"\n📄 Полный отчёт Slither: {report_json}")
    if not issues:
        print("✅ Уязвимости не обнаружены!")
        return

    print(f"\n🔎 Найдено {len(issues)} потенциальных уязвимостей:\n" + "="*60)
    for i in issues:
        raw_check = i['check']
        rus_check = CHECK_TRANSLATIONS.get(raw_check.lower(), raw_check)
        rus_impact = IMPACT_TRANSLATIONS.get(i['impact'].lower(), i['impact'])

        print(f"⚠️ {rus_check} — уровень риска: {rus_impact}")
        print(f"Описание: {i['description']}")
        if i['elements']:
            print(f"Затрагиваемые элементы: {', '.join(i['elements'])}")
        print(f"Местоположение: {i['location']}")
        print("-" * 60)

def save_simple_json(issues, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Упрощённый JSON‑отчёт сохранён: {out_path}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        contract_path = 'soll.sol'
        print("ℹ️  Анализирую по умолчанию 'soll.sol'")
    else:
        contract_path = sys.argv[1]

    issues, full_report = analyze_contract(contract_path)
    print_report(issues, full_report)
    save_simple_json(issues, Path(contract_path).with_name('simple_report.json'))

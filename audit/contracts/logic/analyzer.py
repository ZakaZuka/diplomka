import shutil
import subprocess
from pathlib import Path
import openai
import google.generativeai as genai
from numpy.random import standard_t


class ERC20AuditTool:
    def __init__(self, contract_path, openai_api_key):
        self.contract_path = Path(contract_path)
        #self.slither = Slither(str(self.contract_path))
        genai.configure(api_key=openai_api_key)

    def run_slither_json(self):
        if not shutil.which("slither"):
            return "❌ Slither не установлен или не найден в PATH"

        proc = subprocess.run(
            ['slither', str(self.contract_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return proc.stderr.strip() or proc.stdout.strip()

    def check_erc20_standard(self):
        code = self.contract_path.read_text(encoding='utf-8')
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
                Проверь смарт-контракт на соответствие стандарту ERC20
                и просто напиши что соответствует, а что нет, без вывода, просто список
                {code}
                """
        response = model.generate_content(prompt)
        return response.text

    def analyze_with_ai(self):
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Дан отчет  slither-analyzer, просто переведи на русский
        с сохранением технического английского, убери строки где есть
        C:USERS И solc --version
        формат:
        функция/параметр(строка): уязвимость
        пример: ссылка на гит:
        {self.run_slither_json()}
        """
        response = model.generate_content(prompt)
        return response.text

    def analyze(self):
        print(f"🔍 Анализируем: {self.contract_path.name}")
        standard_check = self.check_erc20_standard()
        ai_analysis = self.analyze_with_ai()

        # Формируем текст для вывода
        result_text = f"""
            === Проверка на соответствие стандарту ERC20 ===
            {standard_check}
            === 📄 Результат анализа с помощью Slither и AI===
            {ai_analysis}
            """
        return result_text.strip()
    
if __name__ == "__main__":
    tool = ERC20AuditTool("soll.sol", 
                          openai_api_key="")
    result = tool.analyze()

    print("\n=== 📋 AI-анализ ===")
    print(result['ai_analysis'])

    print("\n=== 🛡️ Найденные уязвимости ===")
    for issue in result['slither_issues']:
        print(f"⚠️ {issue['check']} ({issue['impact']}) — {issue['description']}")

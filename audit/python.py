import shutil
import subprocess
from pathlib import Path
import openai


class ERC20AuditTool:
    def __init__(self, contract_path, openai_api_key):
        self.contract_path = Path(contract_path)
        # self.slither = Slither(str(self.contract_path))
    def analyze_with_ai(self):


       # model = genai.GenerativeModel("gemini-pro")
        #prompt = f"""
        #Проанализируй следующий отчет slither-analyzer, переведи на русский и дай советы как исправить:
        #{code_snippet}
        #"""
        #response = model.generate_content(prompt)
        return self.run_slither_json()

    def run_slither_json(self):
        if not shutil.which("slither"):
            return "❌ Slither не установлен или не найден в PATH"

        proc = subprocess.run(
            ['slither', str(self.contract_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    def analyze(self):
        print(f"🔍 Анализируем: {self.contract_path.name}")

        # Запуск slithe`r
        slither_output = self.run_slither_json()

        # AI-анализ
        ai_analysis = self.analyze_with_ai()

        # Формируем текст для вывода
        result_text = f"""
            === 📄 Результат анализа с помощью Slither и AI===
            {ai_analysis}
            """
        return result_text.strip()


if __name__ == "__main__":
    tool = ERC20AuditTool("soll.sol",
                          openai_api_key="AIzaSyA1Y8Ii4Hsfl71q4bfQq5IshxTYHjkxiZA")
    result = tool.analyze()

    print(result)
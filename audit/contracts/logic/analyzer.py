import shutil
import subprocess
from pathlib import Path
from jinja2 import Template
import google.generativeai as genai
from decouple import config


class ERC20AuditTool:
    def __init__(self, contract_path, openai_api_key):
        self.contract_path = Path(contract_path)
        genai.configure(api_key=openai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _render_settings(self, template_name: str, **kwargs) -> str:
        template_path = Path(__file__).parent / "set_tasks" / template_name
        template_text = template_path.read_text(encoding='utf-8')
        template = Template(template_text)
        return template.render(**kwargs)

    def run_slither_json(self):
        if not shutil.which("slither"):
            return "Slither не установлен или не найден в PATH"

        proc = subprocess.run(
            ['slither', str(self.contract_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc.stderr.strip() or proc.stdout.strip()

    def check_erc20_standard(self):
        code = self.contract_path.read_text(encoding='utf-8')
        set_task = self._render_settings("erc20_check.txt", code=code)
        response = self.model.generate_content(set_task)
        return response.text

    def analyze_with_ai(self):
        slither_output = self.run_slither_json()
        set_task = self._render_settings("slither_translate.txt", report=slither_output)
        response = self.model.generate_content(set_task)
        return response.text

    def analyze(self):
        print(f"Анализируем: {self.contract_path.name}")
        standard_check = self.check_erc20_standard()
        ai_analysis = self.analyze_with_ai()

        result_text = f"""
        === Проверка на соответствие стандарту ERC20 ===
        {standard_check}

        === Результат анализа с помощью Slither и AI ===
        {ai_analysis}
        """
        return result_text.strip()


if __name__ == "__main__":
    from decouple import config
    api_key = config("GENAI_API_KEY")
    tool = ERC20AuditTool("soll.sol", openai_api_key=api_key)
    result = tool.analyze()
    print("\n=== AI-анализ ===")
    print(result)

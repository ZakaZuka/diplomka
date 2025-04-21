
import openai
from slither import Slither

class ERC20AuditTool:
    def __init__(self, contract_path, openai_api_key):
        self.contract_path = contract_path
        self.slither = Slither(contract_path)
        self.client = openai.OpenAI(api_key=openai_api_key)

    def analyze_with_ai(self, code_snippet):
        """
        Анализирует код с использованием OpenAI GPT.
        """
        prompt = f"""
        Проанализируй следующий код смарт-контракта Solidity и найди потенциальные уязвимости или проблемы:

        {code_snippet}

        Если найдешь уязвимости, объясни их и предложи исправления.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — эксперт по безопасности смарт-контрактов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5
        )

        return response.choices[0].message.content

    def analyze(self):
        """
        Запускает полный анализ контракта.
        """
        print(f"Анализ контракта: {self.contract_path}")
        with open(self.contract_path, "r") as file:
            code = file.read()

        # Статический анализ с помощью Slither
        slither_report = []
        for contract in self.slither.contracts:
            slither_report.append(f"Контракт: {contract.name}")
            for function in contract.functions:
                slither_report.append(f"  Функция: {function.name}")

        # AI-анализ
        ai_analysis = self.analyze_with_ai(code)

        return "\n".join(slither_report) + "\n\nАнализ ИИ:\n" + ai_analysis
